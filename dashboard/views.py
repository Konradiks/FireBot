from django.shortcuts import render

def dashboardMain(request):
    return render(request, 'dashboard/main.html')