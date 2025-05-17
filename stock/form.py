from django import forms

class StockSymbolForm(forms.Form):
    symbol = forms.CharField(label='Stock Symbol', max_length=10, required=True)