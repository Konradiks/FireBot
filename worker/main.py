import random
import threading
import time
import ipaddress
from tkinter.font import names

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
            print(f"Zablokowano adres: {ip}")
            time.sleep(1)

    def stop(self):
        print("Stopping...")
        self.interrupt = True

    def getName(self):
        return self.name




if __name__ == '__main__':
    testWorker = FireWorker()
    testWorker.start()
    time.sleep(5)
    print("STOP")
    testWorker.stop()
