
from django.urls import path
from stock import views

urlpatterns = [
    path('', views.home, name='home'),
]