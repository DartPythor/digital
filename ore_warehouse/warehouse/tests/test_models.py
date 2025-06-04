from django.test import TestCase
from warehouse.models import TruckModel, DumpTruck, Warehouse
from warehouse.until import is_point_in_polygon


class TruckModelTest(TestCase):
    def test_create_truck_model(self):
        model = TruckModel.objects.create(name="TestTruck", max_capacity=150)
        self.assertEqual(str(model), "TestTruck")
        self.assertEqual(model.max_capacity, 150)

    def test_truck_model_exists_in_db(self):
        TruckModel.objects.create(name="ExistTruck", max_capacity=100)
        exists = TruckModel.objects.filter(name="ExistTruck").exists()
        self.assertTrue(exists)


class DumpTruckTest(TestCase):
    def setUp(self):
        self.model = TruckModel.objects.create(name="БЕЛАЗ", max_capacity=120)

    def test_create_dump_truck_and_overload(self):
        truck = DumpTruck.objects.create(
            board_number="T123",
            model=self.model,
            current_weight=130,
            si_percent=0.30,
            fe_percent=0.65,
        )
        self.assertEqual(str(truck), "T123")
        self.assertAlmostEqual(truck.overload_percent(), 8.33, places=2)

    def test_dump_truck_exists_in_db(self):
        DumpTruck.objects.create(
            board_number="T125",
            model=self.model,
            current_weight=110,
            si_percent=0.31,
            fe_percent=0.64,
        )
        self.assertTrue(DumpTruck.objects.filter(board_number="T125").exists())


class WarehouseTest(TestCase):
    def setUp(self):
        self.wkt = "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
        self.warehouse = Warehouse.objects.create(
            name="Main Storage",
            initial_weight=900,
            initial_si=0.34,
            initial_fe=0.65,
            area_wkt=self.wkt,
        )

    def test_create_warehouse(self):
        self.assertEqual(str(self.warehouse), "Main Storage")
        self.assertEqual(self.warehouse.initial_weight, 900)
        self.assertEqual(self.warehouse.area_wkt, self.wkt)

    def test_warehouse_exists_in_db(self):
        exists = Warehouse.objects.filter(name="Main Storage").exists()
        self.assertTrue(exists)

    def test_point_inside_polygon(self):
        self.assertTrue(
            is_point_in_polygon(31, 25, self.warehouse.area_wkt),
        )

    def test_point_outside_polygon(self):
        self.assertFalse(
            is_point_in_polygon(50, 50, self.warehouse.area_wkt),
        )

    def test_point_on_boundary(self):
        self.assertTrue(
            is_point_in_polygon(30, 10, self.warehouse.area_wkt),
        )
