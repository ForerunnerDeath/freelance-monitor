import filters
import sample_data

def process_orders(orders):
    seen_ids = set()

    total_count = 0
    duplicate_count = 0
    matched_count = 0
    rejected_count = 0

    matched_orders = []

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
            matched_orders.append(order)
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

    return {
        "total": total_count,
        "duplicates": duplicate_count,
        "matched": matched_count,
        "rejected": rejected_count,
        "matched_orders": matched_orders,
    }


result = process_orders(sample_data.orders)

print()
print("Подходящие заказы в result:")

for order in result["matched_orders"]:
    order_id = order.get("id")
    title = order.get("title", "Без названия")
    budget = order.get("budget", 0)

    print(order_id, title, "Бюджет:", budget)