import os
from matplotlib import pyplot as plt
import cv2
from google_images_download import google_images_download as gid
# Comparison compares two images, a golden standerd a new image, to each other and will return true 
# if it has enough matches

def comparison(golden_image,new_image,indir,show=False):
    if indir:
        img1 = cv2.imread(indir+'/'+golden_image)
        img2 = cv2.imread(indir+'/'+new_image)
    else:
        img1 = cv2.imread(golden_image)
        img2 = cv2.imread(new_image)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    sift = cv2.xfeatures2d.SIFT_create()

    kp1, desc1 = sift.detectAndCompute(img1, None)
    kp2, desc2 = sift.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    #matches = bf.match(desc1, desc2)
    #matches = sorted(matches, key = lambda x:x.distance)
    flann_index_kdtree = 0
    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc1, desc2, k=2)

    good1 = []
    for m, n in matches:
        if m.distance < 0.75*n.distance:
            good1.append(m)

    if show:
        n_matches = 100
        match_img = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches[:n_matches], None, flags=2)
        plt.figure(figsize=(12, 6))
        plt.imshow(match_img);
        plt.show()

    if len(good1) > 100:
        return "\\" + indir + new_image
    else:
        return None


#does the google query. The parameters "Query" and "N" need to be variables on the django home page
def fetch_images(query,n,map_name):
    response = gid.googleimagesdownload()
    arguments = {
        "keywords" : query,
        "limit": n,
        "print_urls": False,
        #"suffix_keywords": "Drone",
        "output_directory": map_name,
        "format": "png"
    }
    response.download(arguments)

#loops over the fetched images. We need to play around with maps and how we are going to store them. Python
# os.walk does funky things at times so be warned.
def loop_over_images(map_name,Query):
    indir = map_name + "\\" + Query + "\\"
    image_list = []
    for _, _, filenames in os.walk(indir):
        for f in filenames:
            image_list.append(f)
    return image_list, indir

def run_scrape(query, map_name, golden_image):
    fetch_images(query, 10, map_name)
    image_list, indir = loop_over_images(map_name, query)
    image_locations = []
    for image in image_list: #compares each image to a golden image
        loc = comparison(golden_image, image, indir, show=False)
        if loc:
            image_locations.append(loc.replace("google_scrape\\",""))
    return image_locations

