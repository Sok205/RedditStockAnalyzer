"""
This module contains a class to fetch stock data using the yfinance library.
"""

import time
import yfinance as yf
from requests.exceptions import HTTPError, RequestException

class FetchStockData:
    """
    A class to fetch stock data using the yfinance library.
    """

    def get_stock_data(self, stock_symbol: str, max_tries: int = 5, delay: int = 6):
        """
        Fetches stock data for a given stock symbol.
        :param stock_symbol: The stock symbol to fetch data for.
        :param max_tries: The maximum number of attempts to fetch data.
        :param delay: The delay between attempts in seconds.
        :return: A dictionary containing the stock data or error information.
        """
        result = {
            'success': False,
            'data': None,
            'error': None
        }

        for attempt in range(max_tries):
            try:
                if attempt > 0:
                    time.sleep(delay)

                stock = yf.Ticker(stock_symbol)
                info = stock.info
                current_price = info.get('currentPrice')

                # Checking if current price is available
                if current_price is None:
                    result.update({
                        'success': False,
                        'data': None,
                        'error': f"Current price for {stock_symbol} is not available"
                    })
                    break

                result.update({
                    'success': True,
                    'data' : {
                        'current_price': current_price,
                        'currency' : info.get('currency')
                    },
                    'error': None
                })
                return result

            except HTTPError as e:
                if hasattr(e, 'response') and e.response.status_code == 429:
                    print(f"Attempt: {attempt + 1} of {max_tries} failed due to rate limit. Retrying...")
                    if attempt == max_tries - 1:
                        result.update({
                            'success': False,
                            'data': None,
                            'error': "Rate limit exceeded. Try again later",
                        })
                continue

            except RequestException as e:
                result.update({
                    'success': False,
                    'error': f"Failed to fetch stock data for {stock_symbol}",
                    'data': None
                })
                break

        return result

    def get_historical_stock_data(self, stock_symbol: str, period: str = "1mo", interval: str = "1d", max_tries: int = 5, delay: int = 6):
        """
        Fetches historical stock data for a given stock symbol.
        :param stock_symbol: The stock symbol to fetch data for.
        :param period: The period of data to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
        :param interval: The interval between data points (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
        :param max_tries: The maximum number of attempts to fetch data.
        :param delay: The delay between attempts in seconds.
        :return: A dictionary containing the historical stock data or error information.
        """
        # Result dictionary to store the response
        result = {
            'success': False,
            'data': None,
            'error': None
        }

        # Loop to retry fetching data in case of errors
        for attempt in range(max_tries):
            try:
                if attempt > 0:
                    time.sleep(delay)

                stock = yf.Ticker(stock_symbol)
                historical_data = stock.history(period=period, interval=interval)

                if historical_data.empty:
                    result.update({
                        'success': False,
                        'data': None,
                        'error': f"No historical data available for {stock_symbol}"
                    })
                    break
                hist_data = historical_data.reset_index()
                hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')

                formatted_data = {
                    'dates' : hist_data['Date'].tolist(),
                    'prices' : hist_data['Close'].tolist(),
                    'volume' : hist_data['Volume'].tolist()
                }

                result.update({
                    'success': True,
                    'data': formatted_data,
                    'error': None
                })
                return result

            except HTTPError as e:
                if hasattr(e, 'response') and e.response.status_code == 429:
                    print(f"Attempt: {attempt + 1} of {max_tries} failed due to rate limit. Retrying...")
                    if attempt == max_tries - 1:
                        result.update({
                            'success': False,
                            'data': None,
                            'error': "Rate limit exceeded. Try again later",
                        })
                continue

            except RequestException as e:
                result.update({
                    'success': False,
                    'error': f"Failed to fetch historical data for {stock_symbol}",
                    'data': None
                })
                break

if __name__ == "__main__":
    fetcher = FetchStockData()
    symbol = "AAPL"
    result = fetcher.get_stock_data(symbol)
    print(result)

    result_history = fetcher.get_historical_stock_data(symbol)
    print(result_history)