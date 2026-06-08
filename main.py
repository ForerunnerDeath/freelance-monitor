import filters
import sample_data

seen_ids = set()

for order in sample_data.orders:
    order_id = order.get("id")
    title = order.get("title", "Без названия")

    if order_id in seen_ids:
        print("Дубль заказа", order_id, title)
        continue

    seen_ids.add(order_id)

    status = filters.check_order(order)

    if status == "matched":
        print("Подходящий заказ", order_id, title)
    else:
        print("Не подходит", order_id, title, "Причина:", status)