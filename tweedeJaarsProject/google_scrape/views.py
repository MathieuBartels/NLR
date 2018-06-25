import os
from django.shortcuts import render
from django.core.files.base import ContentFile
from .main2 import google_scrape



# Create your views here.
def index(request):
    if request.method == 'GET':
        return render(request, 'googlescrapeindex.html', {
            "form" : True,
        })
    else:   
        if request.method == 'POST' and request.FILES['myfile']:
            uploaded_filename = upload(request)
            query = request.POST['query']
            google_scrape(query, uploaded_filename )

            #// Here you are calling script_function, 
            #// passing the POST data for 'info' to it;
            return render(request, 'googlescrapeindex.html', { })
    return render(request, 'googlescrapeindex.html',)


def upload(request):
    folder = "google_scrape\\static\\gold_image\\"

    uploaded_filename = request.FILES['myfile'].name
    query = request.POST['query']
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # create the folder if it doesn't exist.
    try:
        os.mkdir(os.path.join(base_dir, folder, query))
    except:
        pass

    full_filename = os.path.join(base_dir, folder, query, uploaded_filename)
    fout = open(full_filename, 'wb+')

    file_content = ContentFile(request.FILES['myfile'].read())
    # Iterate through the chunks.
    for chunk in file_content.chunks():
        fout.write(chunk)
    fout.close()
    return full_filename
