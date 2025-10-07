import threading
import time
import ipaddress


class FireWorker(threading.Thread):
    def run(self):
        start_ip = ipaddress.IPv4Address("1.0.253.254")
        end_ip = ipaddress.IPv4Address("192.111.55.80")

        while True:
            for ip_int in range(int(start_ip), int(end_ip) + 1, 1177):
                ip = ipaddress.IPv4Address(ip_int)
                print(f"Zablokowano adres: {ip}")
                time.sleep(1)


if __name__ == '__main__':
    testWorker = FireWorker()
    testWorker.start()

