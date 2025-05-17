from django.core.management.base import BaseCommand
import nltk

class Command(BaseCommand):
    help = 'Download NLTK vader_lexicon'

    def handle(self, *args, **kwargs):
        nltk.download('vader_lexicon')
        nltk.download('stopwords')
        nltk.download('punkt_tab')