from playwright.sync_api import sync_playwright
from sources.profi_ru import parse_graphql_response
import debug_profi_login

BASE_ORDER_URL = debug_profi_login.PROFI_URL
USER_DATA_DIR = debug_profi_login.USER_DATA_DIR
found_orders = []

def handle_response(response):
    if "/graphql" not in response.url:
        return
    if response.status != 200:
        print("GraphQL status:", response.status)
        return
    try:
        data = response.json()
    except Exception as error:
        print("GraphQL status:", response.status, response.url)
        return
    data_block = data.get("data") or {}
    if "boSearchBoardItems" not in data_block:
        return
    else:
        orders = parse_graphql_response(data)
    found_orders.extend(orders)
    print("Найдено заказов в этом ответе:", len(orders))
    print("Всего найдено заказов:", len(found_orders))

def main():
    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
        user_data_dir = USER_DATA_DIR,
        headless = False,
        viewport={"width": 1400, "height": 900}
        )
        page = browser_context.new_page()
        page.on("response", handle_response)
        page.goto(BASE_ORDER_URL, wait_until = "domcontentloaded")
        page.wait_for_timeout(5000)
        print("Браузер открыт")
        input("Когда страница заказов загрузится, нажми Enter...")
        page.wait_for_timeout(2000)
        print("Текущий URL:", page.url)
        print("Итого найдено заказов:", len(found_orders))
        for order in found_orders[:3]:
            print("-----")
            print(order["external_id"])
            print(order["title"])
            print(order["budget"])
            print(order["url"])
        browser_context.close()

if __name__ == "__main__":
    main()
    
