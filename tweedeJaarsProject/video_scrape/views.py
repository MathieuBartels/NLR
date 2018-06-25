from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from .forms import FilesForm
import youtube_dl
import os
from .main import main
# Create your views here.


def index(request):
    if request.method == 'GET':
        return render(request, 'videoscrapeindex.html',)
    else:   
        if request.method == 'POST':
            link = request.POST['youtube']
            name = request.POST['name']
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            main(link, name)
            #// Here you are calling script_function, 
            #// passing the POST data for 'info' to it;
            return render(request, 'videoscrapeindex.html', { })
