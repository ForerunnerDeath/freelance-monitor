orders = [
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
    {"id": 2, "title": "Fix layout", "budget": 3000, "tags": ["html", "css"]},
    {"id": 3, "title": "Parser to Excel", "budget": "12000 RUB", "tags": ["python", "parser"]},
    {"id": 4, "title": "Python script for CSV", "budget": None, "tags": ["python"]},
    {"id": 5, "title": "Telegram notifications", "budget": "до 8000 ₽", "tags": []},
    {"id": 1, "title": "Telegram bot", "budget": 7000, "tags": ["python", "telegram"]},
]

def parse_budget(raw_budget):
    if raw_budget is None:
        return 0

    if isinstance(raw_budget, int):
        return raw_budget

    if isinstance(raw_budget, str):
        digits = ""

        for char in raw_budget:
            if char.isdigit():
                digits = digits + char

        if digits == "":
            return 0

        return int(digits)

    return 0

def has_good_keywords(order):
    tags = order.get("tags", [])
    title = order.get("title", "").lower()

    if "python" in tags or "telegram" in tags:
        return True
    if "python" in title or "telegram" in title or "parser" in title:
        return True
    return False

def check_order(order):
    raw_budget = order.get("budget", 0)
    budget = parse_budget(raw_budget)
    tags = order.get("tags", [])    # здесь нужно достать tags

    if budget < 5000: 
        return "low_budget" # если бюджет меньше 5000 - вернуть "low_budget"

    if not has_good_keywords(order):
        return "bad_keywords"

    return "matched" # иначе вернуть "matched"


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