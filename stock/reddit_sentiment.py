"""
File for Reddit sentiment analysis
"""

import os
import re
from datetime import datetime

import pandas as pd
import praw
from dotenv import load_dotenv
from textblob import TextBlob
import re

load_dotenv()


class RedditSentiment:
    """
    Class to handle Reddit sentiment analysis
    """

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
        )

    def clean_text(self, text):
        """
        Clean the text by removing links, special characters, and extra spaces
        :param text: Text to be cleaned
        :return: Cleaned text
        """
        if not isinstance(text, str):
            return ""

        # Removing links
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Removing mentions and hashtags (whole words)
        text = re.sub(r'@\w+|#\w+', '', text)
        # Removing special characters
        text = re.sub(r'[^A-Za-z0-9\s]', '', text)
        # Removing extra spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def get_sentiment(self, text):
        """
        Get sentiment polarity of the using TextBlob (-1 to 1)
        TextBlob - library for processing textual data
        :param text:
        :return:
        """
        clean_text = self.clean_text(text)
        if not clean_text:
            return 0

        analysis = TextBlob(clean_text)
        return analysis.sentiment.polarity

    def get_reddit_posts(self, stock_symbol, limit=100):
        """
        Fetch Reddit posts for a given stock symbol
        :param stock_symbol: Stock symbol to search for
        :param limit: Number of posts to fetch
        :return: DataFrame with Reddit posts and their sentiment scores
        """
        posts = []

        try:
            # Fetching posts from multiple subreddits
            for post in self.reddit.subreddit(
                            'stocks+investing+wallstreetbets').search(
                            f'{stock_symbol} stock', limit=limit, time_filter='month'):

                full_text = f"{post.title} {post.selftext}"
                sentiment_score = self.get_sentiment(full_text)

                # Only consider posts with a sentiment score
                posts.append({
                    'title': post.title,
                    'text': post.selftext,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'sentiment': sentiment_score,
                    'created_at': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f'https://www.reddit.com{post.permalink}',
                    'subreddit': post.subreddit.display_name,
                })

        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            return pd.DataFrame()

        return pd.DataFrame(posts)

    def analyze_sentiment(self, stock_symbol):
        """
        Analyze sentiment of Reddit posts for a given stock symbol
        :param stock_symbol:
        :return:
        """
        posts_df = self.get_reddit_posts(stock_symbol)

        if len(posts_df) == 0:
            return {
                'success': False,
                'data': None,
                'error': f"No Reddit posts found for {stock_symbol}"
            }

        avg_sentiment = posts_df['sentiment'].mean()

        posts_df["sentiment_category"] = posts_df["sentiment"].apply(
            lambda x: "positive" if x > 0 else ("negative" if x < 0 else "neutral")
        )

        sentiment_count = posts_df["sentiment_category"].value_counts().to_dict()

        top_posts = posts_df.nlargest(5, 'sentiment')[['title', 'sentiment', 'url']]

        return {
            'success': True,
            'data': {
                'average_sentiment': float(avg_sentiment),
                'sentiment_distribution': sentiment_count,
                'posts_count': len(posts_df),
                'top_posts': top_posts.to_dict(orient='records')
            },
            'error': None
        }

