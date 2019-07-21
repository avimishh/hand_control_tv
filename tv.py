import cv2
import numpy as np
import threading


# channel global variables
class Channel:
    index = 0
    isPlaying = True
    N = 5
    channelChanged = True


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
    a = 0
    while True:
        # if channel.isPlaying == True:
        if Channel.channelChanged is True:
            cap = cv2.VideoCapture(all_channels[Channel.index])
            Channel.channelChanged = False
        while cap.isOpened():
            _, tv_frame = cap.read()
            if _ is False:
                break
            cv2.putText(tv_frame, "CH #" + str(Channel.index + 1), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            if Channel.isPlaying is True:
                cv2.imshow('tv', tv_frame)
            # cap = cv2.VideoCapture(all_channels[channel.index])
            # while channel.isPlaying == False and key_pressed != ord('q'):
            key_pressed = cv2.waitKey(50)
            if key_pressed == ord('q'):
                break
            if Channel.channelChanged is True:
                cap.release()
        cap.release()
    # cv2.destroyAllWindows()
    # cv2.destroyWindow('tv')


