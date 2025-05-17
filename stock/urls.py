
from django.urls import path
from stock import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reddit_sentiment/', views.reddit_sentiment, name='reddit_sentiment'),
    path('reddit_sentiment_ml/', views.reddit_sentiment_ml_view, name='reddit_sentiment_ml'),
]