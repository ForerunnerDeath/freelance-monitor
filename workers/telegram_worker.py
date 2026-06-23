import time
import json
import redis
import config

from tasks.telegram_tasks import send_telegram_for_order_task


connect = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    decode_responses=True,
    socket_timeout=config.REDIS_SOCKET_TIMEOUT,
)


def process_task(task_json):
    task_data = json.loads(task_json)
    task_name = task_data["task_name"]
    payload = task_data["payload"]

    if task_name == "send_telegram_for_order":
        return send_telegram_for_order_task(**payload)
    
    raise ValueError(f"Unknown task: {task_name}")


def main():
    while True:
        move_ready_delayed_tasks()
        result = connect.brpop(config.TELEGRAM_QUEUE_NAME, timeout=config.REDIS_BRPOP_TIMEOUT)
        if result is None:
            print("No tasks, waiting...")
            continue

        queue_name, task_json = result
        print(f"Got task from queue: {queue_name}")

        try:
            task_result = process_task(task_json)
            print(f"Task completed: {task_result}")
        except Exception as error:
            handle_task_error(task_json, error)


def handle_task_error(task_json, error):
    task_data = json.loads(task_json)
    task_data["attempts"] += 1
    task_data["last_error"] = str(error)

    if task_data["attempts"] < task_data["max_attempts"]:
        schedule_retry(task_data)
        return
    task_data.pop("retry_at", None)
    task_json = json.dumps(task_data)
    connect.rpush(config.TELEGRAM_FAILED_QUEUE_NAME, task_json)
    print("Task failed permanently, moved to failed queue")


def schedule_retry(task_data):
    delay_seconds = config.TELEGRAM_RETRY_BASE_DELAY * (
        2 ** (task_data["attempts"] - 1)
    )
    retry_at = time.time() + delay_seconds
    task_data["retry_at"] = retry_at

    task_json = json.dumps(task_data)
    connect.zadd(config.TELEGRAM_DELAYED_QUEUE_NAME, {task_json: retry_at})

    print(
        f"Task scheduled for retry in {delay_seconds} seconds. "
        f"Attempt {task_data['attempts']}"
    )


def move_ready_delayed_tasks():
    now = time.time()

    ready_tasks = connect.zrangebyscore(
        config.TELEGRAM_DELAYED_QUEUE_NAME,
        0,
        now,
    )
    for task_json in ready_tasks:
        connect.zrem(config.TELEGRAM_DELAYED_QUEUE_NAME, task_json)
        connect.rpush(config.TELEGRAM_QUEUE_NAME, task_json)
        print("Moved delayed task back to queue")


if __name__ == "__main__":
    main()
