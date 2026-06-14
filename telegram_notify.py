import os
import requests
import time
from dotenv import load_dotenv


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAX_TELEGRAM_RETRIES = int(os.getenv("MAX_TELEGRAM_RETRIES", "3"))
TELEGRAM_RETRY_DELAY = int(os.getenv("TELEGRAM_RETRY_DELAY", "2"))
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


def is_telegram_configured():
    if not TELEGRAM_BOT_TOKEN:
        return False

    if not TELEGRAM_CHAT_ID:
        return False

    return True


def format_order_message(order, check_result):
    source = order.get("source", "unknown")
    external_id = order.get("external_id", "")
    title = order.get("title", "Без названия")
    budget = order.get("budget", "Не указан")
    url = order.get("url", "")
    tags = order.get("tags", [])
    matched_keyword = check_result.get("matched_keyword")
    risky_keyword = check_result.get("risky_keyword")
    reason = check_result.get("reason")
    status = check_result.get("status")

    if tags:
        tags_text = ", ".join(tags)
    else:
        tags_text = "нет тегов"

    if status == "matched":
        title_line = "🔥 Новый подходящий заказ"
        keyword_label = "Ключ"
        keyword = matched_keyword
    
    elif status == "risky":
        title_line = "⚠️ Рискованный заказ"
        keyword_label = "Риск-слово"
        keyword = risky_keyword

    else:
        title_line = "Новый заказ"
        keyword_label = "Причина"
        keyword = reason

    message = (
        f"{title_line}\n\n"
        f"Источник: {source}\n"
        f"ID: {external_id}\n"
        f"Название: {title}\n"
        f"Бюджет: {budget}\n"
        f"Теги: {tags_text}\n"
        f"{keyword_label}: {keyword}\n"
    )

    if url:
        message += f"\nСсылка: {url}"

    return message


def send_telegram_message(text):
    if not is_telegram_configured():
        print("Telegram не настроен: проверь TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
    }

    for attempt in range(1, MAX_TELEGRAM_RETRIES + 1):
        try:
            response = requests.post(url, json=payload, timeout=10)   
            break            
        except requests.exceptions.RequestException as error:
            if attempt < MAX_TELEGRAM_RETRIES:
                print("Сетевая ошибка Telegram, попытка", attempt, "из", MAX_TELEGRAM_RETRIES, error)
                print("Повтор через", TELEGRAM_RETRY_DELAY, "сек.")
                time.sleep(TELEGRAM_RETRY_DELAY)
                continue
            else:
                print("Сетевая ошибка Telegram:", error)
                return False
    try:
        response_data = response.json()
    except ValueError:
        print("Telegram вернул не JSON:", response.text)
        return False

    if response.status_code != 200:
        print("Ошибка отправки Telegram:", response.status_code, response_data.get("description", response.text))
        return False
    if response_data.get("ok") is not True:
        print("Telegram API error:", response_data.get("description", "Без описания"))
        return False
    return True


def notify_about_order(order, check_result):
    message = format_order_message(order, check_result)
    return send_telegram_message(message)