import yfinance as yf
import time
from django.http import Http404

class FetchStockData:
    def get_stock_data(self, stock_symbol: str, max_tries: int = 5, delay: int = 6):
        """
        Fetches stock data for a given stock symbol.
        :param stock_symbol: The stock symbol to fetch data for.
        :param max_tries: The maximum number of attempts to fetch data.
        :param delay: The delay between attempts in seconds.
        :return: A DataFrame containing the stock data.
        """

        for attempt in range(max_tries):
            try:
                if attempt > 0:
                    time.sleep(delay)

                stock = yf.Ticker(stock_symbol)

                try:
                    current_price = stock.info.get('currentPrice')
                    if current_price is None:
                        raise ValueError(f"Current price for {stock_symbol} is not available")

                    return {
                        'success': True,
                        'data' : {
                            'current_price': current_price,
                            'currenct' : stock.info.get('currency')
                        }
                    }

                except KeyError as e:
                    if e.response.status_code == 429:
                        print(f"Attempt: {attempt + 1} of {max_tries} failed due to rate limit. Retrying...")
                    if attempt == max_tries - 1:
                        raise ValueError(f"Rate limit exceeded. Try again later")
                    continue

            except Exception as e:
                print(f"Exception while fetching stock data for {stock_symbol}: {e}")
                if attempt == max_tries - 1:
                    return {
                        'success': False,
                        'error': f"failed to fetch stock data for {stock_symbol}"
                    }
                continue