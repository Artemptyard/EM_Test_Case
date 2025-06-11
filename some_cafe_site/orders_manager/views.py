from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from orders_manager.models import Order, Item, OrderItem
from orders_manager.forms import AddOrderForm, FilterOrdersForm, DeleteOrderForm
from orders_manager.serizlizers import DishSerializer
from rest_framework.utils import json
from typing import Dict, Any


def _add_order(request: WSGIRequest) -> AddOrderForm:
    """Обработка формы добавления заказа"""
    data = AddOrderForm.process_data(request.POST)
    form = AddOrderForm(data)
    if form.is_valid():
        form.save_order(data["items"])
        # form = AddOrderForm()
        return redirect("/orders/")
    return form


def _filter_orders(request: WSGIRequest) -> FilterOrdersForm:
    """Фильтрация заказов"""
    filter_form = FilterOrdersForm(request.POST)
    if filter_form.is_valid():
        pass
    return filter_form


def _delete_orders(request: WSGIRequest) -> DeleteOrderForm:
    """Удаление заказа"""
    delete_form = DeleteOrderForm(request.POST)
    if delete_form.is_valid():
        order_id = delete_form.cleaned_data["order_id"]
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.success(request, f"Order {order_id} has been deleted.")
        # delete_form = DeleteOrderForm()
        return redirect("/orders/")
    return delete_form


def orders_page(request: WSGIRequest) -> HttpResponse:
    """Страница заказов в кафе"""
    orders = Order.objects.all().order_by("table_number").prefetch_related("items")
    if request.method == "POST":
        # data = AddOrderForm.process_data(request.POST)
        print(request.POST)
        # print(data)
        # form = _add_order(request) if "add_order_form" in request.POST else AddOrderForm()
        # if "add_order_form" in request.POST:
        #     data = AddOrderForm.process_data(request.POST)
        #     form = AddOrderForm(data)
        #     if form.is_valid():
        #         form.save_order(data["items"])
        #         # form = AddOrderForm()
        #         return redirect("/orders/")
        # else:
        form = AddOrderForm()
        # filter_form = _filter_orders(request) if "order_filter_form" in request.POST else FilterOrders()
        # if "order_filter_form" in request.POST:
        #     print(request.POST)
        if "delete_order_form" in request.POST:
            delete_form = DeleteOrderForm(request.POST)
            if delete_form.is_valid():
                order_id = delete_form.cleaned_data["order_id"]
                order = get_object_or_404(Order, id=order_id)
                order.delete()
                messages.success(request, f"Заказ {order_id} успешно удалён.")
                # delete_form = DeleteOrderForm()
                return redirect("/orders/")
        # delete_form = _delete_orders(request) if "delete_order_form" in request.POST else DeleteOrderForm()
    else:
        delete_form = DeleteOrderForm()
        form = AddOrderForm()
    filter_form = FilterOrdersForm()
    delete_form = DeleteOrderForm()
    if request.method == "GET":
        filter_form = FilterOrdersForm(request.GET or None)
        if filter_form.is_valid():
            table_number = filter_form.cleaned_data.get("table_number")
            status = filter_form.cleaned_data.get("status")

            if table_number:
                orders = orders.filter(table_number=table_number)
            if status:
                orders = orders.filter(status=status)
    ser_items = DishSerializer(form.fields['items'].queryset, many=True).data
    data = {
        "orders": orders,
        "form": form,
        "filter_form": filter_form,
        "delete_form": delete_form,
        "items_json": json.dumps(ser_items, ensure_ascii=False)
    }
    return render(request, "orders/orders.html", data)


class AddOrder(CreateView):
    """"""
    model = Order
    form_class = AddOrderForm
    template_name = "orders/orders.html"
    # success_url =

    def form_valid(self, form):
        """"""
        data = AddOrderForm.process_data(self.request.POST)
        print(data)
        form = AddOrderForm(data)
        if form.is_valid():
            # form.save_order(data["items"])
            pass
        return super().form_valid(form)


def edit_order(request: WSGIRequest, order_id: int) -> HttpResponse:
    """Страница заказов в кафе"""
    order = Order.objects.filter(id=order_id).prefetch_related("items").first()
    order_items = OrderItem.objects.filter(order_id=order_id).select_related("item")
    items = Item.objects.all()

    item_quantities = {oi.item.id: oi.quantity for oi in order_items}

    form = AddOrderForm(order)
    data = {
        "edit_form": form,
        "counter": item_quantities
    }
    return redirect("/orders#edit_form")

