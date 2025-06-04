from django.shortcuts import redirect
from django.views.generic import TemplateView

from warehouse.models import DumpTruck, Warehouse
from warehouse.until import is_point_in_polygon


class WarehouseView(TemplateView):
    template_name = "warehouse/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        trucks = DumpTruck.objects.select_related("model").all()
        warehouse = Warehouse.objects.first()

        if warehouse:
            accepted_trucks = self.get_accepted_trucks(
                trucks,
                warehouse.area_wkt,
            )
            quality_info = self.calculate_quality(warehouse, accepted_trucks)
        else:
            accepted_trucks = []
            quality_info = {
                "total_after": 0,
                "quality_after": "0% SiO2, 0% Fe",
            }

        context.update(
            {
                "trucks": trucks,
                "warehouse": warehouse,
                "accepted_trucks": accepted_trucks,
                **quality_info,
            },
        )
        return context

    def post(self, request, *args, **kwargs):
        trucks = DumpTruck.objects.select_related("model").all()

        for truck in trucks:
            coord_str = request.POST.get(f"unload_{truck.id}", "").strip()
            try:
                x, y = map(float, coord_str.split())
                truck.unload_x = x
                truck.unload_y = y
            except (ValueError, TypeError):
                truck.unload_x = None
                truck.unload_y = None
            truck.save()

        return redirect("warehouse:index")

    @staticmethod
    def get_accepted_trucks(trucks, polygon):
        accepted = []
        for truck in trucks:
            if truck.unload_x is not None and truck.unload_y is not None:
                in_area = is_point_in_polygon(
                    truck.unload_x,
                    truck.unload_y,
                    polygon,
                )
                if in_area:
                    accepted.append(truck)
        return accepted

    @staticmethod
    def calculate_quality(warehouse, accepted_trucks):
        w0 = warehouse.initial_weight
        si0 = warehouse.initial_si
        fe0 = warehouse.initial_fe

        total_si = w0 * si0
        total_fe = w0 * fe0
        w1 = w0

        for truck in accepted_trucks:
            total_si += truck.current_weight * truck.si_percent
            total_fe += truck.current_weight * truck.fe_percent
            w1 += truck.current_weight

        if w1 > 0:
            si_final = round(total_si / w1, 2)
            fe_final = round(total_fe / w1, 2)
        else:
            si_final = fe_final = 0.0

        return {
            "total_after": w1,
            "quality_after": f"{si_final}% SiO2, {fe_final}% Fe",
        }


__all__ = ()
