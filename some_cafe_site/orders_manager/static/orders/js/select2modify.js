$(document).ready(function () {
    $("#id_items").select2({
        multiple: true,
        query: function (query) {
            var data = {results: []};
            var term = query.term  // Получаем поисковый запрос пользователя
            if (term)
                term = term.toLowerCase();

            for (var i = 0; i < items.length; i++) {
                var counter = counters[items[i].id] || 0;
                var dishName = items[i].dish.toLowerCase();

                // Фильтрация по поисковому запросу
                if (dishName.includes(term) || !term) {
                    data.results.push({
                        "id": items[i].id + "/" + counter,
                        "text": items[i].dish
                    });
                }
            }

            query.callback(data);
        },
        formatSelection: function (item) {
            return item.text + counters[item.id];
        },
        formatResult: function (item) {
            return item.id;
        },
        closeOnSelect: true
    });

    // Обработка выбора блюда (увеличение счётчика)
    $("#id_items").on('select2:select', function (e) {
        var selectedItem = e.params.data;
        if (typeof selectedItem.id === 'string') {
            var selectedItemId = selectedItem.id.split('/')[0];
            if (!counters[selectedItemId]) {
                counters[selectedItemId] = 0;
            }
            counters[selectedItemId] += 1;
            $(this).trigger('change');
        }
    });

    // Обработка удаления блюда (увеличение счётчика)
    $("#id_items").on('select2:unselect', function (e) {
        var unselectedItem = e.params.data;
        if (typeof unselectedItem.id === 'string') {
            var unselectedItemId = unselectedItem.id.split('/')[0];
            if (counters[unselectedItemId] > 0) {
                counters[unselectedItemId] -= 1;
            }
            $(this).trigger('change');
        }
    });

    $(document).on('change', '.dynamic-dropdown', function () {
        $(this).select2();
    });
});
