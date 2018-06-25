import os
from .bounding import main
from django.shortcuts import render
from django.core.files.base import ContentFile



# Create your views here.
def index(request):
    if request.method == 'GET':
        return render(request, 'blenderindex.html',)
    else:   
        if request.method == 'POST':
            uploadBackground(request)
            name = uploadModel(request)
            blenderPath = request.POST['path']
            number = request.POST['number']
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


            path = (os.path.join(base_dir, 'blender'))
            os.chdir(path)
            
            os.system(blenderPath + " --background " + "static\\models\\" + name + " --python main.py" + " -- " + number) 


            main(name.replace(".blend",""))     
             
            for a_file in os.listdir(os.path.join(base_dir, "blender/static", "background_images")):
                os.remove(os.path.join(base_dir, "blender/static", "background_images", a_file))

            os.chdir(base_dir)



            #// Here you are calling script_function, 
            #// passing the POST data for 'info' to it;
            return render(request, 'blenderindex.html', {})
    return render(request, 'blenderindex.html',)

def uploadBackground(request):
    folder = "blender\\static\\background_images"
    for a_file in request.FILES.getlist('backgroundImage'):
        uploaded_filename = a_file.name

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        location = os.path.join(base_dir, folder)
            # create the folder if it doesn't exist.
        try:
            os.mkdir(location)
        except:
            pass

        full_filename = os.path.join(location, uploaded_filename)
        fout = open(full_filename, 'wb+')

        file_content = ContentFile(a_file.read())
        # Iterate through the chunks.
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()
    return

def uploadModel(request):
    folder = "blender\\static\\models"

    uploaded_filename = request.FILES['Model'].name
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    location = os.path.join(base_dir, folder)
        # create the folder if it doesn't exist.
    try:
        os.mkdir(location)
    except:
        pass

    full_filename = os.path.join(location, uploaded_filename)
    fout = open(full_filename, 'wb+')

    file_content = ContentFile(request.FILES['Model'].read())
    # Iterate through the chunks.
    for chunk in file_content.chunks():
        fout.write(chunk)
    fout.close()
    return uploaded_filename
