from pathlib import Path

from playwright.sync_api import sync_playwright

import config

SOURCE_NAME = "profi_ru"
BASE_ORDER_URL = "https://profi.ru/backoffice/n.php?o="
PROFI_URL = "https://profi.ru/backoffice/n.php"
PLAYWRIGHT_WAIT_MS = 5000


class ProfiAuthError(Exception):
    pass


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

    return {
        "source": SOURCE_NAME,
        "external_id": order_id,
        "title": title,
        "url": build_order_url(order_id),
        "description": description,
        "budget": budget,
        "tags": [],
        "project_type": "Заказ",
    }


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


def is_login_page(page):
    current_url = page.url.lower()

    if "login" in current_url or "auth" in current_url:
        return True

    try:
        body_text = page.locator("body").inner_text(timeout=1500).lower()
    except Exception:
        return False

    login_markers = [
        "войти",
        "вход",
        "телефон",
        "пароль",
        "код из смс",
        "авторизац",
    ]

    return any(marker in body_text for marker in login_markers)


def open_profi_context(playwright):
    auth_mode = config.PROFI_RU_AUTH_MODE
    headless = config.PROFI_RU_HEADLESS

    if auth_mode == "persistent_profile":
        profile_dir = Path(config.PROFI_RU_PROFILE_DIR)
        profile_dir.mkdir(parents=True, exist_ok=True)

        browser_context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            viewport={"width": 1400, "height": 900},
        )

        return browser_context, None

    storage_state_path = Path(config.PROFI_RU_STORAGE_STATE)

    if not storage_state_path.exists():
        raise ProfiAuthError(
            f"Profi.ru storage_state file not found: {storage_state_path}"
        )

    browser = playwright.chromium.launch(
        headless=headless,
    )

    browser_context = browser.new_context(
        viewport={"width": 1400, "height": 900},
        storage_state=str(storage_state_path),
    )

    return browser_context, browser


def fetch_orders(pages=1, verbose=True):
    found_orders = []
    seen_ids = set()

    auth_failed_seen = False
    last_graphql_status = None
    graphql_seen = False
    login_page_seen = False

    def handle_response(response):
        nonlocal auth_failed_seen
        nonlocal last_graphql_status
        nonlocal graphql_seen

        if "/graphql" not in response.url:
            return

        graphql_seen = True
        last_graphql_status = response.status

        if response.status == 401:
            auth_failed_seen = True

            if verbose:
                print("GraphQL status:", response.status)

            return

        if response.status != 200:
            if verbose:
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
        new_orders_count = 0

        for order in orders:
            if order["external_id"] in seen_ids:
                continue

            seen_ids.add(order["external_id"])
            found_orders.append(order)
            new_orders_count += 1

        if verbose:
            print("Новых заказов в этом ответе:", new_orders_count)
            print("Всего найдено заказов:", len(found_orders))

    with sync_playwright() as p:
        browser_context = None
        browser = None

        try:
            browser_context, browser = open_profi_context(p)

            page = browser_context.new_page()
            page.on("response", handle_response)

            page.goto(PROFI_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(PLAYWRIGHT_WAIT_MS)

            login_page_seen = is_login_page(page)

            for scroll_number in range(pages - 1):
                if verbose:
                    print("Profi.ru scroll:", scroll_number + 1)

                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)

        finally:
            if browser_context is not None:
                browser_context.close()

            if browser is not None:
                browser.close()

    if auth_failed_seen and len(found_orders) == 0:
        raise ProfiAuthError(
            "Profi.ru auth expired: GraphQL status 401. "
            "Нужно обновить авторизацию Profi.ru."
        )

    if login_page_seen and len(found_orders) == 0:
        raise ProfiAuthError(
            "Profi.ru auth expired: browser opened login page. "
            "Нужно обновить авторизацию Profi.ru."
        )

    if verbose and auth_failed_seen and len(found_orders) > 0:
        print("Profi.ru: был GraphQL 401, но заказы успешно получены")

    if verbose and not graphql_seen:
        print("Profi.ru GraphQL responses not seen")

    if verbose and graphql_seen and last_graphql_status != 200 and not found_orders:
        print("Profi.ru last GraphQL status:", last_graphql_status)

    return found_orders


if __name__ == "__main__":
    from filters import check_order_v2

    orders = fetch_orders(pages=2, verbose=True)
    print("orders count:", len(orders))

    stats = {
        "matched": 0,
        "risky": 0,
        "rejected": 0,
    }

    for order in orders:
        result = check_order_v2(order)
        status = result["status"]
        stats[status] += 1

    print("First 5 orders:")

    for order in orders[:5]:
        result = check_order_v2(order)
        status = result["status"]

        print("-----")
        print(order["external_id"])
        print(order["title"])
        print(order["description"][:300])
        print(order["budget"])
        print("status:", status)
        print("reason:", result.get("reason"))
        print(order["url"])
        print("matched_keyword:", result.get("matched_keyword"))
        print("negative_keyword:", result.get("negative_keyword"))
        print("risky_keyword:", result.get("risky_keyword"))

    print("Matched orders:")

    for order in orders:
        result = check_order_v2(order)

        if result["status"] == "matched":
            print(order["external_id"])
            print(order["title"])
            print(order["budget"])
            print("reason:", result.get("reason"))
            print("matched_keyword:", result.get("matched_keyword"))
            print(order["url"])
            print(order["description"][:300])

    print("Risky orders:")

    for order in orders:
        result = check_order_v2(order)

        if result["status"] == "risky":
            print(order["external_id"])
            print(order["title"])
            print(order["budget"])
            print("reason:", result.get("reason"))
            print("risky_keyword:", result.get("risky_keyword"))
            print(order["url"])
            print(order["description"][:300])

    print("stats:", stats)
