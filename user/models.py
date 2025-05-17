from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.symbol

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favourite_stocks = models.ManyToManyField(Stock, blank=True, related_name='fans')

    def __str__(self):
        return f"{self.user.username}'s profile"