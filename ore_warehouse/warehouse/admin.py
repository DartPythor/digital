from django.contrib import admin

from warehouse.models import DumpTruck, TruckModel, Warehouse


class DumpTruckInline(admin.TabularInline):
    model = DumpTruck
    extra = 0
    fields = (
        "board_number",
        "current_weight",
        "overload_percent_display",
        "unload_coords",
    )
    readonly_fields = ("overload_percent_display", "unload_coords")

    def overload_percent_display(self, obj):
        return f"{obj.overload_percent()}%"

    overload_percent_display.short_description = "Перегруз"

    def unload_coords(self, obj):
        if obj.unload_x is not None and obj.unload_y is not None:
            return f"{obj.unload_x}, {obj.unload_y}"
        return "-"

    unload_coords.short_description = "Координаты разгрузки"


@admin.register(TruckModel)
class TruckModelAdmin(admin.ModelAdmin):
    list_display = ("name", "max_capacity", "dump_trucks_count")
    search_fields = ("name",)
    inlines = [DumpTruckInline]

    def dump_trucks_count(self, obj):
        return obj.dumptruck_set.count()

    dump_trucks_count.short_description = "Кол-во самосвалов"


@admin.register(DumpTruck)
class DumpTruckAdmin(admin.ModelAdmin):
    list_display = (
        "board_number",
        "model_name",
        "max_capacity",
        "current_weight",
        "overload_percent_display",
        "unload_coords",
        "quality_info",
    )
    list_filter = ("model",)
    search_fields = ("board_number",)
    fieldsets = (
        (None, {"fields": ("board_number", "model")}),
        ("Груз", {"fields": ("current_weight", "si_percent", "fe_percent")}),
        (
            "Координаты разгрузки",
            {"fields": ("unload_x", "unload_y"), "classes": ("collapse",)},
        ),
    )

    def model_name(self, obj):
        return obj.model.name

    model_name.short_description = "Модель"
    model_name.admin_order_field = "model__name"

    def max_capacity(self, obj):
        return obj.model.max_capacity

    max_capacity.short_description = "Макс. грузоподъемность (т)"

    def overload_percent_display(self, obj):
        return f"{obj.overload_percent()}%"

    overload_percent_display.short_description = "Перегруз"

    def unload_coords(self, obj):
        if obj.unload_x is not None and obj.unload_y is not None:
            return f"{obj.unload_x}, {obj.unload_y}"
        return "-"

    unload_coords.short_description = "Координаты разгрузки"

    def quality_info(self, obj):
        return f"SiO₂: {obj.si_percent}%, Fe: {obj.fe_percent}%"

    quality_info.short_description = "Характеристики руды"


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "initial_weight",
        "initial_si_display",
        "initial_fe_display",
    )
    fields = ("name", "initial_weight", "initial_si", "initial_fe", "area_wkt")

    def initial_si_display(self, obj):
        return f"{obj.initial_si * 100}%"

    initial_si_display.short_description = "% SiO₂"

    def initial_fe_display(self, obj):
        return f"{obj.initial_fe * 100}%"

    initial_fe_display.short_description = "% Fe"


__all__ = ()
