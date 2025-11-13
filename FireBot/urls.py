"""
URL configuration for FireBot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

APP_NAME = 'FireBot'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', views.login_view, name='login'),
    path('', views.homePage, name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('logout/', views.logout_view, name='logout'),
    # path("setup/", views.setup_view, name="setup"),
    path('power_off/', views.power_off_worker, name="power_off_worker"),
    path('power_on/', views.power_on_worker, name="power_on_worker"),
    path('add-address-to-list/<str:list_type>/', views.add_address_to_list, name="add-address-to-list"),
    path('<str:list_type>/delete/<int:id>/', views.delete_ip, name='delete_ip'),
]
