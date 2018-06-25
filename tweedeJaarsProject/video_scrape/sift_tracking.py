import cv2
from skimage.transform import warp
import matplotlib.pyplot as plt

from PIL import ImageGrab
import numpy as np
from itertools import compress

# SIFT opencv:
# pip install --user opencv-contrib-python


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
obj_loc = [(0, 0), (0, 0)]

# converts sift point list to numpy array
def get_coordinate_list(point_list):
    x_list = []
    y_list = []
    for point in point_list:
        x_list.append(point[0][0])
        y_list.append(point[0][1])
    return np.array([x_list, y_list]).T

# returns bounding box dimension based on min and max point values 
def get_box_points(dst):
    points = get_coordinate_list(dst)
    x_list, y_list = sorted(points[:,0]),sorted(points[:,1])
    start = (int(round(min(x_list[:2]),0)+0.5),int(round(min(y_list[:2]),0)+0.5))
    end = (int(round(max(x_list[2:]),0)+0.5),int(round(max(y_list[2:]),0)+0.5))
    return start, end


# returns box based on relative point distances to corners points.
def get_point_based_box(src, dst, shape):
    src_points = get_coordinate_list(src)
    dst_points = get_coordinate_list(dst)
       
    # find centroids of keypoints clouds
    src_centroid = [np.mean(src_points[:, 0]), np.mean(src_points[:, 1])]
    dst_centroid = [np.mean(dst_points[:, 0]), np.mean(dst_points[:, 1])]
        
    # find ranges in x and y direction of keypoint clouds
    src_range_x = int(max(src_points[:, 0])-min(src_points[:, 0]))
    src_range_y = int(max(src_points[:, 1])-min(src_points[:, 1]))
        
    dst_range_x = int(max(dst_points[:, 0])-min(dst_points[:, 0]))
    dst_range_y = int(max(dst_points[:, 1])-min(dst_points[:, 1]))
        
    # calculate new roi size based on ranges of the src and dst keypoints
    new_shape = (shape[0] / src_range_y * dst_range_y, shape[1] / src_range_x * dst_range_x)
    
    relative_centroid_position_x = src_centroid[0] / shape[1]
    relative_centroid_position_y = src_centroid[1] / shape[0]
       
    top_left_x = dst_centroid[0] - new_shape[1]*relative_centroid_position_x
    top_left_y = dst_centroid[1] - new_shape[0]*relative_centroid_position_y
    
    bot_right_x = top_left_x + new_shape[1]
    bot_right_y = top_left_y + new_shape[0]
    
    start = (max(int(round(top_left_x)), 1), max(1, int(round(top_left_y))))
    end = (max(1, int(round(bot_right_x))), max(1, int(round(bot_right_y))))
    return start, end
    
def sift_roi_localization(roi,img):
    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(roi, None)
    kp2, des2 = sift.detectAndCompute(img, None)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])

    MIN_MATCH_COUNT = 6
    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m[0].queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m[0].trainIdx].pt for m in good ]).reshape(-1,1,2)
       
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        src_pts = [src_pts[i] for i in range(len(src_pts)) if matchesMask[i]]
        dst_pts = [dst_pts[i] for i in range(len(dst_pts)) if matchesMask[i]]
        
        h, w = roi.shape[:2]
                
        (start_x, start_y), (end_x, end_y) = get_point_based_box(src_pts, dst_pts, (h, w))
        new_roi = img.copy()[start_y:end_y, start_x:end_x]

        return img, new_roi, [(start_x, start_y), (end_x, end_y)]
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
        cv2.destroyAllWindows()
        return (), (), [(0, 0), (0, 0)]
    

# select the object to track
def click_and_crop(event, x, y, flags, param):
    global obj_loc
    cropping = False

    if event == cv2.EVENT_LBUTTONDOWN:
        obj_loc = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        if x > obj_loc[0][0] or x > obj_loc[0][1]:
            obj_loc.append((x, y))
        elif x <= obj_loc[0][0] or x <= obj_loc[0][1]:
            obj_loc = [(x, y)] + obj_loc
        cropping = False

        
# returned het te tracken object als subfoto
def get_region_of_interest(input_image):
    global obj_loc
    obj_loc = [(0, 0), (0, 0)]
    clone = input_image.copy()
    cv2.namedWindow("Mark object of interest")
    cv2.setMouseCallback("Mark object of interest", click_and_crop)

    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("Mark object of interest", input_image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            input_image = clone.copy()

        # if the 'q' key is pressed, break from the loop
        elif key == ord("q"):
            break

    cv2.destroyAllWindows()
    print(obj_loc)
    if obj_loc:
        return clone[obj_loc[0][1]:obj_loc[1][1], obj_loc[0][0]:obj_loc[1][0]]
    else:
        return



# tracker for different sources
def tracker():
    count = 0
    
    # get initial frame and roi
    frame = cv2.cvtColor(np.array(ImageGrab.grab(bbox=the_window)), cv2.COLOR_BGR2RGB)
    roi = get_region_of_interest(frame)
    prev = roi
    
    
    while(1):
        new_frame = cv2.cvtColor(np.array(ImageGrab.grab(bbox=the_window)), cv2.COLOR_BGR2RGB)
        combo, roi = sift_roi_localization(roi, new_frame)
        
        if combo is not ():
            cv2.imshow('frame', combo)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                lost = False
                break
        
        else:
            break
            
        if prev.shape != roi.shape:
            count += 1
            prev = roi
    print(count)

