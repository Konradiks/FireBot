import socket
import time
import random
import ipaddress
from datetime import datetime, timedelta


def send_threat_log(src_ip: str, count: int, now=datetime.now(), syslog_server: str = "192.168.1.102", syslog_port: int = 514,
                    dst_ip: str = "0.0.0.0", device_name: str = "pwr-test-fw-1", thread: str = 'brute-force',
                    location: str = "Poland") -> tuple[bool, str]:
    """Generuje i wysyła pojedynczy log THREAT przez UDP.

    Args:
        src_ip: adres źródłowy, który ma się pojawić w logu
        count: wartość repeat_count używana w logu
        syslog_server: host docelowy (syslog server)
        syslog_port: port UDP
        dst_ip: adres docelowy użyty w logu
        device_name: nazwa urządzenia w logu
        thread: typ w polu threat (np. 'brute-force')

    Returns:
        (success, message) — success True gdy wysłano, message z informacją lub błędem
    """

    # now = datetime.now()
    syslog_timestamp = now.strftime("%Y/%m/%d %H:%M:%S")
    event_time_dt = now + timedelta(seconds=5)
    event_time = event_time_dt.strftime("%Y/%m/%d %H:%M:%S")

    log = (
        f"{syslog_timestamp} {device_name} 1,{event_time},026901003422,THREAT,vulnerability,2817,"
        f"{event_time},{src_ip},{dst_ip},{src_ip},{dst_ip},GlobalProtect,,,web-browsing,vsys1,"
        f"pwrnet,pwrnet,ae2.1105,loopback.8,testLogForward,{event_time},1364489,{str(count)},39807,443,39807,"
        "20077,0x1402000,tcp,reset-both,login.esp,"
        "Palo Alto Networks GlobalProtect Authentication Brute Force Attempt(40017),any,medium,"
        f"client-to-server,7480298811480622218,0x0,{location},{location},,,0,,,4,,,,,,,,0,0,0,0,0,,"
        f"{device_name},,,,,0,,0,,N/A,{thread},AppThreat-9036-9738,0x0,0,4294967295,,,"
        "dd610301-4de7-40e4-b184-fc8ddde522bd,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0,"
        f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.000+01:00,,,,internet-utility,general-internet,browser-based,4,,,"
        "web-browsing,no,no,,,NonProxyTraffic"
    )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(log.encode("utf-8"), (syslog_server, syslog_port))
        sock.close()
        return True, "Syslog THREAT został wysłany.", log
    except Exception as e:
        return False, f"Wystąpił błąd podczas wysyłania: {e}"



def send_random_threats(
    subnet: str = "192.168.64.0/24",
    iterations: int | None = None,
    min_sleep: int = 0,
    max_sleep: int = 0.01,
    min_count: int = 1,
    max_count: int = 70,
    syslog_server: str = "127.0.0.1",
    syslog_port: int = 514,
    device_name: str = "pwr-test-fw-1",
    thread: str = 'brute-force',
    location: str = "Poland",
):
    """Wysyła logi THREAT z losowymi adresami IP z podanej sieci.

    Args:
        subnet: CIDR sieci, z której losowane będą adresy (np. '192.168.64.0/24')
        iterations: ile logów wysłać; jeśli None → działaj w pętli nieskończonej
        min_sleep/max_sleep: losowy czas oczekiwania w sekundach między logami
        min_count/max_count: zakres losowej wartości repeat_count
        syslog_server/syslog_port: adres i port serwera syslog
        device_name: nazwa urządzenia umieszczona w logu
        thread: wartość pola threat (np. 'brute-force')
        location: wartość pola location/source country

    Funkcja zwraca po zakończeniu liczbę wysłanych logów.
    """

    net = ipaddress.ip_network(subnet)
    num_hosts = net.num_addresses
    sent = 0
    now = datetime.now() - timedelta(hours=2)
    try:
        i = 0
        while True:
            if iterations is not None and i >= iterations:
                break

            if num_hosts <= 2:
                src_ip = str(net.network_address)
            else:

                offset = random.randint(1, num_hosts - 2)
                src_ip = str(ipaddress.ip_address(int(net.network_address) + offset))

            count = random.randint(min_count, max_count)
            now += timedelta(minutes=1)


            ok, msg = send_threat_log(src_ip, count, now=now, syslog_server=syslog_server, syslog_port=syslog_port,
                                      dst_ip="156.17.134.8", device_name=device_name, thread=thread,
                                      location=location)
            if ok:
                sent += 1
                print(f"[{sent}] Wysłano log z {src_ip} count={count}")
            else:
                print(f"Błąd wysyłki dla {src_ip}: {msg}")

            i += 1

            sleep_for = random.uniform(min_sleep, max_sleep)
            print(f"Oczekiwanie {sleep_for:.1f}s przed kolejnym logiem...")
            time.sleep(sleep_for)

    except KeyboardInterrupt:
        print("Przerwano przez użytkownika")

    return sent

if __name__ == '__main__':
    ok, msg, log = send_threat_log('8.8.8.12', 20, location="Test", syslog_server="192.168.1.100")
    print(msg)
    print(log)
    #send_random_threats(syslog_server="127.0.0.1", location="Test", subnet='172.21.37.0/26')

