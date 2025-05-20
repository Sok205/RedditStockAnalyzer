"""
stock/views.py
"""
from django.shortcuts import render, redirect
from stock.reddit_sentiment import RedditSentiment
from stock.ml.analyzer_ml import MlSentimentAnalyzer
from .stock_data import FetchStockData
from .form import StockSymbolForm
def home(request):
    """
    Renders the home page.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = StockSymbolForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol']
            return redirect('reddit_sentiment_ml') + f'?symbol={symbol}'
    else:
        form = StockSymbolForm()
    return render(request, 'stock/home.html', {'form': form})

def reddit_sentiment(request):
    """
    Renders the sentiment analysis page.
    :param request:
    :return:
    """
    symbol = request.GET.get('symbol', '')
    time_filter = request.GET.get('time_filter', 'week')

    if time_filter not in ["week", "month", "year"]:
        time_filter = "week"

    if symbol:
        sentiment = RedditSentiment()
        result = sentiment.analyze_sentiment(symbol, time_filter=time_filter)
        if result['success'] and result['data']:
            result['data']['time_filter'] = time_filter

    else:
        result = {
            'success': False,
            'error': 'No symbol provided',
            'data': None
        }

    stock_fetcher = FetchStockData()
    stock_data = stock_fetcher.get_stock_data(symbol)


    return render(request, 'stock/sentiment.html', {'result': result, 'symbol': symbol, 'time_filter': time_filter, 'stock_data': stock_data})


def reddit_sentiment_ml_view(request):
    """
    Renders the sentiment analysis page using ML.
    :param request:
    :return:
    """
    symbol = request.GET.get('symbol', 'AAPL')
    time_filter = request.GET.get('time_filter', 'week')

    if time_filter not in ["week", "month", "year"]:
        time_filter = "week"

    form = StockSymbolForm()

    if symbol:
        reddit = RedditSentiment()
        ml_analyzer = MlSentimentAnalyzer()
        posts_df = reddit.get_reddit_posts(symbol, limit=50, time_filter=time_filter)

        if posts_df.empty:
            result = {
                'success': False,
                'error': f'No posts found for {symbol}',
                'data': None
            }
        else:
            posts_df['preprocessed'] = posts_df['text'].apply(ml_analyzer.preprocess)
            posts_df['ml_sentiment'] = posts_df['preprocessed'].apply(ml_analyzer.analyze_sentiment)

            avg_ml_sentiment = posts_df['ml_sentiment'].mean()
            top_posts = posts_df.nlargest(5, 'ml_sentiment')[['title', 'ml_sentiment', 'url']]

            result = {
                'success': True,
                'data': {
                    'average_sentiment': float(avg_ml_sentiment),
                    'posts_count': len(posts_df),
                    'top_posts': top_posts.to_dict(orient='records'),
                    'time_filter': time_filter
                },
                'error': None
            }
    else:
        result = {
            'success': False,
            'error': 'No symbol provided',
            'data': None
        }

    stock_fetcher = FetchStockData()
    stock_data = stock_fetcher.get_stock_data(symbol)

    return render(request, 'stock/sentimentml.html', {
        'form': form,
        'result': result,
        'symbol': symbol,
        'time_filter': time_filter,
        'stock_data': stock_data
    })