from pathlib import Path

from playwright.sync_api import sync_playwright

import config
from sources.profi_ru import PROFI_URL


def main():
    profile_dir = Path(config.PROFI_RU_PROFILE_DIR)
    profile_dir.mkdir(parents=True, exist_ok=True)

    print("Profi.ru profile dir:", profile_dir)
    print("Open noVNC in browser:")
    print("http://127.0.0.1:6080/vnc.html?autoconnect=true")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            viewport={"width": 1400, "height": 900},
        )

        page = context.new_page()
        page.goto(PROFI_URL, wait_until="domcontentloaded")

        input("Войди в Profi.ru через noVNC, потом нажми Enter здесь...")

        context.close()

    print("Persistent Profi.ru profile saved:", profile_dir)


if __name__ == "__main__":
    main()
