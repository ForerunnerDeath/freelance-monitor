from filters import check_order

orders = [
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
    {"id": 2, "title": "Fix layout", "budget": 3000, "tags": ["html", "css"]},
    {"id": 3, "title": "Parser to Excel", "budget": "12000 RUB", "tags": ["python", "parser"]},
    {"id": 4, "title": "Python script for CSV", "budget": None, "tags": ["python"]},
    {"id": 5, "title": "Telegram notifications", "budget": "до 8000 ₽", "tags": []},
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
    {"id": 6, "title": "Excel report automation", "budget": "6000 RUB", "tags": []},
    {"id": 7, "title": "Landing page design", "budget": 15000, "tags": ["design"]},
    {"id": 8, "title": "Small automation task", "budget": 9000, "tags": ["Python", "API"]},
]

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