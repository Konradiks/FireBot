from django.shortcuts import render, redirect
from FireBot.models import IPLists
from django.contrib.auth.decorators import login_required
from . import forms


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
    return render(request, 'dashboard/mode.html')

@login_required
def settings_page(request):
    form = forms.SettingsForm()
    return render(request, 'dashboard/settings.html', {'form': form})

@login_required
def statistics_page(request):

    return render(request, 'dashboard/statistics.html')



