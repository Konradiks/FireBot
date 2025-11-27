from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
import json
import os
from .functions import *
from django.contrib.auth import login, logout
from .forms import CustomLoginForm


def homePage(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    else:
        return redirect('login')

def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            else:
                return redirect("dashboard:dashboard")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', { "form": form })

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

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

        return redirect("/")

    return render(request, "setup.html")

@login_required
def power_off_worker(request):
    # if worker_module.worker_instance:
    #     worker_module.worker_instance.stop()
    #     worker_module.worker_instance = None
    #     print("Worker stopped")
    # else:
    #     print("No worker instance to stop")
    return redirect('/dashboard/mode')

@login_required
def power_on_worker(request):
    # if worker_module.worker_instance is None:
    #     settings: Settings = get_settings()
    #     if request.method == "POST":
    #         worker_module.worker_instance = ActionExecutor(unblock_ip_interval=datetime.timedelta(seconds=30), failed_attempts_limit = settings.failed_attempts_limit)
    #     else:
    #         worker_module.worker_instance = ActionExecutor(unblock_ip_interval=datetime.timedelta(seconds=30), failed_attempts_limit = settings.failed_attempts_limit)
    #     worker_module.worker_instance.start()
    #     print("Worker started")
    # else:
    #     print("Worker already running")
    return redirect('/dashboard/mode')

@login_required
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

@login_required
def delete_ip(request, list_type, id):
    ip = IPLists.objects.get(id=id)
    ip.delete()
    return redirect(f'/dashboard/{list_type}/')



