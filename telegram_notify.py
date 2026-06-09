import os
import requests
from dotenv import load_dotenv


load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


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

    if tags:
        tags_text = ", ".join(tags)
    else:
        tags_text = "нет тегов"

    message = (
        "🔥 Новый подходящий заказ\n\n"
        f"Источник: {source}\n"
        f"ID: {external_id}\n"
        f"Название: {title}\n"
        f"Бюджет: {budget}\n"
        f"Теги: {tags_text}\n"
        f"Ключ: {matched_keyword}\n"
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

    response = requests.post(url, json=payload, timeout=10)

    if response.status_code != 200:
        print("Ошибка отправки Telegram:", response.status_code, response.text)
        return False

    return True


def notify_about_order(order, check_result):
    message = format_order_message(order, check_result)
    return send_telegram_message(message)