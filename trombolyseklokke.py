from tkinter import *
import logging
import time
import math
import json
from tinydb import TinyDB, where

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

        # Init for children
        self.init()

        Timer.timers.append(self)

    def init(self):
        False

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
        if(not self.paused):
            self.totalSeconds += 1
            self.GUIWindow.after(1000, self.update_timer)

        self.text.update(self.format_time())

    def start_timer(self):
        if(self.paused):
            self.paused = False
            self.update_timer()

    def reset_timer(self):
        self.totalSeconds = 0

    def pause_timer(self):
        self.paused = True

    @staticmethod
    def reset_timers():
        for timer in Timer.timers:
            timer.reset_timer()
            timer.pause_timer()

    @staticmethod
    def pause_timers():
        for timer in Timer.timers:
            timer.pause_timer()

    @staticmethod
    def start_timers():
        for timer in Timer.timers:
            timer.start_timer()

# Static Timer variables
Timer.timers = []

# SequenceTimer extends Timer
class SequenceTimer(Timer):
    def init(self):
        # Keep track of the time for each sequence
        self.times = []

    def next_sequence(self):
        self.times.append(self.totalSeconds)
        self.clear_timer()

    def clear_timer(self):
        self.totalSeconds = 0

    def reset_timer(self):
        self.clear_timer()
        self.times = []

# Static Controller class
class Controller:
    def __init__(self):
        # Read JSON config file
        configFile = open("./config.json", encoding="utf-8")
        Controller.config = json.load(configFile)
        configFile.close()

        Controller.currSequence = 0
        Controller.sequences = Controller.config["sequences"]

        # Total max time
        Controller.totalTime = Controller.calc_total_time()

        Controller.done = False

        # Start GUI
        GUI()

    @staticmethod
    def calc_total_time():
        totalTime = 0

        for sequence in Controller.sequences:
            totalTime += sequence["seconds"]

        return totalTime

    @staticmethod
    def next_sequence(sequeceTimer):
        # Don't run again if process is done
        if(Controller.done):
            return False

        # Stop if currentSequence has passed the number of sequences given in the config file
        if(Controller.currSequence + 1 >= len(Controller.sequences)):
            sequeceTimer.next_sequence()
            Timer.pause_timers()
            Controller.done = True
            # This is where we'll make the GUI show the final results
            return print("done")

        # Go to the next sequence when program is not done and there is another sequence available
        sequeceTimer.next_sequence()
        Controller.currSequence += 1

    @staticmethod
    def reset():
        Timer.reset_timers()
        Controller.currSequence = 0
        Controller.done = False

class GUI:
    def __init__(self):
        self.window = Tk()
        self.title = "Trombolyseklokke"
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()
        self.totalTimer = Timer(self, 10, 10)
        self.sequeceTimer = SequenceTimer(self, self.width / 2, self.height / 2)
        self.add_btn(text="Stop", color="#FF0000", x=50, y=50, command=Controller.reset)
        self.add_btn(text="Pause", color="#FFFF00", x=100, y=100, command=Timer.pause_timers)
        self.add_btn(text="Start", color="#FFFFFF", x=150, y=150, command=Timer.start_timers)
        self.add_btn(text="Next", color="#FFFFFF", x=200, y=200, command=self.next_sequence)

        Text(text=Controller.totalTime, x=500, y=500, window=self.window)

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

    def next_sequence(self):
        Controller.next_sequence(self.sequeceTimer)

class DB:
    def __init__(self):
        self.db = TinyDB('db.json')
        return self.db

    def createEntry(self, startTimestamp, sequences, totalSeconds):
        return self.db.insert({"startTimestamp": startTimestamp, "sequences": sequences, "totalSeconds": totalSeconds})

    def getEntry(self, startTimestamp):
        return self.db.search(where("startTimestamp") == startTimestamp)

logging.basicConfig(level=logging.INFO)

Controller()
