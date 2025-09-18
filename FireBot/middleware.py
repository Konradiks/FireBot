import os
import json
from django.shortcuts import redirect
from django.conf import settings

class CheckConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.config_file = os.path.join(settings.BASE_DIR, "config.json")

    def __call__(self, request):
        # sprawdzamy czy plik konfiguracyjny istnieje
        if not os.path.exists(self.config_file):
            if request.path != "/setup/":  # żeby nie zapętlić
                return redirect("/setup/")
        else:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            # sprawdzamy czy konfiguracja jest kompletna
            if not config.get("admin_password") or not config.get("api_key") or not config.get("server_url"):
                if request.path != "/setup/":
                    return redirect("/setup/")

        return self.get_response(request)
