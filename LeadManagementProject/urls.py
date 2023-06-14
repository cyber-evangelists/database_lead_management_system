from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from LeadManagementApp import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('users/', views.users, name='users'),

    path('upload/', views.upload, name='upload'),

    path('logs/', views.logs, name='logs'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
