import socket
import threading
import time
import ipaddress
import datetime
from django.utils import timezone

from FireBot.models import FailedLoginSummary, BlockedAddress
from worker.functions import save_log, get_raw_log, parse_raw_log, is_ip_on_list

worker_instance = None

debug = False
simulate = False


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
    def __init__(
            self,
            unblock_ip_interval,
            failed_attempts_limit,
            block_duration_1,
            block_duration_2,
            block_duration_3,
            block_4_permanently,
            block_period_reset_time,
            automated,
            whitelist,
            name=None,
            sleep_time=datetime.timedelta(minutes=1)
    ):
        if name is None:
            name = "ActionExecutor"

        super().__init__(name=name)

        # -------------------------
        # CONFIG
        # -------------------------
        self.unblock_ip_interval = unblock_ip_interval  # co ile odblokowywać IP
        self.failed_attempts_limit = failed_attempts_limit  # próg failed attempts
        self.sleep_time = sleep_time.total_seconds()
        self.whitelist = whitelist

        # Czas kolejnego odblokowania
        self.next_unblock_time = timezone.localtime()

        # Okna blokad
        self.block_duration_1 = block_duration_1
        self.block_duration_2 = block_duration_2
        self.block_duration_3 = block_duration_3
        self.block_4_permanently = block_4_permanently  # blokada 4 = permanentna?

        # Reset poziomu blokady po X czasie
        self.block_period_reset_time = block_period_reset_time

        # Tryb działania blokera
        self.automated = automated  # jeśli True → automatyczne API
        print(f"[{self.name} Started in automated mode: {self.automated}]")
        self.debug = True  # logging

    # ----------------------------------------------------------------------
    # PODNIESIENIE POZIOMU BLOKADY
    # ----------------------------------------------------------------------

    def increase_blockade(self, threat_blockade: BlockedAddress, now):
        """
        Zwiększa poziom blokady lub resetuje, jeśli minęło 30 dni.
        """
        threat_blockade.start_time = now

        # jeśli end_time jest None (nowy rekord), resetujemy poziom
        if threat_blockade.end_time is None:
            threat_blockade.block_number = 1
            threat_blockade.end_time = now + self.block_duration_1

        # jeśli ostatnia blokada nie jest przedawniona → podbij poziom
        elif threat_blockade.end_time + self.block_period_reset_time > now:


            if threat_blockade.block_number == 1:
                threat_blockade.block_number = 2
                threat_blockade.end_time = now + self.block_duration_2
                threat_blockade.requires_unblock = True

            elif threat_blockade.block_number == 2:
                threat_blockade.block_number = 3
                threat_blockade.end_time = now + self.block_duration_3
                threat_blockade.requires_unblock = True

            elif threat_blockade.block_number == 3:
                if self.block_4_permanently:
                    threat_blockade.block_number = 4
                    threat_blockade.requires_unblock = False
                    # Możesz tu dodać wpis do blacklist
                else:
                    threat_blockade.requires_unblock = True
                    threat_blockade.block_number = 3
                threat_blockade.end_time = now + self.block_duration_3

        # jeśli blokada się przedawniła → reset do poziomu 1
        else:
            threat_blockade.block_number = 1
            threat_blockade.end_time = now + self.block_duration_1

        # ustaw flagi blokady
        threat_blockade.is_blocked = False
        threat_blockade.was_unblocked = False
        threat_blockade.processed = False

        return threat_blockade

        # ----------------------------------------------------------------------
        # ODBLOKOWANIE ADRESÓW
        # ----------------------------------------------------------------------

    def unblock_expired(self, now):
        """
        Zdejmuje blokady, których czas minął.
        """
        to_unblock = BlockedAddress.objects.filter(
            is_blocked=True,
            end_time__lte=now,
            processed=False
        )

        if not to_unblock:
            return



        # for blockade in to_unblock:
        #     print(blockade)
        #     if is_ip_on_list(blockade.address, "Blacklist"):
        #         if self.debug:
        #             print(f"[{self.name}] Address {blockade.address} on whitelist → skipping")
        #         blockade.processed = True
        #         blockade.save(update_fields=["processed"])


        if self.automated:
            print(f"API Call not implemented")
            for entry in to_unblock:
                if is_ip_on_list(entry.address, "Blacklist"):
                    if self.debug:
                        print(f"[{self.name}] Address {entry.address} on Blacklist → skipping")
                    entry.address.processed = True
                    entry.address.save(update_fields=["processed"])
                    continue
                entry.is_blocked = False
                entry.was_unblocked = True
                entry.requires_unblock = False
                entry.processed = True
                entry.save(update_fields=["is_blocked", "was_unblocked", "requires_unblock", "processed"])

        else:
            for entry in to_unblock:
                if is_ip_on_list(entry.address, "Blacklist"):
                    if self.debug:
                        print(f"[{self.name}] Address {entry.address} on Blacklist → skipping")
                    entry.address.processed = True
                    entry.address.save(update_fields=["processed"])
                    continue
                entry.requires_unblock = True
                entry.processed = True
                entry.save(update_fields=["requires_unblock", "processed"])


    def loop(self):
        now = timezone.localtime()

        # ==========================================================
        # 1. ODBLOKOWANIE ADRESÓW (raz na zdefiniowany okres)
        # ==========================================================
        if now >= self.next_unblock_time:
            self.unblock_expired(now)
            self.next_unblock_time = now + self.unblock_ip_interval
            # nie return — chcemy też od razu blokować nowe
            print(f"[{self.name}] Next unblock scheduled at {self.next_unblock_time}")

        # ==========================================================
        # 2. BLOKOWANIE ADRESÓW
        # ==========================================================

        if debug:
            print(f'[{self.name}] Checking if the number of new failed login attempts has exceeded the limits')

        # pobierz adresy z nadmiarową liczbą prób
        threat_ip_list = FailedLoginSummary.objects.filter(
            attempts_count__gt=self.failed_attempts_limit,
            processed=False,

        )
        if not threat_ip_list:
            time.sleep(self.sleep_time)
            return

        for threat in threat_ip_list:
            if debug:
                print(f"[{self.name}] Analyzing Threat: {threat}")

            # jeśli adres na whitelist → pomijamy
            if is_ip_on_list(threat.source_address, "Whitelist"):
                if self.debug:
                    print(f"[{self.name}] Address {threat.source_address} on whitelist → skipping")
                threat.processed = True
                threat.save(update_fields=["processed"])
                continue

            # Pobierz lub utwórz wpis blokady
            threat_blockade, created = BlockedAddress.objects.get_or_create(
                address=threat.source_address,
                defaults={
                    "start_time": now,
                    "block_number": 1,
                    "end_time": now + self.block_duration_1,
                    "is_blocked": False,
                    "requires_unblock": True,
                    "was_unblocked": False,
                    "created_at": now,
                    "processed": False,
                }
            )

            if threat_blockade.was_unblocked != False or True != threat_blockade.requires_unblock:
                pass
            else:
                if debug:
                    print(f'[{self.name}] {threat} was not yet Blocked.')
                threat.processed = True
                threat.save(update_fields=["processed"])
                continue

            if not created and threat_blockade.was_unblocked:
                # podbij poziom blokady
                threat_blockade = self.increase_blockade(threat_blockade, now)
                if debug:
                    print(f'{self.name} increased blockade for {threat.source_address} ')

            # TRYB AUTOMATYCZNY
            if self.automated:
                print(f"[{self.name}] Automatic API call → NOT IMPLEMENTED YET")

            # zapis blokady
            threat_blockade.save()

            # oznacz źródło jako przetworzone i zresetuj licznik
            threat.processed = True
            threat.attempts_count = 0
            threat.save(update_fields=["processed", "attempts_count"])

            # pauza przed kolejną iteracją
        time.sleep(self.sleep_time)


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
        if debug:
            print(f"[{self.name}] Checking for new brute-force logs...")

        from FireBot.models import ThreatLog, FailedLoginSummary
        from django.utils import timezone
        # Pobierz nowe logi brute-force

        reset_delta = self.reset_attempts_time

        now = timezone.localtime()
        if simulate:
            now = timezone.make_aware(datetime.datetime(2025, 11, 8, 12, 22, 44))


        logs = (ThreatLog.objects.filter(
            processed=False,
            threat_category="brute-force")
                .order_by("generated_time"))

        # print("logs", logs)

        if not logs:
            if debug:
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

            summary: FailedLoginSummary = None
            for log in ip_logs:
                if debug:
                    print(f"[{self.name}] Processing {log}, for ip {ip}")
                last_generated_time = log.generated_time
                total_attempts = log.repeat_count

                if summary == None:
                    try:
                        summary = FailedLoginSummary.objects.get(source_address=ip)
                    except FailedLoginSummary.DoesNotExist:
                        # Jeśli nie ma wpisu, tworzymy nowy
                        if debug:
                            print("new failed log")
                        summary = FailedLoginSummary.objects.create(
                            source_address=ip,
                            last_attempt=last_generated_time,
                            attempts_count=total_attempts
                        )
                        continue
                if now - summary.last_attempt > reset_delta:

                    summary.attempts_count = total_attempts
                else:

                    summary.attempts_count += total_attempts


                if summary.last_attempt < last_generated_time:

                    summary.last_attempt = last_generated_time

            summary.processed = False
            summary.save()

            summary: FailedLoginSummary = None

            # Zaznacz logi jako przetworzone (processed=True)
            for log in ip_logs:
                log.processed = True
                log.save(update_fields=['processed'])
            print(f"[{self.name}] New brute-force attempts found and saved.")

        time.sleep(self.sleep_time)

########################################################################################################################
#########                                                                                                      #########
#########                                      LogFetche                                                       #########
#########                                                                                                      #########
########################################################################################################################

class LogFetcher(BaseWorker):
    def __init__(self, ip:ipaddress.IPv4Address=None, port:int=None, allowed_ips=None):
        super().__init__(name="LogFetcher")
        self.ip = ip
        self.port = port
        self.UDPServer = None
        self.buffer = 4096
        self.allowed_ips = allowed_ips
        print(f" allowed ip {allowed_ips}")

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
        if self.allowed_ips != []:
            if str(addr[0]) not in self.allowed_ips:
                print(f"[{self.name}] Not allowed IP address: {addr}")
                return

        if debug:
            print(f"[{self.name}] Received data from %s:%d" % (addr[0], addr[1]), end=" ")
            mess = raw_data.decode().strip()
            # print("Message: '" + mess + "'") # For debugging
        try:
            raw_log = get_raw_log(raw_data)
            if raw_log:
                try:
                    log = parse_raw_log(raw_log)
                    # print("log: " + str(log))
                    if log:
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
