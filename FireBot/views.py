from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.conf import settings
from django.db import IntegrityError
import json
import os
from worker.main import FireWorker, worker_instance
from ipaddress import ip_address, ip_network
from django.contrib import messages
from .models import IPLists


def homePage(request):
    return render(request, 'home.html')

def setup_view(request):
    config_path = os.path.join(settings.BASE_DIR, "config.json")

    if request.method == "POST":
        admin_password = request.POST.get("admin_password")
        api_key = request.POST.get("api_key")
        server_url = request.POST.get("server_url")

        config = {
            "admin_password": admin_password,
            "api_key": api_key,
            "server_url": server_url
        }
        with open(config_path, "w") as f:
            json.dump(config, f)

        return redirect("/")  # po zapisaniu konfiguracji wraca na stronę główną

    return render(request, "setup.html")

def logout(request):
    print("Wylogowano")
    return redirect("/")



def power_off_worker(request):
    global worker_instance
    if worker_instance:
        worker_instance.stop()
        worker_instance = None
    return redirect('/dashboard/mode')

def power_on_worker(request):
    global worker_instance
    if worker_instance is None:
        if request.method == "POST":
            print("hello?")
            worker_name = request.POST.get("name")
            print(worker_name)
            worker_instance = FireWorker(worker_name)
            worker_instance.run()
        else:
            worker_instance = FireWorker()
            worker_instance.run()
    return redirect('/dashboard/mode')

def add_address_to_blacklist(request):
    if request.method != "POST":
        messages.error(request, "Nieobsługiwana metoda (użyj POST).")
        return redirect("/dashboard/blacklist/")

    address_str = request.POST.get("address")
    if not address_str:
        messages.error(request, "Nie podano adresu IP.")
        return redirect("/dashboard/blacklist/")

    mask_str = request.POST.get("mask")

    if not mask_str or not (32 >= int(mask_str) >= 0):
        messages.error(request, "Podano złą maskę sieci")
        return redirect("/dashboard/blacklist/")

    network_str = address_str + "/" + mask_str

    try:
        network = ip_network(network_str)
    except ValueError:
        messages.error(request, "Niepoprawny adres IP.")
        return redirect("/dashboard/blacklist/")

    if IPLists.objects.filter(network=network).exists():
        messages.warning(request, f"Sieć {network} już istnieje w bazie.")
        return redirect("/dashboard/blacklist/")

    add_bl = IPLists()
    add_bl.network = network
    add_bl.list_type = 'BLACKLIST'
    if request.POST.get("comment"):
        add_bl.comment = request.POST.get("comment")
    try:
        add_bl.save()
        messages.success(request, f"Sieć {network} została dodana do czarnej listy.")
    except IntegrityError:
        messages.error(request, "Błąd bazy danych – nie udało się zapisać sieci.")
        return redirect("/dashboard/blacklist/")

    messages.success(request, f"Sieć {network} został dodany do czarnej listy.")
    return redirect("/dashboard/blacklist/")

