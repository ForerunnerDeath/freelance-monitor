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


def get_int_env(name, default):
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


ENABLE_FL_RU = get_bool_env("ENABLE_FL_RU", True)
ENABLE_PROFI_RU = get_bool_env("ENABLE_PROFI_RU", True)

FL_RU_PAGES = get_int_env("FL_RU_PAGES", 3)
DEFAULT_INTERVAL = get_int_env("DEFAULT_INTERVAL", 300)
MIN_INTERVAL = get_int_env("MIN_INTERVAL", 60)
MIN_BUDGET = get_int_env("MIN_BUDGET", 3000)

FL_RU_TIMEOUT = get_int_env("FL_RU_TIMEOUT", 10)
FL_RU_USER_AGENT = os.getenv("FL_RU_USER_AGENT", "Mozilla/5.0")
FL_RU_MIN_ORDERS_PER_PAGE = get_int_env("FL_RU_MIN_ORDERS_PER_PAGE", 20)
FL_RU_CONCURRENCY_LIMIT = get_int_env("FL_RU_CONCURRENCY_LIMIT", 2)

PROFI_RU_PAGES = get_int_env("PROFI_RU_PAGES", 3)
PROFI_RU_HEADLESS = get_bool_env("PROFI_RU_HEADLESS", False)

# storage_state - старый режим авторизации через сохранённые cookies/localStorage.
# persistent_profile - новый режим через полноценный профиль браузера Playwright.
PROFI_RU_AUTH_MODE = os.getenv("PROFI_RU_AUTH_MODE", "storage_state")

PROFI_RU_STORAGE_STATE = os.getenv(
    "PROFI_RU_STORAGE_STATE",
    "playwright_auth/profi_storage_state.json",
)

PROFI_RU_PROFILE_DIR = os.getenv(
    "PROFI_RU_PROFILE_DIR",
    "playwright_profiles/profi_ru",
)

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")

# Локально Docker Redis проброшен как 127.0.0.1:6380.
# Внутри Docker Compose это переопределяется на REDIS_HOST=redis, REDIS_PORT=6379.
REDIS_PORT = get_int_env("REDIS_PORT", 6380)

TELEGRAM_QUEUE_NAME = "queue:telegram"
TELEGRAM_FAILED_QUEUE_NAME = "queue:telegram:failed"
TELEGRAM_DELAYED_QUEUE_NAME = "queue:telegram:delayed"

TELEGRAM_RETRY_BASE_DELAY = get_int_env("TELEGRAM_RETRY_BASE_DELAY", 5)
REDIS_SOCKET_TIMEOUT = get_int_env("REDIS_SOCKET_TIMEOUT", 15)
REDIS_BRPOP_TIMEOUT = get_int_env("REDIS_BRPOP_TIMEOUT", 2)
