from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = "restaurant"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("reserver/", views.client_reservation, name="client_reservation"),
    path("pos/", views.pos_view, name="pos"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("produits/", views.products, name="products"),
    path("produits/crud/", views.product_crud, name="product_crud"),
    path("commandes/", views.orders, name="orders"),
    path("stock/", views.inventory, name="inventory"),
    path("stock/crud/", views.inventory_crud, name="inventory_crud"),
    path("rh/", views.employees, name="employees"),
    path("rh/crud/", views.employee_crud, name="employee_crud"),
    path("rh/paie/", views.payroll, name="payroll"),
    path("finances/", views.finance, name="finance"),
    path("operations/", views.operations, name="operations"),
    path("operations/crud/", views.operations_crud, name="operations_crud"),
    path("cuisine/", views.kitchen_view, name="kitchen"),
    path("cuisine/update-status/", views.update_order_status, name="update_order_status"),
    path("profil/", views.profile_view, name="profile"),
]
