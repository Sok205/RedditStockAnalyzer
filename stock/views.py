"""
stock/views.py
"""
from django.shortcuts import render
from stock.reddit_sentiment import RedditSentiment
from stock.ml.analyzer_ml import MlSentimentAnalyzer
def home(request):
    """
    Renders the home page.
    :param request:
    :return:
    """
    return render(request, 'stock/home.html')

def reddit_sentiment(request):
    symbol = request.GET.get('symbol', 'AAPL')
    sentiment = RedditSentiment()
    result = sentiment.analyze_sentiment(symbol)
    return render(request, 'stock/sentiment.html', {'result': result, 'symbol': symbol})


def reddit_sentiment_ml_view(request):
    symbol = request.GET.get('symbol', 'AAPL')
    reddit = RedditSentiment()
    ml_analyzer = MlSentimentAnalyzer()
    posts_df = reddit.get_reddit_posts(symbol, limit=50)

    if posts_df.empty:
        return render(request, 'stock/sentiment.html', {
            'result': {'success': False, 'error': f'No posts for {symbol}'},
            'symbol': symbol
        })

    # Preprocessing and analyze sentiment using ML model
    posts_df['preprocessed'] = posts_df['text'].apply(ml_analyzer.preprocess)
    posts_df['ml_sentiment'] = posts_df['preprocessed'].apply(ml_analyzer.analyze_sentiment)

    avg_ml_sentiment = posts_df['ml_sentiment'].mean()
    top_posts = posts_df.nlargest(5, 'ml_sentiment')[['title', 'ml_sentiment', 'url']]

    result = {
        'success': True,
        'data': {
            'average_sentiment': float(avg_ml_sentiment),
            'posts_count': len(posts_df),
            'top_posts': top_posts.to_dict(orient='records')
        },
        'error': None
    }
    return render(request, 'stock/sentimentml.html', {'result': result, 'symbol': symbol})