import filters
import sample_data

def process_orders(orders):
    seen_ids = set()

    total_count = 0
    duplicate_count = 0
    matched_count = 0
    rejected_count = 0

    for order in orders:
        total_count += 1
        order_id = order.get("id")
        title = order.get("title", "Без названия")

        if order_id in seen_ids:
            duplicate_count += 1
            print("Дубль заказа", order_id, title)
            continue

        seen_ids.add(order_id)

        status = filters.check_order(order)

        if status == "matched":
            matched_count += 1
            print("Подходящий заказ", order_id, title)
        else:
            rejected_count += 1
            print("Не подходит", order_id, title, "Причина:", status)

    print()
    print("Статистика:")
    print("Всего заказов:", total_count)
    print("Дублей:", duplicate_count)
    print("Подходящих:", matched_count)
    print("Неподходящих:", rejected_count)


process_orders(sample_data.orders)