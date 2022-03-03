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
    def __init__(self, gui, x, y):
        logging.info("creating Timer")
        self.totalSeconds = 0
        self.GUIWindow = gui.window
        self.gui = gui
        self.text = Text(text=self.totalSeconds, x=x, y=y, window=self.GUIWindow)
        self.paused = True
        
        Timer.timers.append(self)
        
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
        if(not self.paused):
            self.GUIWindow.after(1000, self.update_timer)
    
    def start_timer(self):
        if(self.paused):
            self.paused = False
            self.update_timer()
        
    def reset_timer(self):
        self.totalSeconds = 0
    
    def pause_timer(self):
        self.paused = True
        
    def reset_timers():        
        for timer in Timer.timers:
            timer.reset_timer()
            timer.pause_timer()
        
    def pause_timers():        
        for timer in Timer.timers:
            timer.pause_timer()
        
    def start_timers():        
        for timer in Timer.timers:
            timer.start_timer()
    
# Static Timer variables
Timer.timers = []

# Static Timer methods
Timer.reset_timers = staticmethod(Timer.reset_timers)
Timer.pause_timers = staticmethod(Timer.pause_timers)

class GUI:
    def __init__(self):
        self.window = Tk()
        self.title = "Trombolyseklokke"
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight() 
        self.totalTimer = Timer(self, 10, 10)
        self.sequeceTimer = Timer(self, self.width / 2, self.height / 2)
        self.add_btn(text="Stop", color="#FF0000", x=50, y=50, command=Timer.reset_timers)
        self.add_btn(text="Pause", color="#FFFF00", x=100, y=100, command=Timer.pause_timers)
        self.add_btn(text="Start", color="#FFFF00", x=150, y=150, command=Timer.start_timers)
        
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
        
    def add_btn(self, text, color, x, y, command):
        btn = Button(self.window, text=text, command=command, bg=color)
        btn.place(x=x, y=y)

logging.basicConfig(level=logging.INFO)

GUI()



