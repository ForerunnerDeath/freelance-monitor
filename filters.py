import config
import re

GOOD_KEYWORDS = [
    "python",
    "fastapi",
    "django",
    "flask",
    "sqlalchemy",
    "postgresql",
    "postgres",
    "sqlite",
    "redis",
    "celery",
    "docker",
    "linux",

    "парсинг",
    "парсер",
    "parser",
    "scraping",
    "скрипт",
    "автоматизация",
    "автоматизировать",

    "csv",
    "excel",
    "таблица",
    "google sheets",
    "гугл таблиц",
    "калькулятор",

    "telegram",
    "телеграм",
    "telegram-бот",
    "телеграм-бот",
    "чат-бот",
    "чат бот",
    "бот для сайта",
    "бот поддержки",
    "бот для мессенджера",
    "бот для whatsapp",
    "бот для ватсап",
    "бот для vk",
    "бот для вк",

    "rest api",
    "api",
    "webhook",
    "вебхук",
    "интеграция api",
    "интеграция",

    "vps",
    "сервер",
    "деплой",
    "развернуть",
    "настроить сервер",

    "сбор данных",
    "выгрузка данных",
    "из выдачи",
    "гуглдок",
    "google docs"
]
BAD_KEYWORDS = [
    "таргетолог",
    "директолог",
    "копирайтер",
    "рерайтер",
    "контент-менеджер",
    "контент-креатор",
    "smm",
    "seo",

    "обзвон",
    "холодные звонки",
    "продавцы",
    "кассиры",
    "оператор чата",
    "вести переписку",

    "отзыв",
    "отзывы",
    "перевод",
    "перефразировать",

    "дизайнер",
    "дизайн",
    "figma",
    "логотип",
    "баннер",
    "монтажер",
    "монтажёр",
    "видео",
    "3d",

    "вакансия",
    "вакансию",
    "ищем сотрудника",
    "в штат",
    "полная занятость",
    "офис",
    "резюме",
    "кандидатов",

    "за процент",
    "без оплаты",
    "за отзыв",
    "стажировка",
    "доля в проекте",
]

RISKY_KEYWORDS = [
    "битрикс",
    "bitrix",
    "bitrix24",
    "битрикс24",

    "1с",
    "1c",
    "1C",
    "1С",

    "б24",
    "мойсклад",
    "мой склад",

    "wordpress",
    "вордпресс",
    "opencart",
    "php",
    "laravel",
    "yii",
    "modx",
    "cms",

    "flutter",
    "react",
    "vue",
    "frontend",
    "фронтенд",

    "crm",
    "amoCRM",
    "amocrm",

    "диплом",
    "дипломная",
    "курсовая",
    "реферат",
    "презентация + речь",
]

def parse_budget(raw_budget):
    if raw_budget is None:
        return None
    if isinstance(raw_budget, int):
        return raw_budget

    if isinstance(raw_budget, str):
        budget_text = raw_budget.strip()
        if budget_text == "":
            return None
        numbers = re.findall(r"\d[\d\s]*", budget_text)
        if len(numbers) == 0:
            return None
        first_number = numbers[0]
        digits = ""
        for char in first_number:
            if char.isdigit():
                digits = digits + char
        if digits == "":
            return None

        return int(digits)

    return None

def find_bad_keyword(order):
    title = order.get("title", "").lower()
    description = order.get("description", "").lower()
    text = title + " " + description

    for keyword in BAD_KEYWORDS:
        if keyword.lower() in text:
            return keyword

    return None

def find_good_keyword(order):
    raw_tags = order.get("tags", [])
    tags = []

    for tag in raw_tags:
        if isinstance(tag, str):
            tags.append(tag.lower())
    title = order.get("title", "").lower()
    description = order.get("description", "").lower()
    text = title + " " + description + " " + " ".join(tags)

    for keyword in GOOD_KEYWORDS:
        keyword_lower = keyword.lower()
        if keyword_lower in text:
            return keyword
    return None    

def find_risky_keyword(order):
    raw_tags = order.get("tags", [])
    tags = []

    for tag in raw_tags:
        if isinstance(tag, str):
            tags.append(tag.lower())
    title = order.get("title", "").lower()
    description = order.get("description", "").lower()
    text = title + " " + description + " " + " ".join(tags)

    for keyword in RISKY_KEYWORDS:
        keyword_lower = keyword.lower()
        if keyword_lower in text:
            return keyword
    return None

def is_vacancy(order):
    project_type = order.get("project_type", "").lower()

    if "вакансия" in project_type:
        return True

    return False

def check_order_v2(order):
    raw_budget = order.get("budget", 0)
    budget = parse_budget(raw_budget)

    if is_vacancy(order):
        return {
            "status": "rejected",
            "reason": "vacancy",
            "budget": budget,
        }

    bad_keyword = find_bad_keyword(order)
    if bad_keyword is not None:
        return {
            "status": "rejected",
            "reason": "negative_keyword",
            "budget": budget,
            "negative_keyword": bad_keyword,
        }

    if budget is not None and budget > 0 and budget < config.MIN_BUDGET:
        return {
            "status": "rejected",
            "reason": "low_budget",
            "budget": budget,
        }
    risky_keyword = find_risky_keyword(order)
    if risky_keyword is not None:
        return {
            "status": "risky",
            "reason": "risky_keyword",
            "risky_keyword": risky_keyword,
            "budget": budget
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