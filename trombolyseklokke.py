from tkinter import *
import logging
import time

class Timer:
    def __init__(self, gui):
        logging.info("creating Timer")
        self.totalSeconds = 0
        self.GUIWindow = gui.window
        self.gui = gui
        self.update_text()
        self.update_timer()
        
    def update_text(self):
        label = Label(self.GUIWindow, text=self.totalSeconds, fg="#FFFFFF", bg="#000000", font=("Helvetica", 18))
        label.place(x=self.gui.width / 2, y=self.gui.height / 2)
    
    def update_timer(self):
        self.totalSeconds += 1
        self.update_text()
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



