# cv2.namedWindow('road')
# cap = cv2.VideoCapture('test2.mp4')
# while cap.isOpened():
#     _, frame = cap.read()
#     cv2.imshow('road', frame)
#     key_pressed = cv2.waitKey(1)
#     if key_pressed == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()

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
    t.geometry('%dx%d+%d+%d' % (400, 100, 850, 200))
    # set font for labels
    fontv = tkfontchooser.Font(family="Arial", size=18)
    # create buttons, labels
    fingers = tk.Label(t, name="fingers", text="None", font= fontv)
    fingers.place(x=20, y=10)
    # hull = tk.Label(t, name="hull", text="None", font= fontv)
    # hull.place(x=20, y=10)
    # defects = tk.Label(t, name="defects", text="None", font=fontv)
    # defects.place(x=20, y=60)
    command = tk.Label(t, name="command", text="None", font=fontv)
    command.place(x=20, y=60)
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