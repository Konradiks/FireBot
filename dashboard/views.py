from django.shortcuts import render, redirect

def dashboard_Main(request):
    return redirect('/dashboard/statistics/')

def banned_page(request):
    return render(request, 'dashboard/blacklist.html')

def excluded_page(request):
    return render(request, 'dashboard/white_list.html')

def mode_page(request):
    return render(request, 'dashboard/mode.html')

def settings_page(request):
    return render(request, 'dashboard/settings.html')

def statistics_page(request):
    return render(request, 'dashboard/statistics.html')
