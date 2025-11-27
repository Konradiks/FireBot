from django.contrib import admin
from .models import IPLists, ThreatLog, FailedLoginSummary, BlockedAddress
from dashboard.models import Settings


# Register your models here.
admin.site.register(IPLists)
admin.site.register(ThreatLog)
admin.site.register(FailedLoginSummary)
admin.site.register(BlockedAddress)
admin.site.register(Settings)
