from django.shortcuts import render

# Create your views here.

def home(request):
    """
    Renders the home page.
    :param request:
    :return:
    """
    return render(request, 'stock/home.html')