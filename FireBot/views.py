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
from .functions import *


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

def add_address_to_list(request, list_type):
    if request.method != "POST":
        messages.error(request, "Nieobsługiwana metoda (użyj POST).")
        return redirect(f"/dashboard/{list_type}/")

    address_str = request.POST.get("address")
    mask_str = request.POST.get("mask")
    comment = request.POST.get("comment")

    network = parse_network(address_str, mask_str, list_type, request)
    if not network:
        return redirect(f"/dashboard/{list_type}/")

    if check_network_exists(network, request, list_type):
        return redirect(f"/dashboard/{list_type}/")

    create_iplist_entry(list_type, network, comment, request)
    return redirect(f"/dashboard/{list_type}/")

def delete_ip(request, list_type, id):
    ip = IPLists.objects.get(id=id)
    ip.delete()
    return redirect(f'/dashboard/{list_type}/')

