GOOD_KEYWORDS = ["python", "telegram", "parser", "excel", "api", "bot", "телеграм", "парсинг", "парсер", "скрипт", "автоматизация","csv","таблица","vps", "сервер"]
BAD_KEYWORDS = ["таргетолог", "директолог", "копирайтер", "обзвон", "отзыв", "продавцы", "кассиры", "оператор чата", "вести переписку", "монтажер", "контент-креатор", "вакансию", "кандидатов", "перевод", "перефразировать"]

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

def has_bad_keywords(order):
    title = order.get("title", "").lower()
    for keyword in BAD_KEYWORDS:
        if keyword in title:
            return True
        
    return False

def find_bad_keyword(order):
    title = order.get("title", "").lower()
    for keyword in BAD_KEYWORDS:
        if keyword in title:
            return keyword
        
    return None

def find_good_keyword(order):
    raw_tags = order.get("tags", [])
    tags = []

    for tag in raw_tags:
        if isinstance(tag, str):
            tags.append(tag.lower())
    title = order.get("title", "").lower()

    for keyword in GOOD_KEYWORDS:
        if keyword in tags:
            return keyword

    for keyword in GOOD_KEYWORDS:
        if keyword in title:
            return keyword
    return None    


def check_order_v2(order):
    raw_budget = order.get("budget", 0)
    budget = parse_budget(raw_budget)

    bad_keyword = find_bad_keyword(order)
    if bad_keyword is not None:
        return {
            "status": "rejected",
            "reason": "negative_keyword",
            "budget": budget,
            "negative_keyword": bad_keyword,
        }

    if budget > 0 and budget < 5000:
        return {
            "status": "rejected",
            "reason": "low_budget",
            "budget": budget,
        }
    good_keyword = find_good_keyword(order)
    if good_keyword is None:
        return {
            "status": "rejected",
            "reason": "bad_keywords",
            "budget": budget,
        }
    return {
        "status": "matched",
        "reason": "matched",
        "budget": budget,
        "matched_keyword": good_keyword,
    }