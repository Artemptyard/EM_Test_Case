from typing import List, Dict, Any

from django import forms
from django.db.models import QuerySet
from django.http import QueryDict

from .models import Item, OrderStatuses, Order, OrderItem
from django_select2.forms import ModelSelect2MultipleWidget

from django_select2.forms import ModelSelect2MultipleWidget
from django.utils.safestring import mark_safe
from django import forms


class MyModelSelect2MultipleWidget(ModelSelect2MultipleWidget):
    """
    Custom Select2 multiple widget that allows choosing the same item multiple times
    and includes a quantity input for each selection.
    """

    def __init__(self, *args, **kwargs):
        self.quantity_name = kwargs.pop('quantity_name', 'quantity')
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        rendered = super().render(name, value, attrs, renderer)
        quantity_html = """
        <script>
        (function($) {
            $(document).ready(function() {
                let selectField = $('#id_%(name)s');
                selectField.on('select2:select', function(e) {
                    let selectedOption = e.params.data.id;
                    let quantityInput = $('<input>')
                        .attr('type', 'number')
                        .attr('name', '%(quantity_name)s[' + selectedOption + ']')
                        .attr('min', '1')
                        .attr('value', '1')
                        .addClass('quantity-input');

                    selectField.next('.select2-container').after(quantityInput);
                });
            });
        })
        </script>
        """ % {'name': name, 'quantity_name': self.quantity_name}

        return mark_safe(rendered + quantity_html)


class AddOrderForm(forms.Form):
    """Создание html формы добавления заказа"""

    table_number = forms.IntegerField(
        label="Номер стола",
        max_value=24, min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "1"})
    )
    items = forms.ModelMultipleChoiceField(
        label="Меню",
        queryset=Item.objects.all(),
        widget=MyModelSelect2MultipleWidget(
            model=Item,
            search_fields=["dish__icontains"],  # Поиск по имени
            attrs={
                # Начало поиска с первой буквы
                "data-minimum-input-length": 0,
                "data-placeholder": "Выберите блюдо"
            }
        ),
        error_messages={"required": "Пожалуйста закажите хотя бы одно блюдо."})
    status = forms.ChoiceField(
        choices=OrderStatuses.choices,
        label="Статус заказа",
        initial=OrderStatuses.WAITING,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = OrderItem
        fields = ['item']

    # def __init__(self, items: QuerySet(), *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['items'].queryset = items

    @classmethod
    def post_init(cls, data: QueryDict):
        pass

    def save_order(self, items: List[int]):
        """Сохранение данных, полученных из формы в базу данных

        :param items: Список всех блюд в заказе.
        """
        # Я реализовал свой метод сохранения (вместо ModalForm),
        # так как я не нашёл готового виджета, который смог бы расширить функционал ModelSelect2MultipleWidget.
        # ModelSelect2MultipleWidget не позволяет выбирать несколько одинаковых значений, так как использует QuerySet.
        # Поэтому я проверяю корректность формы, создавая экземпляр класса AddOrderForm(data),
        # а сохранение в базу данных произвожу этим методом, который подсчитывает количество одинаковых блюд (quantity).
        data = self.cleaned_data
        # Записываем данные о новом заказе
        order = Order(table_number=data["table_number"], status=data["status"])
        order.save()
        # Записываем данные о блюдах в заказе, подсчитывая количество повторяющихся блюд.
        for item in data["items"]:
            OrderItem.objects.create(order=order, item=item, quantity=items.count(item.id))

    @staticmethod
    def process_data(data: QueryDict) -> Dict[str, Any]:
        """Обработка данных для возможности создания экземпляра класса

        :param data: Данные POST, которые возвращает frontend.
        :return: Правильные данные, которые подходят для класса.
        """
        data = dict(data)
        # Приводи id заказов из формата id/number в формат id
        data["items"] = [int(i_id[:i_id.find("/")]) for i_id in data["items"]]
        data["table_number"] = int(data["table_number"][0])
        # Убираем ошибку кодировки
        data["status"] = str(data["status"][0]).strip("&#x27;")
        return data

    # def get_counters(self) -> Dict[str, Any]:
    #     """"""
    #


class FilterOrdersForm(forms.Form):
    """Создание формы фильтра заказов"""
    table_number = forms.IntegerField(
        min_value=1, required=False,
        widget=forms.NumberInput(attrs={
            "placeholder": "Поиск по номеру стола",
            "oninput": "submitFilterForm()"
        })
    )
    status = forms.ChoiceField(
        choices=[("", "Все статусы")] + list(OrderStatuses.choices),
        label="Статус заказа",
        required=False,
        initial="Все статусы",
        widget=forms.Select(attrs={
            "class": "form-control",
            "onchange": "submitFilterForm()"
        })
    )


class DeleteOrderForm(forms.Form):
    """Форма удаление заказа по id"""
    order_id = forms.IntegerField(
        label="Введите id заказа для удаления",
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "id заказа"
        }),
        error_messages={
            "required": "Введите id заказа для удаления.",
        }
    )

    def clean_order_id(self):
        """Проверка, что выбранный id существует"""
        order_id = self.cleaned_data.get("order_id")
        if not Order.objects.filter(id=order_id).exists():
            raise forms.ValidationError(f"Заказа id{order_id} не найден.")
        return order_id
