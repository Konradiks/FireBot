from django import forms
from .models import Settings
import re

class SettingsForm2(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            "bot_frequency",
            "failed_attempts_limit",
            "reset_attempts_time",
            "block_duration_1",
            "block_duration_2",
            "block_duration_3",
            "permanent_block",
            "whitelist_enabled",
            "log_server_ip",
            "log_server_port",
        ]
        labels = {
            "bot_frequency": "Częstotliwość działania bota",
            "failed_attempts_limit": "Ilość nieudanych prób logowania przed zablokowaniem",
            "reset_attempts_time": "Czas po którym resetuje się liczba nieudanych prób",
            "block_duration_1": "Czas trwania 1. blokady",
            "block_duration_2": "Czas trwania 2. blokady",
            "block_duration_3": "Czas trwania 3. blokady",
            "permanent_block": "Czy stosować permanentną blokadę po 4. naruszeniu?",
            "whitelist_enabled": "Czy włączyć listę dozwolonych adresów (whitelist)?",
            "log_server_ip": "Adres IP nasłuchiwania logów",
            "log_server_port": "Port nasłuchiwania logów",
        }
        help_texts = {
            "bot_frequency": "Jak często bot ma się uruchamiać (np. co 5 minut: 0:05:00).",
            "failed_attempts_limit": "Po tylu błędnych próbach adres IP zostanie zablokowany.",
            "reset_attempts_time": "Po tym czasie bez prób, liczba błędnych logowań zostanie wyzerowana.",
            "block_duration_1": "Czas trwania pierwszej blokady IP. Można podać dni: HH:MM:SS lub D HH:MM:SS",
            "block_duration_2": "Czas trwania drugiej blokady IP. Można podać dni: HH:MM:SS lub D HH:MM:SS",
            "block_duration_3": "Czas trwania trzeciej blokady IP. Można podać dni: HH:MM:SS lub D HH:MM:SS",
            "whitelist_enabled": "Adresy z whitelist nie będą blokowane.",
            "log_server_ip": "Adres IP z którego wysyłane są logi do Firebota",
            "log_server_port": "Numer portu na który serwer wysyła logi do Firebota",
        }
        widgets = {
            "bot_frequency": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "reset_attempts_time": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "block_duration_1": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "block_duration_2": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "block_duration_3": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "log_server_ip": forms.TextInput(attrs={
                "pattern": r"^(\d{1,3}\.){3}\d{1,3}$",
                "title": "Adres IPv4, np. 192.168.0.1"
            }),
            "log_server_port": forms.NumberInput(attrs={
                "min": 1,
                "max": 65535
            }),
        }

    def clean_duration_field(self, field_name):
        """Walidacja formatu DurationField z opcjonalnymi dniami."""
        value = self.cleaned_data.get(field_name)
        if isinstance(value, str):
            if not re.match(r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$", value):
                raise forms.ValidationError("Niepoprawny format czasu. Użyj HH:MM:SS lub D HH:MM:SS")
        return value

    def clean_bot_frequency(self):
        return self.clean_duration_field("bot_frequency")

    def clean_reset_attempts_time(self):
        return self.clean_duration_field("reset_attempts_time")

    def clean_block_duration_1(self):
        return self.clean_duration_field("block_duration_1")

    def clean_block_duration_2(self):
        return self.clean_duration_field("block_duration_2")

    def clean_block_duration_3(self):
        return self.clean_duration_field("block_duration_3")
