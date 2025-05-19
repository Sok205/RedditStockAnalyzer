import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import nltk

#TODO: Make the model more accurate
#TODO: Add more information to be displayed
class MlSentimentAnalyzer:
    def __init__(self):
        """
        self.sia - an instance of SentimentIntensityAnalyzer for sentiment analysis
        self.vectorizer - an instance of TfidfVectorizer for text vectorization
        self.classifier - an instance of RandomForestClassifier for classification
        self.stop_words - a set of English stop words for text preprocessing
        self.quality_threshold - a threshold for quality classification
        :return: None
        """
        self.sia = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.stop_words = set(stopwords.words('english'))
        self.quality_threshold = 0.5


    def preprocess(self, text):
        """
        Preprocess the text by removing special characters, stop words, and tokenizing
        :param text: Text to be preprocessed
        :return: List of tokens
        """
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in self.stop_words]
        return ' '.join(tokens)

    def calculate_quality(self, post):
        """
        Calculate quality of the post
        :param post:
        :return:
        """
        qs = 0

        if len(post['text']) > 100:
            qs += 0.25

        if post['score'] > 10:
            qs += 0.25

        sentiment_scores = self.sia.polarity_scores(post['text'])
        qs += abs(sentiment_scores['compound']) * 0.5
        return qs

    def filter_posts(self, posts_df):
        """
        Filter posts based on quality
        :param posts_df: List of posts
        :return: Filtered list of posts
        """
        posts_df['quality_score'] = posts_df.apply(self.calculate_quality, axis=1)
        return posts_df[posts_df['quality_score'] > self.quality_threshold]

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the text
        :param text: Text to be analyzed
        :return: Sentiment score
        """
        vader_sentiment = self.sia.polarity_scores(text)

        text_length = min(1000, len(text))
        word_count = len(text.split())
        has_question = 1 if '?' in text else 0
        has_exclamation = 1 if '!' in text else 0

        sentiment_score = (
                vader_sentiment['compound'] * 0.7 +
                (text_length / 1000) * 0.1 +
                (has_question * -0.1) +
                (has_exclamation * 0.1)
        )
        return sentiment_score

    def analyze_trend(self, posts_df, window_size=7):
        """
        Analyze trend of the posts
        :param posts_df: List of posts
        :param window_size: Size of the window for trend analysis
        :return: Trend score
        """

        if len(posts_df) == 0:
            return {
                'trend':'Neutral',
                'daily_sentiment': pd.Series(),
                'moving_average': pd.Series(),
                'current_sentiment': 0
            }

        posts_df['date'] = pd.to_datetime(posts_df['created_utc'])
        posts_df.set_index('date', inplace=True)

        daily_sentiment = posts_df['sentiment'].resample('D').mean()

        moving_avg = daily_sentiment.rolling(window=window_size).mean()

        trend = 'Neutral'
        if len(moving_avg) > 0:
            if moving_avg.iloc[-1] > 0.2:
                trend = 'Bullish'
            elif moving_avg.iloc[-1] < -0.2:
                trend = 'Bearish'

        return {
            'trend': trend,
            'daily_sentiment': daily_sentiment,
            'moving_avg': moving_avg,
            'current_sentiment': moving_avg.iloc[-1] if len(moving_avg) > 0 else 0
        }