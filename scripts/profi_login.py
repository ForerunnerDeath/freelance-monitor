from pathlib import Path

from playwright.sync_api import sync_playwright

import config
from sources.profi_ru import PROFI_URL

storage_state_path = Path(config.PROFI_RU_STORAGE_STATE)
storage_state_path.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1400, "height": 900},
    )

    page = context.new_page()
    page.goto(PROFI_URL, wait_until="domcontentloaded")

    input("Войди в Profi.ru в открывшемся браузере, потом нажми Enter здесь...")

    context.storage_state(path=str(storage_state_path))
    browser.close()

print("Storage state saved:", storage_state_path)