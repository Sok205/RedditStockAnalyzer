from django.contrib import admin
from django.urls import path, include
from user import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login')
]