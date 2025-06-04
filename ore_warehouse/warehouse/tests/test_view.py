from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from warehouse.models import DumpTruck, TruckModel, Warehouse
from warehouse.views import WarehouseView


class WarehouseViewTests(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(
            name="Основной склад",
            area_wkt="POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))",
            initial_weight=1000,
            initial_si=0.5,
            initial_fe=0.3,
        )

        model1 = TruckModel.objects.create(
            name="CAT-777",
            max_capacity=100,
        )
        model2 = TruckModel.objects.create(
            name="Komatsu-930",
            max_capacity=150,
        )

        self.truck1 = DumpTruck.objects.create(
            board_number="AA-001",
            model=model1,
            current_weight=90,
            si_percent=0.6,
            fe_percent=0.25,
        )

        self.truck2 = DumpTruck.objects.create(
            board_number="BB-002",
            model=model2,
            current_weight=140,
            si_percent=0.4,
            fe_percent=0.35,
        )

        self.client = Client()
        self.url = reverse("warehouse:index")

    def test_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "warehouse/index.html")

        context = response.context
        self.assertEqual(context["warehouse"], self.warehouse)

        self.assertEqual(context["total_after"], 1000)
        self.assertEqual(context["quality_after"], "0.5% SiO2, 0.3% Fe")

    @patch("warehouse.views.is_point_in_polygon")
    def test_post_request_valid_coordinates(self, mock_in_polygon):
        mock_in_polygon.side_effect = [True, False]

        data = {
            f"unload_{self.truck1.id}": "5 5",
            f"unload_{self.truck2.id}": "15 15",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.truck1.refresh_from_db()
        self.truck2.refresh_from_db()
        self.assertEqual(self.truck1.unload_x, 5.0)
        self.assertEqual(self.truck1.unload_y, 5.0)
        self.assertEqual(self.truck2.unload_x, 15.0)
        self.assertEqual(self.truck2.unload_y, 15.0)

        response = self.client.get(response.url)
        context = response.context

        self.assertEqual(len(context["accepted_trucks"]), 1)
        self.assertEqual(context["accepted_trucks"][0], self.truck1)
        self.assertEqual(context["total_after"], 1090)

        self.assertIn("SiO2", context["quality_after"])
        self.assertIn("Fe", context["quality_after"])

    def test_post_request_invalid_coordinates(self):
        data = {
            f"unload_{self.truck1.id}": "invalid data",
            f"unload_{self.truck2.id}": "10 5",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.truck1.refresh_from_db()
        self.truck2.refresh_from_db()
        self.assertIsNone(self.truck1.unload_x)
        self.assertIsNone(self.truck1.unload_y)
        self.assertEqual(self.truck2.unload_x, 10.0)
        self.assertEqual(self.truck2.unload_y, 5.0)

    def test_no_warehouse(self):
        Warehouse.objects.all().delete()
        response = self.client.get(self.url)

        context = response.context
        self.assertIsNone(context["warehouse"])
        self.assertEqual(context["total_after"], 0)
        self.assertEqual(context["quality_after"], "0% SiO2, 0% Fe")

    @patch("warehouse.views.is_point_in_polygon")
    def test_get_accepted_trucks_method(self, mock_in_polygon):
        mock_in_polygon.side_effect = [True, False]

        self.truck1.unload_x = 5
        self.truck1.unload_y = 5
        self.truck1.save()

        self.truck2.unload_x = 15
        self.truck2.unload_y = 15
        self.truck2.save()

        model = TruckModel.objects.create(
            name="BELAZ-7555",
            max_capacity=200,
        )
        DumpTruck.objects.create(
            board_number="CC-003",
            model=model,
            current_weight=180,
            si_percent=0.55,
            fe_percent=0.28,
        )

        trucks = DumpTruck.objects.all()
        accepted = WarehouseView.get_accepted_trucks(
            trucks,
            self.warehouse.area_wkt,
        )

        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0], self.truck1)

        self.assertEqual(mock_in_polygon.call_count, 2)
        mock_in_polygon.assert_any_call(
            5.0,
            5.0,
            self.warehouse.area_wkt,
        )
        mock_in_polygon.assert_any_call(
            15.0,
            15.0,
            self.warehouse.area_wkt,
        )

    def test_calculate_quality_method(self):
        accepted_trucks = [self.truck1, self.truck2]

        result = WarehouseView.calculate_quality(
            self.warehouse,
            accepted_trucks,
        )

        total_weight = 1000 + 90 + 140
        self.assertEqual(result["total_after"], total_weight)

        self.assertIn("SiO2", result["quality_after"])
        self.assertIn("Fe", result["quality_after"])
        self.assertIn("%", result["quality_after"])

        result_empty = WarehouseView.calculate_quality(
            self.warehouse,
            [],
        )
        self.assertEqual(result_empty["total_after"], 1000)
        self.assertEqual(
            result_empty["quality_after"],
            "0.5% SiO2, 0.3% Fe",
        )

    @patch("warehouse.views.is_point_in_polygon")
    def test_edge_cases(self, mock_in_polygon):
        mock_in_polygon.side_effect = [True, True]

        self.truck1.unload_x = 10
        self.truck1.unload_y = 5
        self.truck1.save()

        self.truck2.unload_x = 0
        self.truck2.unload_y = 0
        self.truck2.save()

        trucks = DumpTruck.objects.all()
        accepted = WarehouseView.get_accepted_trucks(
            trucks,
            self.warehouse.area_wkt,
        )
        self.assertEqual(len(accepted), 2)

        self.warehouse.initial_weight = 0
        self.warehouse.save()

        result = WarehouseView.calculate_quality(self.warehouse, accepted)
        self.assertEqual(
            result["total_after"],
            230,
        )

        self.assertNotEqual(
            result["quality_after"],
            "0% SiO2, 0% Fe",
        )


__all__ = ()
