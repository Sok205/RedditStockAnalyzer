"""
user/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Stock, UserProfile
from django.contrib.auth.models import User
def register(request):
    """
    Handles user registration.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    """
    Handles user login.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """
    Handles user logout.
    :param request:
    :return:
    """
    logout(request)
    return redirect('home')

@login_required
def add_favourite_stock(request, symbol):
    stock, _ = Stock.objects.get_or_create(symbol=symbol.upper())
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.favourite_stocks.add(stock)
    return redirect('profile')

@login_required
def add_favourite_stock_by_form(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip()
        if symbol:
            return add_favourite_stock(request, symbol)

@login_required
def remove_favourite_stock(request, symbol):
    stock = get_object_or_404(Stock, symbol=symbol.upper())
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.favourite_stocks.remove(stock)
    return redirect('profile')

@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    favourites = profile.favourite_stocks.all()
    return render(request, 'user/profile.html', {'favourites': favourites})

@login_required
def user_profile_by_id(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    favourites = profile.favourite_stocks.all()
    return render(request, 'user/profile.html', {'favourites': favourites, 'profile_user': user})

