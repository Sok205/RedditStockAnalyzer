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
