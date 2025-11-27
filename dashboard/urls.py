from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_Main, name="dashboard"),
    path('statistics/', views.statistics_page, name="statistics"),
    path('mode/', views.mode_page, name="mode"),
    path('blacklist/', views.blacklist_page, name="blacklist"),
    path('whitelist/', views.whitelist_page, name="whitelist"),
    path('settings/', views.settings_page, name="settings"),
    path('blocked/', views.blocked_view, name="blocked"),
    path('gen_block_command/', views.gen_block_command, name="gen_block_command"),
    path('gen_unblock_command/', views.gen_unblock_command, name="gen_unblock_command"),

]

