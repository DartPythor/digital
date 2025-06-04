from django.urls import path

from warehouse.views import WarehouseView

app_name = "warehouse"

urlpatterns = [
    path("", WarehouseView.as_view(), name="index"),
]
