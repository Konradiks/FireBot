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
simulate = True

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
        if debug:
            print(f"[{self.name}] Work done.")

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
    def __init__(self, name=None, sleep_time=60, reset_attempts_time = datetime.timedelta(hours=1)):
        if name is None:
            name = "LogAnalyzer"
        super().__init__(name=name)
        self.sleep_time = sleep_time.total_seconds()
        self.reset_attempts_time = reset_attempts_time

        # if self.sleep_time > 0:
        #     self.reset_time = settings.reset_attempts_time
        # else:
        #     self.reset_time = datetime.timedelta(days=1)

    def loop(self):
        print(f"[{self.name}] Checking for new brute-force logs...")

        from FireBot.models import ThreatLog, FailedLoginSummary
        from django.utils import timezone
        import datetime
        # Pobierz nowe logi brute-force

        reset_delta = self.reset_attempts_time

        now = timezone.now()
        if simulate:
            now = timezone.make_aware(datetime.datetime(2025, 11, 8, 12, 22, 44))

        # print("now", now)
        # print(self.reset_attempts_time)
        # print(self.sleep_time)

        logs = (ThreatLog.objects.filter(
            processed=False,
            threat_category="brute-force")
                .order_by("generated_time"))

        # print("logs", logs)

        if not logs:
            print(f"[{self.name}] No logs found.")
            time.sleep(self.sleep_time)
            return

        logs_by_ip = {}
        for log in logs:
            ip = str(log.source_address)
            if ip not in logs_by_ip:
                logs_by_ip[ip] = []
            logs_by_ip[ip].append(log)

        # Przetwarzanie logów dla każdego IP
        for ip, ip_logs in logs_by_ip.items():
            # last_generated_time = max(log.generated_time for log in ip_logs)
            # total_attempts = sum(log.repeat_count for log in ip_logs)

            for log in ip_logs:
                print(f"[{self.name}] Processing {log}, for ip {ip}")
                last_generated_time = log.generated_time
                total_attempts = log.repeat_count

                try:
                    summary = FailedLoginSummary.objects.get(source_address=ip)
                    print(now - summary.last_attempt, end=" ___ ")
                    print(reset_delta)
                    # Jeśli ostatni log wygenerowany jest starszy niż reset_delta, zresetuj licznik
                    if now - summary.last_attempt > reset_delta:
                        print("num resert")
                        summary.attempts_count = total_attempts
                    else:
                        print("addind")
                        summary.attempts_count += total_attempts
                    #
                    # summary.last_attempt = last_generated_time
                    # summary.save()
                    print(str(summary.last_attempt) + "___"+ str(last_generated_time))
                    if summary.last_attempt < last_generated_time:
                        print("new time")
                        summary.last_attempt = last_generated_time

                except FailedLoginSummary.DoesNotExist:
                    # Jeśli nie ma wpisu, tworzymy nowy
                    print("new failed log")
                    FailedLoginSummary.objects.create(
                        source_address=ip,
                        last_attempt=last_generated_time,
                        attempts_count=total_attempts
                    )

            # Zaznacz logi jako przetworzone (processed=True)
            for log in ip_logs:
                log.processed = True
                log.save(update_fields=['processed'])
        # FailedLogins = FailedLoginSummary.objects.filter(
        #     source_address__in=sus_ip_list
        # )

        # Sprawdzenie czy dany adres już widnieje w bazie
            # w pętli for po logach dla danego adresu
                # jeśli nie utwórz i zapisz w pętli for wszystkie próby ataków od czasu reset_attempts_time wstecz oraz czas
                # ostatniego ataku

                # jeśli isnieje sprawdz czy próba ostatniego logowania nie jest starsza niz aktualna godzina - reset_attempts_time
                # jeśli tak wyzeruj last_attempt i zsumuj do attempts_count wartość repeat_count

                # jeśli czas mieści się w przedziale czasu zsumuj do attempts_count wartość repeat_count

        time.sleep(self.sleep_time * 5)
        # if not logs.exists():
        #     time.sleep(self.sleep_time)
        #     return
        #
        # # Grupowanie logów po adresie źródłowym
        # logs_by_ip = {}
        # for log in logs:
        #     logs_by_ip.setdefault(log.source_address, []).append(log)
        #
        # for ip, events in logs_by_ip.items():
        #     # Suma prób brute-force dla tej iteracji
        #     attempts = sum(event.repeat_count for event in events)
        #
        #     try:
        #         summary = FailedLoginSummary.objects.get(source_address=ip)
        #         time_diff = now - summary.last_attempt
        #
        #         if time_diff <= reset_time:
        #             # Kontynuujemy zliczanie prób
        #             summary.attempts_count += attempts
        #         else:
        #             # Resetujemy — próba zbyt stara
        #             summary.attempts_count = attempts
        #
        #         summary.last_attempt = now
        #         summary.save()
        #
        #     except FailedLoginSummary.DoesNotExist:
        #         # Tworzymy pierwszy wpis dla IP
        #         FailedLoginSummary.objects.create(
        #             source_address=ip,
        #             last_attempt=now,
        #             attempts_count=attempts
        #         )
        #
        #     # Oznaczamy ThreatLog jako przetworzony
        #     ThreatLog.objects.filter(
        #         id__in=[e.id for e in events]
        #     ).update(processed=True)

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

    def update_data_and_restart(self, ip: ipaddress.IPv4Address | None = None,
                    port: int | None = None):

        if ip is not None:
            try:
                self.ip = ipaddress.ip_address(ip)
            except ValueError:
                print(f"[{self.name}] Invalid IP address: {ip}")
                return

        if port is not None:
            try:
                port = int(port)
                if 0 <= port <= 65535:
                    self.port = port
                else:
                    print(f"[{self.name}] Port out of range: {port}")
            except (TypeError, ValueError):
                print(f"[{self.name}] Invalid port value: {port}")
                return

        # if self.UDPServer:
        #     print(f"[{self.name}] Restarting UDP server...")
        #     self.UDPServer.close()
        #     self.UDPServer = None
        #
        # self.open_udp_server()


    def open_udp_server(self):
        if self.UDPServer:
            print(f"[{self.name}] UDPServer listening on {self.port}")
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
            # print(f"[{self.name}] Received data from %s:%d" % (addr[0], addr[1]), end=" ")
            mess = raw_data.decode().strip()
            # print("Message: '" + mess + "'") # For debugging
        try:
            raw_log = get_raw_log(raw_data)
            if raw_log:
                try:
                    log = parse_raw_log(raw_log)
                    # print("log: " + str(log))

                    try:
                        log.save()
                        # if debug:
                            # print(f"[{self.name}] Log saved.")
                    except Exception as e:
                        print(f"[{self.name}] Failed to save log: {e}")

                except Exception as e:
                    print(f"[{self.name}] Failed to parse log: {e}")
            elif debug == True:
                print(f"[{self.name}] No threat log found")

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
