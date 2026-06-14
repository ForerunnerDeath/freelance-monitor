from filters import parse_budget, check_order_v2

def test_parse_budget_simple():
    assert parse_budget("15000") == 15000
    assert parse_budget("15 000") == 15000
    assert parse_budget("15 000 руб.") == 15000
    assert parse_budget("") is None
    assert parse_budget("договорная") is None

def test_parse_budget_extra_cases():
    assert parse_budget(None) is None
    assert parse_budget("25000") == 25000
    assert parse_budget("от 20 000 до 30 000 руб.") == 20000
    assert parse_budget("Бюджет: 7 500 ₽") == 7500

def test_check_order_v2_matched():
    order = {
    "title": "Сделать парсер сайта",
    "description": "",
    "budget": "15000",
    "project_type": "project",
    "tags": [],
    }  
    result = check_order_v2(order)
    assert result["status"] == "matched"
    assert result["reason"] == "matched"
    assert result.get("matched_keyword")
    assert result["budget"] == 15000

def test_check_order_v2_risky():
    order = {
        "title": "Доработать Битрикс24 и интеграцию",
        "description": "Нужно настроить 1С и обмен данными",
        "budget": "15000",
        "project_type": "project",
        "tags": [],
        }
    
    result = check_order_v2(order)
    assert result["status"] == "risky"
    assert result["reason"] == "risky_keyword"
    assert result.get("risky_keyword")

def test_check_order_v2_rejected_bad_keyword():
    order = {
        "title": "Копирайтер",
        "description": "Копирайтинг чего то там",
        "budget": "15000",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "rejected"
    assert result["reason"] == "negative_keyword"
    assert result.get("negative_keyword")

def test_check_order_v2_rejected_low_budget():
    order = {
        "title": "Сделать парсер сайта",
        "description": "парсинг",
        "budget": "500",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "rejected"
    assert result["reason"] == "low_budget"
    assert result["budget"] == 500        

def test_check_order_v2_rejected_vacancy():
    order = {
        "title": "Парсер",
        "description": "...",
        "budget": "15000",
        "project_type": "Вакансия",
        "tags": [],
    }
    result = check_order_v2(order)

    assert result["status"] == "rejected"
    assert result["reason"] == "vacancy"

def test_check_order_v2_rejected_no_good_keywords():
    order = {
        "title": "Небольшая задача по сайту",
        "description": "Нужно помочь с простой правкой",
        "budget": "15000",
        "project_type": "project",
        "tags": [],
    }
    result = check_order_v2(order)

    assert result["status"] == "rejected"
    assert result["reason"] == "bad_keywords"

def test_check_order_v2_bad_keyword_has_priority_over_good_keyword():
    order = {
        "title": "Копирайтер для парсера",
        "description": "...",
        "budget": "15000",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "rejected"
    assert result["reason"] == "negative_keyword"
    assert result.get("negative_keyword")

def test_check_order_v2_matched_without_budget():
    order = {
        "title": "парсер",
        "description": "...",
        "budget": "договорная",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "matched"
    assert result["reason"] == "matched"
    assert result["budget"] is None
    assert result.get("matched_keyword")

def test_check_order_v2_risky_without_budget():
    order = {
        "title": "Доработать Битрикс24",
        "description": "...",
        "budget": "договорная",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "risky"
    assert result["reason"] == "risky_keyword"
    assert result["budget"] is None
    assert result.get("risky_keyword")

def test_check_order_v2_matched_by_tag():
    order = {
        "title": "Нужна помощь с задачей",
        "description": "Описание без ключевых слов",
        "budget": "15000",
        "project_type": "project",
        "tags": ["Python"],
    }

    result = check_order_v2(order)

    assert result["status"] == "matched"
    assert result["reason"] == "matched"
    assert result.get("matched_keyword")

def test_check_order_v2_risky_wordpress():
    order = {
        "title": "Доработать wordpress сайт",
        "description": "Нужно поправить несколько вещей",
        "budget": "15000",
        "project_type": "project",
        "tags": [],
    }

    result = check_order_v2(order)

    assert result["status"] == "risky"
    assert result["reason"] == "risky_keyword"
    assert result.get("risky_keyword")