import queue
import random
import socket
import threading
import time
import ipaddress
from tkinter.font import names
import datetime


from worker.functions import save_log, get_raw_log, parse_raw_log

worker_instance = None

debug = True

########################################################################################################################
#########                                                                                                      #########
#########                                      BaseWorker                                                      #########
#########                                                                                                      #########
########################################################################################################################


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

########################################################################################################################
#########                                                                                                      #########
#########                                      ActionExecutor                                                  #########
#########                                                                                                      #########
########################################################################################################################


class ActionExecutor(BaseWorker):
    def __init__(self, name=None):
        if name is None:
            name = "ActionExecutor"
        super().__init__(name=name)

    def loop(self):
        ip = ipaddress.IPv4Address(random.randint(0, 2 ** 32 - 1))
        print(f"{datetime.datetime.now()} Zablokowano adres: {ip}")
        time.sleep(1)

########################################################################################################################
#########                                                                                                      #########
#########                                      LogAnalyzer                                                     #########
#########                                                                                                      #########
########################################################################################################################

class LogAnalyzer(BaseWorker):
    def __init__(self, name=None):
        if name is None:
            name = "LogAnalyzer"
        super().__init__(name=name)

    def loop(self):
        print(f"[{self.name}] Not Yet Implemented")
        time.sleep(30)

########################################################################################################################
#########                                                                                                      #########
#########                                      LogFetche                                                       #########
#########                                                                                                      #########
########################################################################################################################

class LogFetcher(BaseWorker):
    def __init__(self, ip:ipaddress.IPv4Address=None, port:int=None):
        super().__init__(name="LogFetcher")
        self.ip = ip
        self.port = port
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
        if self.UDPServer:
            print(f"[{self.name}] UDPServer już otwarty.")
            return
        if self.ip and self.port:
            try:
                self.UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.UDPServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.UDPServer.bind((self.ip, self.port))
                print(f"[{self.name}] UDPServer open to {self.ip}:{self.port}")
            except socket.error as e:
                print(f"[{self.name}] Failed to bind: {e}")
        else:
            print(f"[{self.name}] No IP and/or Port specified")


    def loop(self):
        raw_data, addr = self.UDPServer.recvfrom(self.buffer)
        if debug:
            print(f"[{self.name}] Received data from %s:%d" % (addr[0], addr[1]), end=" ")
            mess = raw_data.decode().strip()
            print("Message: '" + mess + "'") # For debugging
        try:
            raw_log = get_raw_log(raw_data)

            try:
                log = parse_raw_log(raw_log)
                print("log: " + str(log))

                try:
                    log.save()
                    if debug:
                        print(f"[{self.name}] Log saved.")
                except Exception as e:
                    print(f"[{self.name}] Failed to save log: {e}")

            except Exception as e:
                print(f"[{self.name}] Failed to parse log: {e}")

        except ValueError:
            print(f"[{self.name}] Invalid data received: {raw_data}")





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
