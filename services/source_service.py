import time

import redis

import config
import telegram_notify
from logger import log_error
from sources import fl_ru, profi_ru

SOURCE_ALERT_COOLDOWN_SECONDS = 6 * 60 * 60
_local_alert_cache = {}


def send_source_alert_once(alert_key, message, cooldown_seconds=SOURCE_ALERT_COOLDOWN_SECONDS):
    now = time.time()

    try:
        redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True,
            socket_timeout=getattr(config, "REDIS_SOCKET_TIMEOUT", 5),
        )

        was_set = redis_client.set(
            alert_key,
            "1",
            nx=True,
            ex=cooldown_seconds,
        )

        if was_set:
            telegram_notify.send_telegram_message(message)

        return

    except Exception as error:
        last_sent_at = _local_alert_cache.get(alert_key, 0)

        if now - last_sent_at >= cooldown_seconds:
            telegram_notify.send_telegram_message(
                message
                + "\n\n"
                + f"⚠️ Redis cooldown недоступен: {error}"
            )
            _local_alert_cache[alert_key] = now


def get_pages_for_source(source_module):
    if source_module == fl_ru:
        return config.FL_RU_PAGES

    if source_module == profi_ru:
        return config.PROFI_RU_PAGES

    return 1


def get_orders(verbose):
    all_orders = []
    source_modules = []

    if config.ENABLE_FL_RU:
        source_modules.append(fl_ru)

    if config.ENABLE_PROFI_RU:
        source_modules.append(profi_ru)

    for source_module in source_modules:
        try:
            pages = get_pages_for_source(source_module)
            source_orders = source_module.fetch_orders(pages=pages, verbose=verbose)

        except profi_ru.ProfiAuthError as error:
            error_message = f"Ошибка авторизации Profi.ru: {error}"
            log_error(error_message)

            send_source_alert_once(
                "alert:profi_ru_auth_expired",
                (
                    "⚠️ Profi.ru auth expired\n\n"
                    "Profi.ru сейчас не отдаёт заказы: GraphQL 401.\n"
                    "Нужно обновить файл авторизации:\n"
                    "playwright_auth/profi_storage_state.json\n\n"
                    "Команда:\n"
                    "docker compose stop monitor\n"
                    "python -m scripts.profi_login\n"
                    "docker compose start monitor"
                ),
            )

            continue

        except Exception as error:
            log_error(f"Ошибка получения заказов из {source_module.__name__}: {error}")
            continue

        if verbose:
            print("Источник", source_module.__name__, "вернул", len(source_orders), "заказов")

        all_orders.extend(source_orders)

    return all_orders
