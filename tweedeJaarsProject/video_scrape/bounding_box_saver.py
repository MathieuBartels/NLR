import os
import pandas as pd
import cv2


folder = "images/"


# creates an csv with the new data
def box_to_csv(data_rows, directory, csv_file="dataset.csv"):
    file = directory+"/"+csv_file
    if os.path.isfile(file):
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame([], columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source"])
    df1 = pd.DataFrame(data_rows, columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source"])
    df = pd.concat([df, df1]).drop_duplicates(subset="filename").reset_index(drop=True)
    df.to_csv(file, index=False)
    return df
