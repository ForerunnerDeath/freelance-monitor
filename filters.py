import re

import config

GOOD_KEYWORDS = [
    # Python / backend
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

    # Парсинг / автоматизация
    "парсинг",
    "парсер",
    "parser",
    "scraping",
    "скрипт",
    "автоматизация",
    "автоматизировать",
    "автоматизировать процесс",
    "автоматизировать работу",
    "сбор данных",
    "выгрузка данных",
    "обработка данных",
    "из выдачи",

    # Таблицы / файлы / отчёты
    "csv",
    "excel",
    "xlsx",
    "таблица",
    "google sheets",
    "google docs",
    "гугл таблиц",
    "гуглдок",
    "калькулятор",
    "отчёт",
    "отчет",

    # Telegram / чат-боты — без одиночного "telegram"
    "telegram-бот",
    "telegram бот",
    "бот telegram",
    "бот в telegram",
    "бот для telegram",
    "бот для телеграм",
    "телеграм-бот",
    "телеграм бот",
    "бот телеграм",
    "бот в телеграм",
    "чат-бот",
    "чат бот",
    "бот для сайта",
    "бот поддержки",
    "бот для мессенджера",
    "бот для whatsapp",
    "бот для ватсап",
    "бот для vk",
    "бот для вк",

    # API / интеграции
    "rest api",
    "api",
    "webhook",
    "вебхук",
    "интеграция api",
    "интеграция с api",
    "подключить api",
    "настроить api",

    # Серверы / деплой
    "vps",
    "деплой",
    "deploy",
    "развернуть",
    "настроить сервер",
    "настройка сервера",
    "развернуть на сервере",
    "деплой на сервер",
    "настроить vps",
    "настройка vps",

    # AI — оставляем, но дальше фильтры должны отсекать спам/рассылки
    "ии-агент",
    "ии агент",
    "ai agent",
    "openai",
    "chatgpt",
    "gpt",
]

BAD_KEYWORDS = [
    # Маркетинг / реклама / контент
    "таргетолог",
    "директолог",
    "копирайтер",
    "рерайтер",
    "контент-менеджер",
    "контент менеджер",
    "контент-креатор",
    "контент креатор",
    "smm",
    "seo",
    "маркетолог",
    "трафик менеджер",
    "трафик-менеджер",
    "инста",
    "инсте",
    "инсту",
    "instagram",
    "инстаграм",
    "фейсбук",
    "facebook",
    "аккаунты в инсте",
    "доступ к сообщениям",
    "дать доступ к сообщениям",

    # Лидогенерация / продажи / спам / рассылки
    "лидогенерация",
    "лиды",
    "лидов",
    "сбор лидов",
    "сбор базы",
    "сбор баз",
    "сбор контактов",
    "база клиентов",
    "базы клиентов",
    "массовая рассылка",
    "массовые рассылки",
    "рассылка",
    "рассылки",
    "спам",
    "прогрев",
    "прогрев аккаунтов",
    "прогрев номеров",
    "ферма аккаунтов",
    "ферма номеров",
    "регистрация аккаунтов",
    "много аккаунтов",
    "парс telegram",
    "парс телеграм",
    "парсинг telegram",
    "парсинг телеграм",
    "telegram-пользователей",
    "телеграм-пользователей",
    "пользователей telegram",
    "пользователей телеграм",
    "участников telegram",
    "участников телеграм",

    # Обзвоны / продажи
    "обзвон",
    "холодные звонки",
    "голосовой робот",
    "робот для обзвона",
    "продавцы",
    "кассиры",
    "оператор чата",
    "вести переписку",

    # Отзывы / тексты / переводы
    "отзыв",
    "отзывы",
    "написать отзывы",
    "перевод",
    "перевести текст",
    "перефразировать",

    # Дизайн / видео / 3D
    "дизайнер",
    "дизайн",
    "figma",
    "логотип",
    "баннер",
    "монтажер",
    "монтажёр",
    "монтаж видео",
    "видео",
    "3d",
    "3д",

    # Вакансии / найм
    "вакансия",
    "вакансию",
    "ищем сотрудника",
    "ищем специалиста в штат",
    "в штат",
    "полная занятость",
    "офис",
    "резюме",
    "кандидатов",
    "собеседование",

    # Оплата мусором
    "за процент",
    "без оплаты",
    "за отзыв",
    "стажировка",
    "доля в проекте",

    # Не наш профиль: промышленность / железо / специфичные системы
    "плк",
    "plc",
    "codesys",
    "scada",
    "ириди",
    "iridium",
    "умный дом",
    "arduino",
    "ардуино",

    # Сомнительное / незаконное / вредное
    "взлом",
    "взломать",
    "обойти защиту",
    "обход защиты",
    "накрутка",
    "накрутить",
    "массовая регистрация",
    "аккаунт восстановить",
    "восстановление аккаунта",
    "инстаграм",
    "instagram",

    "unity",
    "юнити",
    "разработчик игр",
    "разработка игр",
    "game dev",
    "gamedev",
    "геймдев",
    "мультиплеер",
    "многопользовательская игра",
    "игра для мобильных устройств",
    "мобильная игра",
    "инди-команда",
    "инди команда",
    "бонусы в случае успеха игры",
    "создание мода",
    "модмейкинг",
    "roblox",
    "роблокс",

    "системный администратор",
    "системный админ",
    "сисадмин",
    "администрирование серверов",
    "инженер по схд",
    "инжинер по схд",
    "схд",
    "nas",
    "synology",
    "жёсткий диск",
    "жесткий диск",
    "жёстких дисков",
    "жестких дисков",
    "замена дисков",
    "диагностика nas",
    "аппаратной части",
    "программной части nas",

    "qlua",
    "quik",
    "квик",
    "терминал quik",
    "терминала quik",
    "брокер",
    "фьючерсы",
    "мосбиржа",
    "торговый скрипт",
    "скрипт-сеточник",
    "сеточник",
    "единая торговая сессия",
    "onorder",
    "ontrade",

    "закупки",
    "закупок",
    "закупочный",
    "эксперт по закупкам",
    "аудит текущей системы закупок",
    "вэд",
    "международной торговле",
    "торговле с китаем",
    "автозапчастей",
    "консультационного сотрудничества",
    "руководящих должностях в закупках",
]

RISKY_KEYWORDS = [
    # CMS / сайты на чужих движках
    "битрикс",
    "bitrix",
    "bitrix24",
    "битрикс24",
    "б24",

    "wordpress",
    "вордпресс",
    "opencart",
    "modx",
    "cms",

    # 1С / склад / CRM
    "1с",
    "1c",
    "1C",
    "1С",
    "мойсклад",
    "мой склад",
    "crm",
    "amoCRM",
    "amocrm",

    # PHP-фреймворки — можно брать, но осторожно
    "php",
    "laravel",
    "yii",

    # Frontend / mobile — не основной фокус
    "flutter",
    "react",
    "vue",
    "frontend",
    "фронтенд",
    "верстка",
    "вёрстка",

    # Windows / десктоп — иногда можно, но не приоритет
    "windows",
    "виндовс",
    "десктоп",
    "desktop",

    # Учёба
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
