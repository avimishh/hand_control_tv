import cv2
import numpy as np
import math
import threading
from tkinter import font
# import view
import tkinter as tk
import queue
import time
import tkfontchooser

request_queue = queue.Queue()
result_queue = queue.Queue()
t = None
COOLDOWN = 5
LAST_TIME = time.time()
class command:
    com = ""

def play():
    command.com = "PLAY"
def pause():
    command.com = "PAUSE"
def move_next():
    command.com = "NEXT"
def move_prev():
    command.com = "PREVIOUS"
def vol_down():
    command.com = "VOLUME CONTROL DOWN"



def submit_to_tkinter(cb, *args, **kwargs):
    request_queue.put((cb, args, kwargs))
    return result_queue.get()


def main_tk_thread():
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
    t.title("Debug controls")
    t.geometry('%dx%d+%d+%d' % (320, 320, 850, 200))
    # set font for labels
    fontv = tkfontchooser.Font(family="Arial", size=18)
    # create buttons, labels
    fingers = tk.Label(t, name="fingers", text="None", font= fontv)
    fingers.place(x=20, y=10)
    # hull = tk.Label(t, name="hull", text="None", font= fontv)
    # hull.place(x=20, y=10)
    defects = tk.Label(t, name="defects", text="None", font=fontv)
    defects.place(x=20, y=60)
    command = tk.Label(t, name="command", text="None", font=fontv)
    command.place(x=20, y=160)
    # start timer a.k.a. scheduler
    timertick()
    # main Tk loop
    t.mainloop()



# setters for Tk GUI elements
def fingers_label(a):
    t.children["fingers"].configure(text=str("Fingers = %s " % a))

# def defects_label(a):
#     t.children["defects"].configure(text=str("All defects = %s" % a))

def command_label(a):
    t.children["command"].configure(text=str("Command = %s" % a))


def exec(fingers_num):
    submit_to_tkinter(fingers_label, str(fingers_num))
    # submit_to_tkinter(hull_label, str(hull.shape[0]))
    # submit_to_tkinter(defects_label, str(defects.shape[0]))
    if command.com:
        submit_to_tkinter(command_label, command.com)




# import math
# from tkinter import font
# import numpy as np
# import cv2  # required 3+
# import tkinter as tk
# import threading
# import queue
# import time
#
#
# request_queue = queue.Queue()
# result_queue = queue.Queue()
# t = None
# COOLDOWN = 5
# LAST_TIME = time.time()
#
# def submit_to_tkinter(cb, *args, **kwargs):
#     request_queue.put((cb, args, kwargs))
#     return result_queue.get()
#
#
# def main_tk_thread():
#     global t
#
#     def timertick():
#         try:
#             cb, args, kwargs = request_queue.get_nowait()
#         except queue.Empty:
#             pass
#         else:  # if no exception was raised
#             retval = cb(*args, **kwargs)
#             result_queue.put(retval)
#         # reschedule after some time
#         t.after(10, timertick)
#
#     # create main Tk window
#     t = tk.Tk()
#     t.title("Debug controls")
#     t.geometry('%dx%d+%d+%d' % (320, 320, 850, 200))
#     # set font for labels
#     fontv = font.Font(family="Arial", size=18, weight=font.BOLD)
#     # create buttons, labels
#     hull = tk.Label(t, name="hull", text="None", font=fontv)
#     hull.place(x=20, y=10)
#     defects = tk.Label(t, name="defects", text="None", font=fontv)
#     defects.place(x=20, y=60)
#     command = tk.Label(t, name="command", text="None", font=fontv)
#     command.place(x=20, y=160)
#     # start timer a.k.a. scheduler
#     timertick()
#     # main Tk loop
#     t.mainloop()
#
#
#
# # setters for Tk GUI elements
# def hull_label(a):
#     t.children["hull"].configure(text=str("All hulls = %s " % a))
#
#
# def defects_label(a):
#     t.children["defects"].configure(text=str("All defects = %s" % a))
#
#
# # def check_command(c, exe):
# #     if c == 1:
# #         if REALLY_NOT_DEBUG and exe:
# #             play()
# #         return "PLAY"
# #     elif c == 2:
# #         if REALLY_NOT_DEBUG and exe:
# #             pause()
# #         return "PAUSE"
# #     elif c == 3:
# #         if REALLY_NOT_DEBUG and exe:
# #             move_next()
# #         return "NEXT"
# #     elif c == 4:
# #         if REALLY_NOT_DEBUG and exe:
# #             move_prev()
# #         return "PREVIOUS"
# #     elif c == 5:
# #         if CHANGE_VOLUME and exe:
# #             vol_down()
# #         return "VOLUME CONTROL DOWN"
#
#
#
#
#     # do not 'change' command to quickly and wait after last one
#     if time.time() - LAST_TIME > COOLDOWN and enable_commands:
#         exe = True
#         LAST_TIME = time.time()
#     else:
#         exe = False
#
#     # check what command to execute and run it
#     com = check_command(count_defects, exe)
#
#     # delta = time.time() - LAST_TIME
#     # to_next = COOLDOWN - delta
#     # if to_next < 0:
#     #     to_next = 0
#     # submit some data to GUI
#     submit_to_tkinter(hull_label, str(hull.shape[0]))
#     submit_to_tkinter(defects_label, str(defects.shape[0]))
#     if com:
#         submit_to_tkinter(command_label, com)
#     # submit_to_tkinter(defects_filtered_label, str(count_defects))
#     # submit_to_tkinter(en_command_label, str("%s, cooldown %.2fs." % (enable_commands, to_next)))
#     # submit_to_tkinter(en_dbg_label, debug)
