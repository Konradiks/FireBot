from django.db import models


# Create your models here.

class IPLists(models.Model):
    LIST_TYPE_CHOICES = [
        ('WHITELIST', 'Whitelist'),
        ('BLACKLIST', 'Blacklist'),
    ]
    network = models.CharField(max_length=43, unique=True)
    list_type = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES, default='Blacklist')
    comment = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.network} ({self.list_type})"

class ThreatLog(models.Model):
    IP_TYPE_CHOICES = [
        ('WHITELIST', 'Whitelist'),
    ]