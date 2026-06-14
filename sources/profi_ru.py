SOURCE_NAME = "profi_ru"
BASE_ORDER_URL = "https://profi.ru/backoffice/n.php?o="


def build_order_url(order_id):
    return f"{BASE_ORDER_URL}{order_id}"


def build_budget(price):
    if not price:
        return ""

    price_prefix = price.get("prefix", "")
    price_value = price.get("value", "")
    price_suffix = price.get("suffix", "")

    return (price_prefix + " " + price_value + " " + price_suffix).strip()


def parse_board_item(item):
    if item.get("type") != "SNIPPET":
        return None

    order_id = item.get("id")
    if not order_id:
        return None

    title = item.get("title", "")
    description = item.get("description", "")
    price = item.get("price") or {}
    budget = build_budget(price)

    order = {
        "source": SOURCE_NAME,
        "external_id": order_id,
        "title": title,
        "url": build_order_url(order_id),
        "description": description,
        "budget": budget,
        "tags": [],
        "project_type": "Заказ",
    }

    return order


def parse_board_items(items):
    orders = []

    for item in items:
        order = parse_board_item(item)

        if order is None:
            continue

        orders.append(order)

    return orders


def parse_graphql_response(response_data):
    data = response_data.get("data") or {}
    board_data = data.get("boSearchBoardItems") or {}
    items = board_data.get("items") or []

    return parse_board_items(items)


def fetch_orders(pages=1, verbose=True):
    """
    Заглушка на время перехода к Playwright.

    Profi.ru не удалось стабильно получить через обычный requests/cURL:
    сервер возвращает 401 not authenticated вне браузерного контекста.

    Следующий шаг:
    - Playwright открывает Profi.ru как браузер;
    - перехватывает GraphQL-ответ;
    - передаёт JSON в parse_graphql_response().
    """
    if verbose:
        print("Profi.ru: источник пока не подключён, нужен Playwright-транспорт")

    return []


if __name__ == "__main__":
    test_items = [
        {
            "id": "90518402",
            "type": "SNIPPET",
            "title": "Программист инстаграм",
            "description": "Восстановление аккаунта",
            "price": {
                "prefix": "до",
                "value": "15 000 ₽",
                "suffix": "",
            },
        },
        {
            "id": "STORIES",
            "type": "STORIES",
        },
        {
            "id": "DIVIDER",
            "type": "DIVIDER",
            "title": "Вы посмотрели все новые заказы",
        },
    ]

    response_data = {
        "data": {
            "boSearchBoardItems": {
                "items": test_items
            }
        }
    }

    orders = parse_graphql_response(response_data)

    print("orders count:", len(orders))
    print(orders)