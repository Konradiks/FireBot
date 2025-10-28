from django.shortcuts import render, redirect
from FireBot.models import IPLists


def dashboard_Main(request):
    return redirect('/dashboard/statistics/')

def blacklist_page(request):
    blacklist = IPLists.objects.filter(list_type="BLACKLIST")
    return render(request, 'dashboard/blacklist.html', {'blacklist': blacklist})

def whitelist_page(request):
    whitelist = IPLists.objects.filter(list_type="WHITELIST")
    return render(request, 'dashboard/whitelist.html', {'whitelist': whitelist})

def mode_page(request):
    return render(request, 'dashboard/mode.html')

def settings_page(request):
    return render(request, 'dashboard/settings.html')

def statistics_page(request):
    return render(request, 'dashboard/statistics.html')



