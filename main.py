import filters
import sample_data
import db

def process_orders(orders):

    total_count = 0
    duplicate_count = 0
    matched_count = 0
    rejected_count = 0

    matched_orders = []
    rejected_orders = []

    for order in orders:
        total_count += 1
        order_id = order.get("id")
        title = order.get("title", "Без названия")

        if db.is_order_seen(order_id):
            duplicate_count += 1
            print("Дубль заказа", order_id, title)
            continue

        status = filters.check_order(order)
        reason = status

        if status == "matched":
            matched_count += 1
            matched_orders.append(order)
            print("Подходящий заказ", order_id, title)
        else:
            rejected_count += 1
            rejected_orders.append({
                "order": order,
                "reason": reason,
            })
            print("Не подходит", order_id, title, "Причина:", reason)

        db.save_order(order, status, reason)

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
        "rejected_orders": rejected_orders,
    }


def print_matched_orders(result):
    print()
    print("Подходящие заказы в result:")

    for order in result["matched_orders"]:
        order_id = order.get("id")
        title = order.get("title", "Без названия")
        budget = order.get("budget", 0)

        print(order_id, title, "Бюджет:", budget)


def print_rejected_orders(result):
    print()
    print("Неподходящие заказы в result:")

    for rejected_item in result["rejected_orders"]:
        order = rejected_item["order"]
        reason = rejected_item["reason"]
        order_id = order.get("id")
        title = order.get("title", "Без названия")

        print(order_id, title, "Причина:", reason)


db.init_db()
result = process_orders(sample_data.orders)
print_matched_orders(result)
print_rejected_orders(result)