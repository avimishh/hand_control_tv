#region imports
import cv2
import numpy as np
import math
import threading
from tkinter import font
import tkinter as tk
import queue
import time
import tkfontchooser
import tv
# from tv import channel
# from tv import tv_thread
import command_box as cBox
#endregion


#region media player commands define
# command string
class Command:
    com_string = ""

def play():
    Command.com_string = "PLAY"
    tv.Channel.isPlaying = True
def pause():
    Command.com_string = "PAUSE"
    tv.Channel.isPlaying = False
def move_next():
    Command.com_string = "NEXT"
    tv.Channel.index = (tv.Channel.index + 1) % tv.Channel.N
    tv.Channel.channelChanged = True
def move_prev():
    Command.com_string = "PREVIOUS"
    tv.Channel.index = (tv.Channel.index - 1) % tv.Channel.N
    tv.Channel.channelChanged = True
def vol_down():
    Command.com_string = "VOLUME DOWN"
#endregion


#region player's command execution
def exec(fingers_num):
    if fingers_num == 1:
        play()
    elif fingers_num == 2:
        pause()
    elif fingers_num == 3:
        move_next()
    elif fingers_num == 4:
        move_prev()
    elif fingers_num == 5:
        vol_down()
    cBox.print_to_cBox(cBox.fingers_label, str(fingers_num))
    if Command.com_string:
        cBox.print_to_cBox(cBox.command_label, Command.com_string)

#endregion


# region User Camera print text
def camera_print_text(l):
    font = cv2.FONT_HERSHEY_SIMPLEX
    if l == 1:
        if hand_area < 2000:
            cv2.putText(frame, 'Put hand in the box', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        else:
            if area_ratio < 12:
                cv2.putText(frame, '0', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            else:
                cv2.putText(frame, '1', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 2:
        cv2.putText(frame, '2', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 3:
        if area_ratio < 27:
            cv2.putText(frame, '3', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        else:
            cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 4:
        cv2.putText(frame, '4', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 5:
        cv2.putText(frame, '5', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    elif l == 6:
        cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

    else:
        cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)


# endregion


# region Freeze Time Check
def cool_down():
    global LAST_TIME
    if time.time() - LAST_TIME > COOL_DOWN:
        LAST_TIME = time.time()
        return False
    else:
        return True
# endregion


# initial definitions
COOL_DOWN = 5
LAST_TIME = time.time()

cam = cv2.VideoCapture(0)

if __name__ == '__main__':
    threading.Thread(target=cBox.tk_thread).start()
    threading.Thread(target=tv.tv_thread).start()
    # exe = True

    while cam.isOpened():
        # try, catch for skip error when cannot find any contour of max area
        try:
            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            kernel = np.ones((3, 3), np.uint8)

            # roi = small square from screen
            roi = frame[100:300, 100:300]

            # define red box which represent the roi area
            cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # range of the skin color is defined
            lower_skin = np.array([0, 100, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)

            # extract skin color image
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            # fill dark spots within the hand
            mask = cv2.dilate(mask, kernel, iterations=4)

            # mask is blurred using GBlur
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            # find contours
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # find contour of max area(hand)
            hand_cnt = max(contours, key=lambda x: cv2.contourArea(x))

            # approx the contour a little
            epsilon = 0.0005 * cv2.arcLength(hand_cnt, True)     # hand_cnt perimeter
            hand_approx = cv2.approxPolyDP(hand_cnt, epsilon, True)      # skip/remove small curves

            # make convex hull around hand
            hull = cv2.convexHull(hand_cnt)
            cv2.imshow('hello', mask)
            # define area of hull and area of hand
            hull_area = cv2.contourArea(hull)        # hull area
            hand_area = cv2.contourArea(hand_cnt)     # hand area

            # find the percentage of area not covered by hand in convex hull
            area_ratio = ((hull_area - hand_area) / hand_area) * 100

            # find the defects in convex hull with respect to hand
            hull = cv2.convexHull(hand_approx, returnPoints=False)   # returnPoints=False for finding defects
            defects = cv2.convexityDefects(hand_approx, hull)

            # l = n. of defects
            l = 0

            # code for finding n. of defects due to fingers
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(hand_approx[s][0])
                end = tuple(hand_approx[e][0])
                far = tuple(hand_approx[f][0])
                # pt = (100, 180)

                # find length of all sides of triangle
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                s = (a + b + c) / 2
                ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

                # distance between point and convex hull
                d = (2 * ar) / a


                # apply cosine rule here
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
                if angle <= 90 and d > 30:
                    l += 1
                    cv2.circle(roi, far, 3, [255, 0, 0], -1)

                # draw lines around hand
                cv2.line(roi, start, end, [0, 255, 0], 2)

            l += 1

            # print corresponding text which indicate hand reading
            camera_print_text(l)

            # delay, do not change command quickly, wait for 5 sec
            if cool_down() is False:
                exec(l)

            cv2.imshow('mask', mask)
            cv2.imshow('frame', frame)
        except:
            pass

        k = cv2.waitKey(5)
        if k == 27:
            break


# cv2.destroyAllWindows()
# cap.release()


