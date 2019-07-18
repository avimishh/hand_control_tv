import cv2
import numpy as np
import math
import threading
from tkinter import font
import tkinter as tk
import queue
import time
import tkfontchooser


# init def
request_queue = queue.Queue()
result_queue = queue.Queue()
t = None
COOLDOWN = 5
LAST_TIME = time.time()


# command string
class command:
    com = ""

# channel global variables
class channel:
    index = 0
    isPlaying = True
    N = 5
    channelChanged = True


def play():
    command.com = "PLAY"
    channel.isPlaying = True
def pause():
    command.com = "PAUSE"
    channel.isPlaying = False
def move_next():
    command.com = "NEXT"
    channel.index = (channel.index + 1) % channel.N
def move_prev():
    command.com = "PREVIOUS"
    channel.index = (channel.index - 1) % channel.N
def vol_down():
    command.com = "VOLUME DOWN"



def submit_to_tkinter(cb, *args, **kwargs):
    request_queue.put((cb, args, kwargs))
    return result_queue.get()


def tk_thread():
    global t

    def timertick():
        try:
            cb, args, kwargs = request_queue.get_nowait()
        except queue.Empty:
            pass
        else:  # if no exception was raised
            retval = cb(*args, **kwargs)
            result_queue.put(retval)
        # reschedule after some time
        t.after(10, timertick)

    # create main Tk window
    t = tk.Tk()
    t.title("Debug control")
    t.geometry('%dx%d+%d+%d' % (400, 100, 850, 200))
    # set font for labels
    fontv = tkfontchooser.Font(family="Arial", size=18)
    # create buttons, labels
    fingers = tk.Label(t, name="fingers", text="None", font= fontv)
    fingers.place(x=20, y=10)
    command = tk.Label(t, name="command", text="None", font=fontv)
    command.place(x=20, y=60)
    # start timer a.k.a. scheduler
    timertick()
    # main Tk loop
    t.mainloop()


# setters for Tk GUI elements
def fingers_label(numOf):
    t.children["fingers"].configure(text=str("Fingers = %s " % numOf))


def command_label(numOf):
    t.children["command"].configure(text=str("Command = %s" % numOf))


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
    submit_to_tkinter(fingers_label, str(fingers_num))
    if command.com:
        submit_to_tkinter(command_label, command.com)


def tv_thread():
    ch1 = './channels/ch1.mp4'
    ch2 = './channels/ch2.mp4'
    ch3 = './channels/ch3.mp4'
    ch4 = './channels/ch4.mp4'
    ch5 = './channels/ch5.mp4'

    all_channels = [ch1, ch2, ch3, ch4, ch5]

    key_pressed = 0
    cv2.resizeWindow('tv', 160, 80)
    cap = ""
    cv2.namedWindow('tv')
    while True:
        # if channel.isPlaying == True:
        if channel.channelChanged == True:
            cap = cv2.VideoCapture(all_channels[channel.index])
        while cap.isOpened():
            _, tv_frame = cap.read()
            if _ == False:
                break
            cv2.putText(tv_frame, "CH #" + str(channel.index+1), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            if channel.isPlaying == True:
                cv2.imshow('tv', tv_frame)
            # cap = cv2.VideoCapture(all_channels[channel.index])
            # while channel.isPlaying == False and key_pressed != ord('q'):
            key_pressed = cv2.waitKey(2)
            if key_pressed == ord('q'):
                break
            if channel.isPlaying == False:
                cap.release()
        cap.release()
    # cv2.destroyAllWindows()
    # cv2.destroyWindow('tv')




if __name__ == '__main__':
    threading.Thread(target=tk_thread).start()
    threading.Thread(target=tv_thread).start()
    # ininital definitions
    cam = cv2.VideoCapture(0)
    # exe = True


    while cam.isOpened():

        try:  # an error comes if it does not find anything in window as it cannot find contour of max area
            # therefore this try error statement

            _, frame = cam.read()
            frame = cv2.flip(frame, 1)
            kernel = np.ones((3, 3), np.uint8)

            # define roi which is a small square on screen
            roi = frame[100:300, 100:300]

            cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # range of the skin color is defined
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)

            # extract skin color image
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # extrapolate the hand to fill dark spots within
            mask = cv2.dilate(mask, kernel, iterations=4)

            # image is blurred using GBlur
            mask = cv2.GaussianBlur(mask, (5, 5), 100)

            # find contours
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # find contour of max area(hand)
            cnt = max(contours, key=lambda x: cv2.contourArea(x))

            # approx the contour a little
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # make convex hull around hand
            hull = cv2.convexHull(cnt)

            # define area of hull and area of hand
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)

            # find the percentage of area not covered by hand in convex hull
            arearatio = ((areahull - areacnt) / areacnt) * 100

            # find the defects in convex hull with respect to hand
            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)

            # l = no. of defects
            l = 0

            # code for finding no. of defects due to fingers
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                pt = (100, 180)

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

            # display corresponding gestures which are in their ranges
            font = cv2.FONT_HERSHEY_SIMPLEX
            if l == 1:
                # play()
                if areacnt < 2000:
                    cv2.putText(frame, 'Put hand in the box', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    if arearatio < 12:
                        cv2.putText(frame, '0', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                    else:
                        cv2.putText(frame, '1', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif l == 2:
                # pause()
                cv2.putText(frame, '2', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif l == 3:
                # move_next()
                if arearatio < 27:
                    cv2.putText(frame, '3', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                else:
                    cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif l == 4:
                # move_prev()
                cv2.putText(frame, '4', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif l == 5:
                # vol_down()
                cv2.putText(frame, '5', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            elif l == 6:
                cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            else:
                cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            # do not 'change' command to quickly and wait after last one
            if time.time() - LAST_TIME > COOLDOWN:
                exe = True
                LAST_TIME = time.time()
            else:
                exe = False

            delta = time.time() - LAST_TIME
            to_next = COOLDOWN - delta
            if to_next < 0:
                to_next = 0
            if exe == True:
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


