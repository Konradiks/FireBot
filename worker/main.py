import random
import threading
import time
import ipaddress
from tkinter.font import names
import datetime

worker_instance = None

class FireWorker(threading.Thread):

    def __init__(self, name="None"):
        super().__init__()
        self.interrupt = False
        self.name = name

    def run(self):
        print("Starting...")
        self.interrupt = False

        while self.interrupt != True:
            ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32 - 1))
            print(f"{datetime.datetime.now()} Zablokowano adres: {ip}")
            time.sleep(1)

    def stop(self):
        print("Stopping...")
        self.interrupt = True

    def getName(self):
        return self.name

class BaseWorker(threading.Thread):
    def __init__(self, name="Worker"):
        super().__init__()
        self._interrupt = threading.Event()
        self.name = name

    def run(self):
        print(f"[{self.name}] Starting...")
        while not self._interrupt.is_set():
            self.loop()       # <- główna metoda, którą nadpisują subclassy
        print(f"[{self.name}] Stopped.")

    def loop(self):
        """Override in subclasses"""
        raise NotImplementedError

    def stop(self):
        print(f"[{self.name}] Stopping...")
        self._interrupt.set()

    def getName(self):
        return self.name

class ActionExecutor(BaseWorker):
    def __init__(self, input_queue=None):
        super().__init__(name='ActionExecutor')
        self.input_queue = input_queue

    def loop(self):
        ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32 - 1))
        print(f"{datetime.datetime.now()} Zablokowano adres: {ip}")
        time.sleep(1)

class LogAnalyzer(BaseWorker):
    def __init__(self):
        super().__init__(name="LogAnalyzer")

    def loop(self):
        print(f"[{self.name}] Found issue!")
        time.sleep(3)


class LogFetcher(BaseWorker):
    def __init__(self):
        super().__init__(name="LogFetcher")

    def loop(self):
        log = f"LOG at {time.time()}"
        print(f"[{self.name}] Fetched log: {log}")
        time.sleep(6)


if __name__ == '__main__':
    # testWorker = FireWorker()
    # testWorker.start()
    # time.sleep(5)
    # print("STOP")
    # testWorker.stop()

    w = ActionExecutor()
    w2 = LogFetcher()
    w3 = LogAnalyzer()

    w.start()
    w2.start()
    w3.start()
    exit(1)
