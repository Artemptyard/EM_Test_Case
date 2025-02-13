from django.db import models


class OrderStatuses(models.TextChoices):
    """Статусы заказа"""
    WAITING = 'waiting', 'в ожидании'
    READY = 'ready', 'готов'
    PAID = 'paid', 'оплачено'


class Item(models.Model):
    """Таблица блюд"""
    id = models.AutoField(primary_key=True)
    dish = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.dish


class Order(models.Model):
    """Таблица заказов"""
    id = models.AutoField(primary_key=True)
    table_number = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=10,
        choices=OrderStatuses.choices,
        default=OrderStatuses.WAITING
    )
    items = models.ManyToManyField(Item, through='OrderItem')

    def __str__(self):
        return f"Заказ {self.id} (Стол {self.table_number}) - {self.get_status_display()}"


class OrderItem(models.Model):
    """Таблица для связи таблицы блюд и заказов"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.dish} (Заказ {self.order.id})"
