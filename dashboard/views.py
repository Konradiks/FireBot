from django.shortcuts import render, redirect
from FireBot.models import IPLists


def dashboard_Main(request):
    return redirect('/dashboard/statistics/')

def blacklist_page(request):
    blacklist = IPLists.objects.filter(list_type="BLACKLIST")
    return render(request, 'dashboard/blacklist.html', {'blacklist': blacklist})

def excluded_page(request):
    return render(request, 'dashboard/white_list.html')

def mode_page(request):
    return render(request, 'dashboard/mode.html')

def settings_page(request):
    return render(request, 'dashboard/settings.html')

def statistics_page(request):
    return render(request, 'dashboard/statistics.html')

def delete_ip(request, id):
    ip = IPLists.objects.get(id=id)
    ip.delete()
    return redirect('/dashboard/blacklist/')

