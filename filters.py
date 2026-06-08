GOOD_KEYWORDS = ["python", "telegram", "parser", "excel", "api", "bot"]

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
    raw_tags = order.get("tags", [])
    tags = []

    for tag in raw_tags:
        if isinstance(tag, str):
            tags.append(tag.lower())
    title = order.get("title", "").lower()

    for keyword in GOOD_KEYWORDS:
        if keyword in tags:
            return True

    for keyword in GOOD_KEYWORDS:
        if keyword in title:
            return True
    return False

def check_order(order):
    raw_budget = order.get("budget", 0)
    budget = parse_budget(raw_budget)

    if budget < 5000: 
        return "low_budget"

    if not has_good_keywords(order):
        return "bad_keywords"

    return "matched"