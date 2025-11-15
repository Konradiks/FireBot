from django.shortcuts import render, redirect
from FireBot.models import IPLists
from django.contrib.auth.decorators import login_required
from . import forms
from worker import classes as worker_module
from worker.classes import FireWorker
from .models import Settings
from django.contrib import messages

@login_required
def dashboard_Main(request):
    return redirect('/dashboard/statistics/')

@login_required
def blacklist_page(request):
    blacklist = IPLists.objects.filter(list_type="BLACKLIST")
    return render(request, 'dashboard/blacklist.html', {'blacklist': blacklist})

@login_required
def whitelist_page(request):
    whitelist = IPLists.objects.filter(list_type="WHITELIST")
    return render(request, 'dashboard/whitelist.html', {'whitelist': whitelist})

@login_required
def mode_page(request):
    bot_active = worker_module.worker_instance is not None
    return render(request, 'dashboard/mode.html', {'bot_active': bot_active})
@login_required
def settings_page(request):
    # Pobierz pierwszy rekord lub utwórz domyślny
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()

    # Usuń wszystkie inne rekordy
    Settings.objects.exclude(pk=settings.pk).delete()

    if request.method == "POST":
        form = forms.SettingsForm2(request.POST)
        if form.is_valid():
            Settings.objects.all().delete()
            form.save()
            messages.success(request, 'Settings saved.')
            return redirect('/dashboard/settings/')

    if request.method == "GET":
        form = forms.SettingsForm2(instance=settings)
        return render(request, 'dashboard/settings.html', {'form': form})

@login_required
def statistics_page(request):

    return render(request, 'dashboard/statistics.html')



