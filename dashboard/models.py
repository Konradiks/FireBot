from django.db import models
from datetime import timedelta

class Settings(models.Model):
    bot_frequency = models.DurationField(
        default=timedelta(minutes=2)  
    )

    executor_frequency = models.DurationField(
        default=timedelta(minutes=5)  
    )

    unblock_frequency = models.DurationField(
        default=timedelta(hours=24)  
    )

    failed_attempts_limit = models.IntegerField(
        default=10
    )

    reset_attempts_time = models.DurationField(
        default=timedelta(days=1)  
    )

    block_duration_1 = models.DurationField(
        default=timedelta(days=3)  
    )
    block_duration_2 = models.DurationField(
        default=timedelta(days=7)  
    )
    block_duration_3 = models.DurationField(
        default=timedelta(days=14)  
    )

    block_period_reset_time = models.DurationField(
        default=timedelta(days=30)  
    )

    permanent_block = models.BooleanField(
        default=True
    )

    executor_automated = models.BooleanField(
        default=False
    )

    whitelist_enabled = models.BooleanField(
        default=True
    )

    log_server_ip = models.GenericIPAddressField(
        default="0.0.0.0"
    )

    log_server_port = models.IntegerField(
        default=514
    )

    allowed_log_sources = models.TextField(
        default="",
        help_text="Lista adresów IP, z których dozwolone jest przesyłanie logów, oddzielone przecinkami.",
        blank=True,
        null=True
    )

    firewall_address = models.TextField(
        default="https://0.0.0.0",
        help_text="Adres Zapory sieciowej, np. https://0.0.0.0 lub https://firewall.pl",
        blank=True,
        null=True
    )

    def __str__(self):
        return "Ustawienia systemu"

    def get_allowed_log_sources(self):
        return [ip.strip() for ip in self.allowed_log_sources.split(",") if ip.strip()]
