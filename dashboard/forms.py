from django import forms
from .models import Settings
import re

class SettingsForm2(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            # --- Częstotliwość pracy botów ---
            "bot_frequency",
            "executor_frequency",
            "unblock_frequency",

            # --- Limity prób ---
            "failed_attempts_limit",
            "reset_attempts_time",

            # --- Czas trwania kolejnych blokad ---
            "block_duration_1",
            "block_duration_2",
            "block_duration_3",

            # --- Reset poziomu blokady ---
            "block_period_reset_time",

            # --- Tryb działania ---
            "permanent_block",
            "executor_automated",

            # --- Whitelist ---
            "whitelist_enabled",

            # --- Serwer logów ---
            "log_server_ip",
            "log_server_port",
            "allowed_log_sources",

            # --- Firewall ---
            "firewall_address",
        ]

        labels = {
            # Boty
            "bot_frequency": "Częstotliwość działania LogAnalyzera",
            "executor_frequency": "Częstotliwość działania ActionExecutora (sprawdzanie blokad)",
            "unblock_frequency": "Częstotliwość sprawdzania odblokowywania IP",

            # Limity
            "failed_attempts_limit": "Limit nieudanych prób logowania",
            "reset_attempts_time": "Czas resetu licznika prób logowania",

            # Blokady
            "block_duration_1": "Czas trwania 1. blokady IP",
            "block_duration_2": "Czas trwania 2. blokady IP",
            "block_duration_3": "Czas trwania 3. blokady IP",
            "block_period_reset_time": "Czas po którym resetuje się poziom blokady",

            # Tryb
            "permanent_block": "Czy stosować permanentną blokadę (4. poziom)?",
            "executor_automated": "Czy bot ma wykonywać blokowanie automatycznie (API)?",

            # Whitelist
            "whitelist_enabled": "Czy włączyć listę dozwolonych adresów (whitelist)?",

            # Logi
            "log_server_ip": "Adres IP nasłuchiwania logów",
            "log_server_port": "Port nasłuchiwania logów",
            "allowed_log_sources": "Dozwolone źródła logów (IP)",

            # firewall
            "firewall_address": "Adres Zapory sieciowej",
        }

        help_texts = {
            "bot_frequency": "Jak często LogAnalyzer przetwarza nowe logi.",
            "executor_frequency": "Jak często ActionExecutor sprawdza adresy do zablokowania.",
            "unblock_frequency": "Jak często wykonywane jest odblokowywanie IP.",

            "failed_attempts_limit": "Po tylu błędnych próbach adres zostanie zablokowany.",
            "reset_attempts_time": "Czas po którym liczba prób jest resetowana. Format czasu: HH:MM:SS lub D HH:MM:SS",

            "block_duration_1": "Format: HH:MM:SS lub D HH:MM:SS",
            "block_duration_2": "Format: HH:MM:SS lub D HH:MM:SS",
            "block_duration_3": "Format: HH:MM:SS lub D HH:MM:SS",
            "block_period_reset_time": "Po tym czasie poziom blokady wraca do poziomu 1. Format: HH:MM:SS lub D HH:MM:SS",

            "permanent_block": "Jeśli włączone – po 4. naruszeniu blokada jest stała.",
            "executor_automated": "Jeśli True – bot będzie sam wywoływać API.",

            "whitelist_enabled": "Adresy znajdujące się na whitelist nie będą blokowane.",

            "log_server_ip": "Adres IPv4, np. 192.168.0.100",
            "log_server_port": "Port UDP serwera logów (np. 514)",
            "allowed_log_sources": "Podaj listę adresów IP oddzielonych przecinkami (np. '192.168.0.1, 192.168.0.2').",

            "firewall_address": "Adres Zapory sieciowej, np. https://0.0.0.0 lub https://firewall.pl",
        }

        widgets = {
            # Czasowe pola
            "bot_frequency": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "executor_frequency": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),
            "unblock_frequency": forms.TextInput(attrs={
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

            "block_period_reset_time": forms.TextInput(attrs={
                "pattern": r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$",
                "title": "Format czasu: HH:MM:SS lub D HH:MM:SS"
            }),

            # Logi
            "log_server_ip": forms.TextInput(attrs={
                "pattern": r"^(\d{1,3}\.){3}\d{1,3}$",
                "title": "Adres IPv4, np. 192.168.0.1"
            }),
            "log_server_port": forms.NumberInput(attrs={
                "min": 1,
                "max": 65535
            }),
            "firewall_address": forms.TextInput(attrs={
                "placeholder": "https://0.0.0.0",
            }),
            # "allowed_log_sources": forms.Textarea(attrs={
            #     "rows": 2,
            #     "placeholder": "192.168.0.1, 192.168.0.2"
            # }),

        }

    # ----------------------- WALIDATORY -----------------------

    def clean_duration_field(self, field_name):
        """Walidacja formatu DurationField z opcjonalnymi dniami."""
        value = self.cleaned_data.get(field_name)
        if isinstance(value, str):
            if not re.match(r"^(\d+\s)?\d{1,2}:\d{2}:\d{2}$", value):
                raise forms.ValidationError(
                    "Niepoprawny format czasu. Użyj HH:MM:SS lub D HH:MM:SS"
                )
        return value

    def clean_bot_frequency(self):
        return self.clean_duration_field("bot_frequency")

    def clean_executor_frequency(self):
        return self.clean_duration_field("executor_frequency")

    def clean_unblock_frequency(self):
        return self.clean_duration_field("unblock_frequency")

    def clean_reset_attempts_time(self):
        return self.clean_duration_field("reset_attempts_time")

    def clean_block_duration_1(self):
        return self.clean_duration_field("block_duration_1")

    def clean_block_duration_2(self):
        return self.clean_duration_field("block_duration_2")

    def clean_block_duration_3(self):
        return self.clean_duration_field("block_duration_3")

    def clean_block_period_reset_time(self):
        return self.clean_duration_field("block_period_reset_time")
