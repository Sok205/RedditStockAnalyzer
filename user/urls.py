from django.contrib import admin
from django.urls import path, include
from user import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/<int:user_id>/', views.user_profile_by_id, name='profile_by_id'),
    path('add_favourite/', views.add_favourite_stock_by_form, name='add_favourite_stock_by_form'),
    path('remove_favourite_stock/<str:symbol>/', views.remove_favourite_stock, name='remove_favourite_stock'),

]