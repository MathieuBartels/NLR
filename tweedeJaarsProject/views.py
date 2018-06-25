from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import os

# Create your views here.

# returns the total amount of images and images per class and source
def get_statistics(file_name):
	if os.path.isfile(file_name):
		df = pd.read_csv(file_name)

		dataset_size = df.filename.count()
		classes_keys = dict(df.groupby('class').size())
		sources_keys =  dict(df.groupby('source').size())

		return dataset_size,classes_keys,sources_keys
	else:
		return 0,{"No data available":None}, {"No data available":None},


def index(request):
    file_name = "images/dataset.csv"
    stats = get_statistics(file_name)
    print(stats)    
    return render(request, 'index.html', {
        'total': stats[0],
        'stats_class': stats[1],
        'stats_method': stats[2]
    })
