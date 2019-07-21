import cv2
import numpy as np
import threading
import queue
import tkinter as tk
import tkfontchooser



# init def
request_queue = queue.Queue()
result_queue = queue.Queue()
t = None


# setters for Tk GUI elements
def fingers_label(numOf):
    t.children["fingers"].configure(text=str("Fingers = %s " % numOf))


def command_label(numOf):
    t.children["command"].configure(text=str("Command = %s" % numOf))


def print_to_cBox(cb, *args, **kwargs):
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
    fingers = tk.Label(t, name="fingers", text="None", font=fontv)
    fingers.place(x=20, y=10)
    command = tk.Label(t, name="command", text="None", font=fontv)
    command.place(x=20, y=60)
    # start timer a.k.a. scheduler
    timertick()
    # main Tk loop
    t.mainloop()



