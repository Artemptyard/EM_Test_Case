from rest_framework import serializers
from .models import Order, OrderItem, Item, OrderStatuses


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'dish']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'dish', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()  # Nesting Item details inside OrderItem

    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)  # Russian status    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)  # Nested items
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Read-only

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'items', 'total_price']
