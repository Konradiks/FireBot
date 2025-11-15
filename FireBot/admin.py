from django.contrib import admin
from .models import IPLists
from dashboard.models import Settings

# Register your models here.
admin.site.register(IPLists)
admin.site.register(Settings)