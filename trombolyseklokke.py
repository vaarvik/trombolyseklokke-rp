from tkinter import *
import time

class Timer:
    def __init__(self):
        self.totalSeconds = 0
    
    def start_timer(self):
        self.totalSeconds += 1
        label = Label(root, text=self.totalSeconds, fg="#FFFFFF", bg="#000000", font=("Helvetica", 18))
        label.place(x=70, y=90)
        root.after(1000, self.start_timer)

def end_fullscreen(event):
    root.attributes("-fullscreen", False)

root = Tk()
root.wm_title("Trombolyseklokke")
root.configure(bg="#000000")
label = Label(root, text=0, fg="#FFFFFF", bg="#000000", font=("Helvetica", 18))
label.place(x=70, y=90)
root.attributes("-fullscreen", True)
timer = Timer()
root.after(1000, timer.start_timer)

root.bind("<Escape>", end_fullscreen)

root.mainloop()
