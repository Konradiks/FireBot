from django.shortcuts import render, redirect
from django.conf import settings
import json
import os

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
