import subprocess
import sys
from database import SessionLocal
from services.order_service import requeue_unsent_telegram_orders


def run_recovery_once():
    with SessionLocal() as session:
        result = requeue_unsent_telegram_orders(session)

    print(f"Telegram recovery: {result}")


def main():
    run_recovery_once()
    worker_process = subprocess.Popen(
        [sys.executable, "-m", "workers.telegram_worker"]
    )

    try:
        main_process = subprocess.Popen(
            [sys.executable, "main.py", "watch"]
        )

        main_process.wait()

    except KeyboardInterrupt:
        print("Stopping app...")

    finally:
        worker_process.terminate()

        try:
            worker_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_process.kill()


if __name__ == "__main__":
    main()
