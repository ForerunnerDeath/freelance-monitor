# freelance-monitor

![Tests](https://github.com/ForerunnerDeath/freelance-monitor/actions/workflows/tests.yml/badge.svg)

`freelance-monitor` - практический Python Backend/Automation проект для мониторинга заказов с фриланс-площадок.

Проект собирает заказы из источников, фильтрует их по степени интересности, сохраняет в PostgreSQL, отправляет подходящие заказы в Telegram через Redis-очередь и предоставляет FastAPI API для просмотра заказов и статистики.

## Возможности

- Парсинг заказов с FL.ru.
- Авторизованный источник Profi.ru через Playwright, Docker/VNC login flow и persistent browser profile.
- Фильтрация заказов по статусам:
  - `matched` - подходящие заказы;
  - `risky` - потенциально интересные заказы, требующие ручной проверки;
  - `rejected` - неподходящие заказы.
- Сохранение заказов в PostgreSQL через SQLAlchemy ORM.
- Защита от дублей через `UNIQUE(source, external_id)`.
- Очередь Telegram-уведомлений через Redis.
- Отдельный Telegram worker с retry/backoff и failed queue.
- FastAPI API для заказов и статистики.
- Docker Compose запуск всей системы: PostgreSQL, Redis, API, worker и monitor.
- Pytest-тесты для фильтров и API.

## Архитектура

Основной pipeline:

```text
FL.ru / Profi.ru
        |
        v
     monitor
        |
        v
   PostgreSQL
        |
        v
   Redis queue
        |
        v
 Telegram worker
        |
        v
     Telegram
```

Параллельно работает API:

```text
FastAPI API -> PostgreSQL -> /health, /stats, /orders
```

## API endpoints

FastAPI API используется для диагностики сервиса, просмотра заказов и работы со статусами.

| Method | Endpoint | Назначение |
| --- | --- | --- |
| `GET` | `/health` | Проверить, что API работает |
| `GET` | `/stats` | Получить статистику по заказам |
| `GET` | `/orders` | Получить список заказов |
| `GET` | `/orders?status=matched` | Получить заказы с фильтром по статусу |
| `GET` | `/orders/{source}/{external_id}` | Получить конкретный заказ по источнику и внешнему ID |
| `PATCH` | `/orders/{source}/{external_id}` | Обновить поля заказа, например `contacted` |

В API используется REST-подход: `GET` для чтения данных, `PATCH` для частичного обновления заказа, query params для фильтрации списка и path params для обращения к конкретному заказу.

Подробная интерактивная документация доступна после запуска проекта:

```text
http://127.0.0.1:8000/docs
```

## Сервисы Docker Compose

| Сервис | Назначение |
| --- | --- |
| `postgres` | PostgreSQL база данных для заказов и миграций Alembic |
| `redis` | Redis broker для очередей Telegram-задач |
| `api` | FastAPI приложение |
| `worker` | Telegram worker, который читает Redis queue и отправляет уведомления |
| `monitor` | Процесс мониторинга, который парсит источники и создаёт задачи в очереди |
| `profi-login` | Вспомогательный сервис для ручной авторизации Profi.ru через браузер в Docker/VNC |

## Стек

- Python 3.14
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Playwright
- httpx
- BeautifulSoup
- pytest
- Docker / Docker Compose

## Быстрый запуск через Docker Compose

### 1. Склонировать репозиторий

```powershell
git clone [<repository-url>](https://github.com/ForerunnerDeath/freelance-monitor.git)
cd freelance-monitor
```

### 2. Создать `.env`

```powershell
Copy-Item .env.example .env
```

Заполните в `.env` реальные Telegram-значения:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 3. Запустить PostgreSQL и Redis

```powershell
docker compose up -d postgres redis
```

### 4. Применить миграции Alembic

```powershell
docker compose run --rm api alembic upgrade head
```

### 5. Запустить сервисы приложения

```powershell
docker compose up -d api worker monitor
```

### 6. Проверить API

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/stats
```

## Авторизация Profi.ru

Источник Profi.ru требует ручной авторизации, потому что заказы доступны только после входа в аккаунт.

Для этого в проекте есть отдельный Docker/VNC login flow:

* `Dockerfile.profi-login` - отдельный Dockerfile для контейнера авторизации;
* `scripts/profi_login_vnc.py` - скрипт запуска браузера для ручного входа;
* `scripts/start_profi_login_vnc.sh` - стартовый скрипт VNC/noVNC окружения;
* `profi-login` service в `docker-compose.yml`.

### Как пройти авторизацию

Запустите сервис авторизации:

```powershell
docker compose up -d profi-login
```

После запуска откройте noVNC в браузере:

```text
http://127.0.0.1:6080
```

В открывшемся браузере вручную войдите в Profi.ru.

После успешной авторизации профиль браузера сохраняется в persistent profile directory, который используется `monitor` для последующего парсинга Profi.ru уже в headless-режиме.

### Проверка Profi.ru после авторизации

После входа можно проверить источник отдельно:

```powershell
docker compose run --rm monitor python -m sources.profi_ru
```

Или проверить общий сбор заказов:

```powershell
docker compose exec monitor python -c "from services.source_service import get_orders; orders = get_orders(verbose=True); print('TOTAL', len(orders)); print('SOURCES', sorted(set(o.get('source') for o in orders))); print({s: sum(1 for o in orders if o.get('source') == s) for s in set(o.get('source') for o in orders)})"
```

### Важные замечания

В `.env.example` источник Profi.ru может быть отключён по умолчанию:

```env
ENABLE_PROFI_RU=false
```

Чтобы включить Profi.ru после авторизации, укажите в `.env`:

```env
ENABLE_PROFI_RU=true
```

## Полезные команды

### Запуск тестов

```powershell
python -m pytest
```

### Проверить статус контейнеров

```powershell
docker compose ps
```

### Посмотреть логи monitor

```powershell
docker compose logs -f monitor
```

### Посмотреть логи worker

```powershell
docker compose logs worker --tail=100
```

### Проверить очереди Redis

```powershell
docker compose exec -T redis redis-cli LLEN queue:telegram
docker compose exec -T redis redis-cli ZCARD queue:telegram:delayed
docker compose exec -T redis redis-cli LLEN queue:telegram:failed
```

### Проверить таблицы PostgreSQL

```powershell
docker compose exec -T postgres psql -U freelance_monitor -d freelance_monitor -c "\dt"
```

### Применить миграции вручную

```powershell
docker compose run --rm api alembic upgrade head
```

## Статус проекта

Это pet-project/portfolio project.

Цель проекта - прокачать практические навыки Python Backend и Automation на реалистичной задаче:

- парсинг и внешние интеграции;
- SQL и ORM;
- FastAPI и REST;
- Redis queues и worker-процессы;
- Docker Compose инфраструктура;
- тестирование и диагностика;
- подготовка проекта к GitHub и портфолио.
