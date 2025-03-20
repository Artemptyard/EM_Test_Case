from django.contrib import admin
from django.urls import path, include
from orders_manager import views

urlpatterns = [
    path("select2/", include('django_select2.urls')),
    path("", views.orders_page),
    path("edit/<int:order_id>/", views.edit_order, name="delete_order"),
    path("#add_order", views.AddOrder.as_view())
]
