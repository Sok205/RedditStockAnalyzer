"""
Unitests for stock app
"""
import pandas as pd

from unittest.mock import patch, Mock, PropertyMock
from django.test import TestCase
from requests.exceptions import HTTPError, RequestException
from .stock_data import FetchStockData
from .reddit_sentiment import RedditSentiment


class FetchStockDataTests(TestCase):
    """
    Unit tests for the FetchStockData class.
    """
    def setUp(self):
        self.fetcher = FetchStockData()
        self.test_symbol = "AAPL"

    @patch('yfinance.Ticker')
    def test_successful_stock_data_fetch(self, mock_ticker):
        """
        Testing successful stock data fetch
        """

        mock_instance = Mock()
        mock_instance.info = {
            'currentPrice': 150.0,
            'currency': 'USD'
        }
        mock_ticker.return_value = mock_instance

        result = self.fetcher.get_stock_data(self.test_symbol)

        self.assertTrue(result['success'])
        self.assertIsNone(result['error'])
        self.assertEqual(result['data']['current_price'], 150.0)
        self.assertEqual(result['data']['currency'], 'USD')

    @patch('yfinance.Ticker')
    def test_missing_current_price(self, mock_ticker):
        """
        Testing handling of missing current price
        """

        mock_instance = Mock()
        mock_instance.info = {
            'currency': 'USD'
        }
        mock_ticker.return_value = mock_instance

        result = self.fetcher.get_stock_data(self.test_symbol)

        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertEqual(
            result['error'],
            f"Current price for {self.test_symbol} is not available"
        )

    @patch('yfinance.Ticker')
    def test_rate_limit_error(self, mock_ticker):
        """
        Testing handling of rate limit errors
        :param mock_ticker:
        """

        mock_response = Mock()
        mock_response.status_code = 429
        http_error = HTTPError(response=mock_response)

        info_property = PropertyMock(side_effect=http_error)
        type(mock_ticker.return_value).info = info_property

        result = self.fetcher.get_stock_data(self.test_symbol, max_tries=2, delay=0)

        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertEqual(result['error'], "Rate limit exceeded. Try again later")

    @patch('yfinance.Ticker')
    def test_network_error(self, mock_ticker):
        """Testing handling of general network errors"""
        info_property = PropertyMock(side_effect=RequestException("Network error"))
        type(mock_ticker.return_value).info = info_property

        result = self.fetcher.get_stock_data(self.test_symbol)

        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertEqual(
            result['error'],
            f"Failed to fetch stock data for {self.test_symbol}"
        )

    @patch('time.sleep')
    @patch('yfinance.Ticker')
    def test_retry_mechanism(self, mock_ticker, mock_sleep):
        """
        Testing the retry mechanism when a rate limit error occurs.
        :param mock_ticker:
        :param mock_sleep:
        :return:
        """
        mock_response = Mock()
        mock_response.status_code = 429
        http_error = HTTPError(response=mock_response)

        info_property = PropertyMock(side_effect=[
            http_error,
            {'currentPrice': 150.0, 'currency': 'USD'}
        ])
        type(mock_ticker.return_value).info = info_property

        result = self.fetcher.get_stock_data(self.test_symbol, max_tries=2, delay=1)

        self.assertTrue(result['success'])
        self.assertIsNone(result['error'])
        self.assertEqual(result['data']['current_price'], 150.0)
        mock_sleep.assert_called_once_with(1)


class RedditSentimentTests(TestCase):
    """Unit tests for RedditSentiment class"""

    def setUp(self):
        self.sentiment = RedditSentiment()

    def test_clean_text(self):
        """Test text cleaning functionality"""
        # Test cases
        test_cases = {
            "Normal text": ("Hello World!", "Hello World"),
            "Text with link": ("Check this https://example.com", "Check this "),
            "Text with special chars": ("Hello @user #tag", "Hello  "),
            "Text with numbers": ("Price is $123.45", "Price is 12345"),
            "Non-string input": (123, ""),
            "Empty string": ("", ""),
        }

        for case_name, (input_text, expected) in test_cases.items():
            with self.subTest(case=case_name):
                result = self.sentiment.clean_text(input_text)
                self.assertEqual(result.strip(), expected.strip())

    def test_get_sentiment(self):
        """
        Test sentiment analysis
        """

        test_cases = {
            "Positive": ("This is great!", 1),
            "Negative": ("This is terrible!", -1),
            "Neutral": ("It is a day.", 0),
            "Empty": ("", 0),
            "Non-string": (123, 0)
        }

        def get_category(score):
            if score > 0:
                return "positive"
            elif score < 0:
                return "negative"
            else:
                return "neutral"

        for case_name, (input_text, expected_polarity) in test_cases.items():
            with self.subTest(case=case_name):
                sentiment = self.sentiment.get_sentiment(input_text)
                self.assertEqual(
                    get_category(sentiment),
                    get_category(expected_polarity)
                )
    @patch('praw.Reddit')
    def test_get_reddit_posts(self, mock_reddit):
        """Test fetching Reddit posts"""
        # Mock Reddit post
        mock_post = Mock()
        mock_post.title = "Test Post"
        mock_post.selftext = "Test Content"
        mock_post.created_utc = 1234567890
        mock_post.permalink = "/r/stocks/comments/test"
        mock_post.subreddit.display_name = "stocks"

        # Mock the search method
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = [mock_post]
        mock_reddit.return_value.subreddit.return_value = mock_subreddit

        result = self.sentiment.get_reddit_posts("AAPL", limit=1)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertTrue('title' in result.columns)
        self.assertTrue('sentiment' in result.columns)

    @patch('praw.Reddit')
    def test_analyze_sentiment_success(self, mock_reddit):
        """Test successful sentiment analysis"""
        # Mock posts data
        mock_posts = pd.DataFrame({
            'title': ['Good news!', 'Bad news'],
            'sentiment': [0.5, -0.5],
            'url': ['url1', 'url2']
        })

        with patch.object(RedditSentiment, 'get_reddit_posts', return_value=mock_posts):
            result = self.sentiment.analyze_sentiment("AAPL")

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIsNone(result['error'])
        self.assertIn('average_sentiment', result['data'])
        self.assertIn('sentiment_distribution', result['data'])

    @patch('praw.Reddit')
    def test_analyze_sentiment_no_posts(self, mock_reddit):
        """Test sentiment analysis with no posts"""
        with patch.object(RedditSentiment, 'get_reddit_posts', return_value=pd.DataFrame()):
            result = self.sentiment.analyze_sentiment("INVALID")

        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertEqual(result['error'], "No Reddit posts found for INVALID")