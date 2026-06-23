import subprocess
import sys


def main():
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
