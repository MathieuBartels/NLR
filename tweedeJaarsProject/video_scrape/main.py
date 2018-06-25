from .process_video import get_youtube_link, no_smart_select_to_data
import cv2
import os

def main(url, name, location="video", form="mp4"):
    video_location = get_youtube_link(url, location, form, name)

    directory = "images/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    no_smart_select_to_data(video_location, directory, 0.9, name)

