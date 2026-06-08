orders = [
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
    {"id": 2, "title": "Fix layout", "budget": 3000, "tags": ["html", "css"]},
    {"id": 3, "title": "Parser to Excel", "budget": 12000, "tags": ["python", "parser"]},
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
]


def check_order(order):
    budget = order.get("budget", 0)  # здесь нужно достать budget
    tags = order.get("tags", [])    # здесь нужно достать tags

    if budget < 5000 : 
        return "low_budget" # если бюджет меньше 5000 - вернуть "low_budget"

    if "python" not in tags and "telegram" not in tags: 
        return "bad_tags" # если нет ни python, ни telegram - вернуть "bad_tags"

    return "matched" # иначе вернуть "matched"
    pass


seen_ids = set()

for order in orders:
    order_id = order.get("id")
    title = order.get("title", "Без названия")

    if order_id in seen_ids:
        print("Дубль заказа", order_id, title)
        continue

    seen_ids.add(order_id)

    status = check_order(order)

    if status == "matched":
        print("Подходящий заказ", order_id, title)
    else:
        print("Не подходит", order_id, title, "Причина:", status)