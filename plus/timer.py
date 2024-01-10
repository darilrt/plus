import time

class Timer:
    start_time = 0

    @staticmethod
    def start(func_name: str) -> None:
        print(f"Starting {func_name}")
        Timer.start_time = time.time()

    @staticmethod
    def log(message: str) -> None:
        elapsed = time.time() - Timer.start_time
        print(f"{message} in {elapsed:.2f} seconds")

    @staticmethod
    def log_and_start(message: str) -> None:
        Timer.log(message)
        Timer.start(message)