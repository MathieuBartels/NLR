import youtube_dl
from cv2 import *
import os
from .sift_tracking import get_region_of_interest, sift_roi_localization
# import requests
from .bounding_box_saver import box_to_csv

# returns the max value of image index in the image directory
def get_max_image_num(directory):
    max = 0
    for image in os.listdir(directory):
        if ".jpg" in image:
            num = int(image.split('_')[-1].replace(".jpg", ""))
            if num > max:
                max = num
    return max + 1

def get_youtube_link(url, location, form, name):
    """
        This function will download a youtube video
        with the format givin in the parameters.
        input:
            url         :str
            location    :str
            form        :str
            name        :str
        return:
            location of file    :str
    """
    options = {
        'format': form, # convert to mp4
        'outtmpl': location + "/" + name + "." + form, # name the file the ID of the video
    }
    ydl = youtube_dl.YoutubeDL(options)
    with ydl:
        result = ydl.extract_info(url, download=True)

    if 'entries' in result:
        # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        # Just a video
        video = result
    return location + "/" + name + "." + form



def no_smart_select_to_data(video_location, picture_location, thres, name):
    vidcap = cv2.VideoCapture(video_location)
    success, image = vidcap.read()
    track = False
    roi = None
    speed = 5
    count = get_max_image_num(picture_location)
    result = []
    retrack = False

    while success:
        key = cv2.waitKey(speed) & 0xFF
        success, image = vidcap.read()
        image = cv2.resize(image, (0, 0), fx=0.6, fy=0.6)

        # if (r)etrack is pressed let user reselect object of interest
        if retrack:
            roi = get_region_of_interest(image)
            name = input("what object are you tracking here")
            retrack = False

        # if tracking is active detect the region of interest
        # store the image and save the location of the bounding box
        if track:

            combo, roi, [(x_1, y_1), (x_2, y_2)] = sift_roi_localization(roi, image)
            if combo != () and roi.shape != (0, 0, 3) :
                file_name = picture_location + "/%s_%d.jpg" % (name, count)
                cv2.imwrite(file_name, combo)
                image = cv2.rectangle(image, (x_1, y_1), (x_2, y_2), (0, 0, 255), 2)
                result.append(["%s_%d.jpg" % (name, count), combo.shape[0], combo.shape[1], name, x_1, y_1, x_2, y_2, "video_scrape"])
                count += 1
            else:
                track = False

            # print("Lost the object")
            # track = False

        # press s to start or stop tracking
        if key == ord('s'):
            if not track:
                roi = get_region_of_interest(image)
                name = input("what object are you tracking here")
            if list(roi.shape) != [0, 0, 3]:
                track ^= True
                cv2.destroyAllWindows()

        # press q to stop the video
        if key == ord('r'):
            retrack = True


        # press q to stop the video
        if key == ord('q'):
            cv2.destroyAllWindows()
            break

        cv2.imshow('Press s if you detect an object of interest', image)
    box_to_csv(result, picture_location)