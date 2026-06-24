import os

from dotenv import load_dotenv

load_dotenv()


def get_bool_env(name, default):
    value = os.getenv(name)

    if value is None:
        return default

    value = value.lower()

    if value in ("1", "true", "yes", "on"):
        return True

    if value in ("0", "false", "no", "off"):
        return False

    return default


ENABLE_FL_RU = get_bool_env("ENABLE_FL_RU", True)
ENABLE_PROFI_RU = get_bool_env("ENABLE_PROFI_RU", True)
FL_RU_PAGES = 3
DEFAULT_INTERVAL = 300
MIN_INTERVAL = 60
MIN_BUDGET = 3000
FL_RU_TIMEOUT = 10
FL_RU_USER_AGENT = "Mozilla/5.0"
FL_RU_MIN_ORDERS_PER_PAGE = 20
PROFI_RU_PAGES = 3
PROFI_RU_HEADLESS = get_bool_env("PROFI_RU_HEADLESS", False)
PROFI_RU_STORAGE_STATE = os.getenv(
    "PROFI_RU_STORAGE_STATE",
    "playwright_auth/profi_storage_state.json",
)
FL_RU_CONCURRENCY_LIMIT = 2
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
TELEGRAM_QUEUE_NAME = "queue:telegram"
TELEGRAM_FAILED_QUEUE_NAME = "queue:telegram:failed"
TELEGRAM_DELAYED_QUEUE_NAME = "queue:telegram:delayed"
TELEGRAM_RETRY_BASE_DELAY = 5
REDIS_SOCKET_TIMEOUT = 15
REDIS_BRPOP_TIMEOUT = 2
