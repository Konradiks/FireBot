from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_Main, name="dashboard"),
    path('statistics/', views.statistics_page, name="statistics"),
    path('mode/', views.mode_page, name="mode"),
    path('blacklist/', views.blacklist_page, name="blacklist"),
    path('whitelist/', views.excluded_page, name="whitelist"),
    path('settings/', views.settings_page, name="settings"),
    path('blacklist/delete/<int:id>/', views.delete_ip, name='delete_ip'),
]

