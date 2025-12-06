import ipaddress
from datetime import datetime
from io import StringIO
import csv
from FireBot.models import IPLists
from django.utils import timezone


debug = False
debug2 = False

def block_ip_address(address, time):
    return f"Zablokowano"

def save_log(log) -> None:
    """
    Saves a single log entry received from the UDP stream.
    :param data: Raw log message received over UDP
    :return:
    """

def get_raw_log(raw_data):
    """
    Clears the data received from the UDP stream.
    :param raw_data: Raw log message received over UDP
    :return:
    """
    """
    <12>Nov  8 12:08:34 pwr-santoslab-fw-1 1,2025/11/08 12:08:34,026901003422,THREAT,vulnerability,2817,2025/11/08 12:08:34,89.64.3.93,156.17.134.8,89.64.3.93,156.17.134.8,GlobalProtect,,,web-browsing,vsys1,pwrnet,pwrnet,ae2.1105,loopback.8,testLogForward,2025/11/08 12:08:34,1383262,8,39906,443,39906,20077,0x1402000,tcp,reset-both,"login.esp",Palo Alto Networks GlobalProtect Authentication Brute Force Attempt(40017),any,medium,client-to-server,7480298811480622214,0x0,Poland,Poland,,,0,,,23,,,,,,,,0,0,0,0,0,,pwr-santoslab-fw-1,,,,,0,,0,,N/A,brute-force,AppThreat-9036-9738,0x0,0,4294967295,,,dd610301-4de7-40e4-b184-fc8ddde522bd,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,0,2025-11-08T12:08:34.766+01:00,,,,internet-utility,general-internet,browser-based,4,"used-by-malware,able-to-transfer-file,has-known-vulnerability,tunnel-other-application,pervasive-use",,web-browsing,no,no,,,NonProxyTraffic
    """
    data = raw_data.decode('utf-8').strip()
    if not data:
        print("[get_raw_log] No data received")
        return
    raw_logs = csv.reader(StringIO(str(data)))
    raw_log = next(raw_logs)
    try:
        if raw_log[3] == "THREAT": # or raw_log[3] == "TRAFFIC":
            return raw_log
    except IndexError:
        if debug == True:
            print("[get_raw_log] Not log data")
            return


def parse_raw_log(raw_log: list[str]):
    """
    Converts a raw log list into a ThreatLog Django model instance.

    :param raw_log: List of strings representing a CSV row from PAN-OS syslog.
    :return: ThreatLog instance if successful, None if row is invalid.
    """
    from FireBot.models import ThreatLog
    try:
        # Sprawdź, czy to jest log typu THREAT
        if raw_log[3] != "THREAT":
            if debug == True:
                print("[parse_raw_log] Not the THREAT log")
            return None

        # if raw_log[69] != 'brute-force':
        #     if debug == True:
        #         print("[parse_raw_log] Not the brute-force log")
        #     return None
            # Tworzymy instancję modelu
        naive_dt = datetime.strptime(raw_log[6], "%Y/%m/%d %H:%M:%S")

        log = ThreatLog.objects.create(
            generated_time=timezone.make_aware(naive_dt, timezone.get_current_timezone()),
            source_address=raw_log[7],
            destination_address=raw_log[8],
            rule_name=raw_log[11],
            application=raw_log[14],
            repeat_count=int(raw_log[23]),
            destination_port=int(raw_log[25]),
            flags=raw_log[28],
            threat_id=raw_log[32],
            source_location=raw_log[38],
            threat_category=raw_log[69],
            payload_protocol_id=raw_log[73],
        )

        return log

    except (IndexError, ValueError) as e:
        # Niepełny lub niepoprawny wiersz CSV
        print(f"[parse_raw_log] Invalid raw log: {e}")
        return None

def is_ip_on_list(ip, list_type):
    """
    :param ip:
    :param list_type: 'Whitelist' or 'Blacklist'
    :return:
    """
    ip = ipaddress.ip_address(ip)
    network_list: IPLists = IPLists.objects.filter(list_type=list_type.upper())
    for el in network_list:
        network = ipaddress.ip_network(el.network)
        if ip in network:
            return True
    return False
