from django.db import models
from datetime import timedelta

class Settings(models.Model):
    bot_frequency = models.DurationField(
        default=timedelta(minutes=3)  # zamiast "0:03:00"
    )

    failed_attempts_limit = models.IntegerField(
        default=5
    )

    reset_attempts_time = models.DurationField(
        default=timedelta(hours=1)  # zamiast "1:00:00"
    )

    block_duration_1 = models.DurationField(
        default=timedelta(minutes=10)  # zamiast "0:10:00"
    )
    block_duration_2 = models.DurationField(
        default=timedelta(hours=1)  # zamiast "1:00:00"
    )
    block_duration_3 = models.DurationField(
        default=timedelta(hours=24)  # zamiast "24:00:00"
    )

    permanent_block = models.BooleanField(
        default=True
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

    def __str__(self):
        return "Ustawienia systemu"
