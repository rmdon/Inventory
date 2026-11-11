from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sales-orders/", views.sales_orders, name="sales_orders"),
    path("imports/", views.import_data, name="import_data"),
]


