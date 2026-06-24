import json

import redis

import config

connect = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    decode_responses=True,
)


def enqueue_telegram_notification(source, external_id):
    task = {
        "task_name": "send_telegram_for_order",
        "payload": {
            "source": source,
            "external_id": external_id,
        },
        "attempts": 0,
        "max_attempts": 3,
    }
    task_json = json.dumps(task)
    connect.rpush(config.TELEGRAM_QUEUE_NAME, task_json)
    return {
        "status": "queued",
        "source": source,
        "external_id": external_id,
    }
