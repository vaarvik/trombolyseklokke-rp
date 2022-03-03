from tkinter import *
import logging
import time
import math

class Text:
    def __init__(self, text, x, y, window):
        self.x = x
        self.y = y
        self.window = window
        self.label = Label(window, text=text, fg="#FFFFFF", bg="#000000", font=("Helvetica", 18))
        self.label.place(x=x, y=y)
    
    def update(self, text):
        self.label = Label(self.window, text=text, fg="#FFFFFF", bg="#000000", font=("Helvetica", 18))
        self.label.place(x=self.x, y=self.y)

class Timer:
    def __init__(self, gui):
        logging.info("creating Timer")
        self.totalSeconds = 0
        self.GUIWindow = gui.window
        self.gui = gui
        self.text = Text(text=self.totalSeconds, x=self.gui.width / 2, y=self.gui.height / 2, window=self.GUIWindow)
        self.update_timer()
        
    def format_time(self):
        seconds = self.totalSeconds % 60
        minutes = math.floor(self.totalSeconds / 60)
        
        if(minutes < 10):
            minutes = "0" + str(minutes)
        else:
            minutes = str(minutes)
            
        if(seconds < 10):
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)
            
        return minutes + ":" + seconds
    def update_timer(self):
        self.totalSeconds += 1
        self.text.update(self.format_time())
        self.GUIWindow.after(1000, self.update_timer)

class GUI:
    def __init__(self):
        self.window = Tk()
        self.title = "Trombolyseklokke"
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight() 
        self.totalTimer = Timer(self)
        
        # config
        logging.info("configuring GUI")
        self.window.wm_title(self.title)       
        self.window.configure(bg="#000000")
        self.window.attributes("-fullscreen", True)
        
        logging.info("starting GUI")
        
        # temporary hotkey to close window during dev
        self.window.bind("<Escape>", self.end_fullscreen)
        
        # prevents code after this point
        self.window.mainloop()
        
    def end_fullscreen(self, event):
        self.window.attributes("-fullscreen", False)

logging.basicConfig(level=logging.INFO)

GUI()



