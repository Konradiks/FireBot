import queue
import random
import socket
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
        self.daemon = True

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
        self.ip = None
        self.port = None
        self.UDPServer = None
        self.buffer = 4096

    def update_data(self, ip: ipaddress.IPv4Address | None = None,
                    port: int | None = None):

        if ip is not None:
            try:
                self.ip = ipaddress.ip_address(ip)
            except ValueError:
                print(f"[{self.name}] Invalid IP address: {ip}")

        if port is not None:
            try:
                port = int(port)
                if 0 <= port <= 65535:
                    self.port = port
                else:
                    print(f"[{self.name}] Port out of range: {port}")
            except (TypeError, ValueError):
                print(f"[{self.name}] Invalid port value: {port}")

    def open_udp_server(self):
        if self.ip is not None and self.port is not None:
            self.UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPServer.bind((self.ip, self.port))


    def loop(self):
        data, addr = self.UDPServer.recvfrom(self.buffer)
        print("Received data from %s:%d" % (addr[0], addr[1]), end=" ")
        mess = data.decode().strip()
        print(data)
        print("Message: '" + mess + '"')
        print(type(data.decode()))
        time.sleep(1)


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
