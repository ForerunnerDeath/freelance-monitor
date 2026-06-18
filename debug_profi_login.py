from playwright.sync_api import sync_playwright

PROFI_URL = "https://profi.ru/backoffice/n.php"
USER_DATA_DIR = "playwright_profiles/profi"

def main():
    with sync_playwright() as p:
        browser_context = p.chromium.launch_persistent_context(
        user_data_dir = USER_DATA_DIR,
        headless = False,
        viewport={"width": 1400, "height": 900}
        )
        page = browser_context.new_page()
        page.goto(PROFI_URL, wait_until = "domcontentloaded")
        print("Браузер открыт")
        input("Когда войдёшь и увидишь заказы, нажми Enter...")
        print("Текущий URL:", page.url)
        browser_context.close()

if __name__ == "__main__":
    main()