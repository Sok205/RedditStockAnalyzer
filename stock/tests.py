"""
Unitests for stock app
"""
from unittest.mock import patch, Mock, PropertyMock
from django.test import TestCase
from requests.exceptions import HTTPError, RequestException
from .stock_data import FetchStockData


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
