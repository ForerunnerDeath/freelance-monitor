from playwright.sync_api import sync_playwright
SOURCE_NAME = "profi_ru"
BASE_ORDER_URL = "https://profi.ru/backoffice/n.php?o="
PROFI_URL = "https://profi.ru/backoffice/n.php"
USER_DATA_DIR = "playwright_profiles/profi"
PLAYWRIGHT_WAIT_MS = 5000



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
    found_orders = []
    def handle_response(response):
        if "/graphql" not in response.url:
            return
        if verbose:
            if response.status != 200:
                print("GraphQL status:", response.status)
                return
        try:
            data = response.json()
        except Exception as error:
            if verbose:
                print("Не удалось прочитать GraphQL JSON:", error)
            return
        data_block = data.get("data") or {}
        if "boSearchBoardItems" not in data_block:
            return
        orders = parse_graphql_response(data)
        found_orders.extend(orders)
        if verbose:
            print("Найдено заказов в этом ответе:", len(orders))
            print("Всего найдено заказов:", len(found_orders))
        
    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
        user_data_dir = USER_DATA_DIR,
        headless = False,
        viewport={"width": 1400, "height": 900}
        )
        page = browser_context.new_page()
        page.on("response", handle_response)
        page.goto(PROFI_URL, wait_until = "domcontentloaded")
        page.wait_for_timeout(PLAYWRIGHT_WAIT_MS)
        browser_context.close()

    return found_orders


if __name__ == "__main__":
    from filters import check_order_v2
    orders = fetch_orders(verbose=True)
    print("orders count:", len(orders))
    stats = {
        "matched": 0,
        "risky": 0,
        "rejected": 0,
    }
    for index, order in enumerate(orders):
        result = check_order_v2(order)
        status = result["status"]
        stats[status] += 1

        if index < 5:
            print("-----")
            print(order["external_id"])
            print(order["title"])
            print(order["budget"])
            print("status:", status)
            print("reason:", result.get("reason"))
            print(order["url"])
            print("matched_keyword:", result.get("matched_keyword"))
            print("negative_keyword:", result.get("negative_keyword"))
            print("risky_keyword:", result.get("risky_keyword"))
    print ("stats:", stats)