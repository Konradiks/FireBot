from django.contrib import admin
from .models import IPLists, ThreatLog
from dashboard.models import Settings


# Register your models here.
admin.site.register(IPLists)
admin.site.register(ThreatLog)
admin.site.register(Settings)
