import pandas as pd
import cv2
import os
import sys, os, argparse

folder = "../images/"


# creates an csv with the new data
def box_to_csv(data_rows, directory, csv_file="dataset.csv"):
    file = directory+"/"+csv_file
    if os.path.isfile(file):
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame([], columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source","id"])
    df1 = pd.DataFrame(data_rows, columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source","id"])
    df = pd.concat([df, df1]).drop_duplicates(subset="filename").reset_index(drop=True)
    df.to_csv(file, index=False)
    return df


# function to find images in dir_path of type ext 
def get_images2(dir_path, ext):
    images = []
    for f in os.listdir(dir_path):
        if f.endswith(ext) and f.startswith("B_"):
            images.append(f)
    return images


# create bounding boxes for all images in dir_path of type ext (bv: .png)
# object_class: class of object as string 
def blender_boxes(dir_path, ext, object_class):
    images = get_images2(dir_path, ext)
    print("found:", len(images), "images")
    
    result = []
    for i in images:
        img = cv2.imread(dir_path+i, 2)
        im2, contours, hierarchy = cv2.findContours(img, 1, 2)
        
        # get max contour
        cnt = sorted(contours, key = cv2.contourArea)[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        id = int(i.split("_")[-1].split(".jpg")[0])
        result.append([i, img.shape[0], img.shape[1], object_class, x, y, x+w, y+h, "blender",id])
        
        img2 = cv2.rectangle(im2, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    box_to_csv(result, dir_path)
    cv2.destroyAllWindows()

def match_boxes(image_directory,black_directory, csv="dataset.csv"):
    file = image_directory+csv
    print(file)
    bb = pd.read_csv(black_directory+"/"+csv)

    if os.path.isfile(file):
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame([], columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source"])

    images = get_images2(image_directory, ".jpg")
    result = []
    print(df)
    for i in images:
        img = cv2.imread(image_directory+i, 2)
        id = int(i.split("_")[-1].split(".jpg")[0])
        row = bb.loc[bb["id"] == id].values.tolist()[0]
        print(row)
        row[0] = i
        result.append(row[:-1])
    
    df1 = pd.DataFrame(result, columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax", "source",])
    df = pd.concat([df, df1]).drop_duplicates(subset="filename").reset_index(drop=True)
    df.to_csv(file, index=False)


def main(dronetype):
    blender_boxes("frames/", ".jpg", dronetype)
    csv_dataset = "frames/dataset.csv"
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    match_boxes(folder, "frames")
    base_dir

    for a_file in os.listdir(os.path.join(base_dir, "blender/frames")):
        os.remove(os.path.join(base_dir, "blender/frames", a_file))