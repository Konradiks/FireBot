from ipaddress import ip_network
from django.contrib import messages
from django.shortcuts import redirect
from django.db import IntegrityError
from .models import IPLists

def parse_network(address_str, mask_str, list_type, request):
    if not address_str:
        messages.error(request, "Nie podano adresu IP.")
        return None

    if not mask_str or not (0 <= int(mask_str) <= 32):
        messages.error(request, "Podano złą maskę sieci")
        return None

    network_str = f"{address_str}/{mask_str}"
    try:
        network = ip_network(network_str)
    except ValueError:
        messages.error(request, "Niepoprawny adres IP.")
        return None

    return network

def check_network_exists(network, request, list_type):
    existing = IPLists.objects.filter(network=network).first()
    if existing:
        messages.warning(request, f"Sieć {network} już istnieje na liście {existing.list_type}.")
        return True
    return False

def create_iplist_entry(list_type, network, comment, request):
    add_bl = IPLists()
    add_bl.network = network

    if list_type not in ("blacklist", "whitelist"):
        messages.warning(request, f'Niepoprawna nazwa listy')
        return None

    add_bl.list_type = list_type.upper()
    if comment:
        add_bl.comment = comment

    try:
        add_bl.save()
        messages.success(request, f"Sieć {network} została dodana do listy {list_type}.")
    except IntegrityError:
        messages.error(request, "Błąd bazy danych – nie udało się zapisać sieci.")
        return None

    return add_bl