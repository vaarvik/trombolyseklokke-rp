from operator import mod
from tkinter import *
import logging
import math
import json
from tinydb import TinyDB, where
from datetime import datetime

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

        # Init for children
        self.init()

        Timer.timers.append(self)

    # Used when initializing classes that inherits this class
    def init(self):
        False

    def format_time(self):
        seconds = math.floor(self.totalSeconds % 60)
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

    def incrementSeconds(self, time):
        self.totalSeconds += time / 1000

    def start_timer(self):
        if(Controller.isRunning):
            Controller.update(lambda time:[self.incrementSeconds(time), self.text.update(self.format_time())])
        else:
            self.text.update(self.format_time())

    def reset_timer(self):
        self.totalSeconds = 0

    @staticmethod
    def reset_timers():
        for timer in Timer.timers:
            timer.reset_timer()

    @staticmethod
    def start_timers():
        for timer in Timer.timers:
            timer.start_timer()

# Static Timer variables
Timer.timers = []

class ProgressBar:
    def __init__(self, gui, x, y, width, height, maxSeconds, bg="black", border=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.maxSeconds = maxSeconds
        self.gui = gui
        self.passedSeconds = 0
        self.canvas = Canvas(self.gui.window, width=width, height=height - border, bd=border, highlightthickness=0, relief='ridge', bg=bg)
        self.canvas.place(x=self.x, y=self.y)
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="", outline="grey", width=0)
        self.fill = self.canvas.create_rectangle(0, 0, self.calc_passed_width(), self.height, fill="blue", outline="", width=0)

        ProgressBar.bars.append(self)

    def calc_passed_width(self):
        if(self.passedSeconds >= self.maxSeconds):
            return self.width * self.maxSeconds

        currentlyPassed = (self.width / self.maxSeconds) * self.passedSeconds
        return currentlyPassed

    def incrementPassedTime(self, time):
        self.passedSeconds += time / 1000
        self.canvas.coords(self.fill, 0, 0, self.calc_passed_width(), self.height)

    def start(self):
        if(Controller.isRunning):
            Controller.update(self.incrementPassedTime)

    def reset(self):
        self.passedSeconds = 0

    @staticmethod
    def reset_bars():
        for bar in ProgressBar.bars:
            bar.reset()

    @staticmethod
    def start_bars():
        for bar in ProgressBar.bars:
            bar.start()

# Static ProgressBar variables
ProgressBar.bars = []

class SequenceProgressBar(ProgressBar):
    def calc_passed_width(self):
        if(self.passedSeconds >= Controller.sequences[Controller.currSequence]["seconds"]):
            return self.width * Controller.sequences[Controller.currSequence]["seconds"]

        currentlyPassed = (self.width / Controller.sequences[Controller.currSequence]["seconds"]) * self.passedSeconds
        return currentlyPassed

# SequenceTimer extends Timer
class SequenceTimer(Timer):
    def init(self):
        # Keep track of the time for each sequence
        self.times = []

    def next_sequence(self, currSequence):
        self.times.append({
            "seconds": self.totalSeconds,
            "name": currSequence["name"]
        })
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
        Controller.startTimestamp = 0
        Controller.sequences = Controller.config["sequences"]

        # Total max time
        Controller.totalTime = Controller.calc_total_time()

        Controller.isDone = False
        Controller.isRunning = False
        Controller.hasStarted = False

        # Create DB
        Controller.db = DB()

        # Start GUI
        Controller.gui = GUI()

        # preserves code running
        Controller.gui.window.mainloop()

    @staticmethod
    def calc_total_time():
        totalTime = 0

        for sequence in Controller.sequences:
            totalTime += sequence["seconds"]

        return totalTime

    @staticmethod
    def next_sequence(sequenceTimer, totalTimer, sequenceProgressbar):
        # Don't run again if process is done
        if(not Controller.isRunning):
            return False

        # Stop if currentSequence has passed the number of sequences given in the config file
        if(Controller.currSequence + 1 >= len(Controller.sequences)):
            sequenceTimer.next_sequence(Controller.sequences[Controller.currSequence])
            Controller.pause()
            Controller.isDone = True

            # Store session data in tiny DB
            Controller.db.createEntry(Controller.startTimestamp, sequenceTimer.times, totalTimer.totalSeconds)
            # This is where we'll make the GUI show the final results
            return True

        # Go to the next sequence when program is not done and there is another sequence available
        sequenceTimer.next_sequence(Controller.sequences[Controller.currSequence])
        sequenceProgressbar.reset()
        Controller.currSequence += 1

    @staticmethod
    def reset():
        Controller.isDone = False
        Controller.isRunning = False
        Controller.hasStarted = False
        Timer.reset_timers()
        ProgressBar.reset_bars()
        Controller.currSequence = 0

    @staticmethod
    def start():
        if(not Controller.isRunning and not Controller.hasStarted):
            currentDateTime = datetime.now()
            Controller.startTimestamp = datetime.timestamp(currentDateTime)

        if(not Controller.isRunning and not Controller.isDone):
            Controller.isRunning = True
            Controller.isDone = False
            Controller.hasStarted = True
            Timer.start_timers()
            ProgressBar.start_bars()

    @staticmethod
    def pause():
        Controller.isRunning = False

    @staticmethod
    def update(cb=lambda time:[]):
        timeInterval = 50
        if(not Controller.isRunning):
            cb(timeInterval)
            Controller.gui.window.update()
            return False

        cb(timeInterval)
        Controller.gui.window.after(timeInterval, lambda:Controller.update(cb))

class GUI:
    def __init__(self):
        self.window = Tk()
        self.title = "Trombolyseklokke"
        self.width = self.window.winfo_screenwidth()
        self.height = self.window.winfo_screenheight()
        self.totalTimer = Timer(self, 10, 10)
        self.sequenceTimer = SequenceTimer(self, self.width / 2, self.height / 2)
        self.totalProgressbar = ProgressBar(self, 0, 2, self.width, 2, Controller.totalTime, "grey")
        self.sequenceProgressbar = SequenceProgressBar(self, self.width / 2 - 600 / 2, self.height / 2 - 40 / 2, 600, 40, 0, border=4)
        self.add_btn(text="Stop", color="#FF0000", x=50, y=50, command=lambda:[Controller.reset()])
        self.add_btn(text="Pause", color="#FFFF00", x=100, y=100, command=lambda:[Controller.pause()])
        self.add_btn(text="Start", color="#FFFFFF", x=150, y=150, command=lambda:[Controller.start()])
        self.add_btn(text="Next", color="#FFFFFF", x=200, y=200, command=lambda:[Controller.next_sequence(self.sequenceTimer, self.totalTimer, self.sequenceProgressbar)])

        # config
        logging.info("configuring GUI")
        self.window.wm_title(self.title)
        self.window.configure(bg="#000000")
        self.window.attributes("-fullscreen", True)

        logging.info("starting GUI")

        # temporary hotkey to close window during dev
        self.window.bind("<Escape>", self.end_fullscreen)

    def seconds_converter(self, seconds):
        maximum = seconds * 1000 / 60
        return maximum

    def end_fullscreen(self, event):
        self.window.attributes("-fullscreen", False)

    def add_btn(self, text, color, x, y, command):
        btn = Button(self.window, text=text, command=command, bg=color)
        btn.place(x=x, y=y)

class DB:
    def __init__(self):
        self.db = TinyDB('db.json')

    def createEntry(self, startTimestamp, sequences, totalSeconds):
        return self.db.insert({"startTimestamp": startTimestamp, "sequences": sequences, "totalSeconds": totalSeconds})

    def getEntry(self, startTimestamp):
        return self.db.search(where("startTimestamp") == startTimestamp)

logging.basicConfig(level=logging.INFO)

Controller()
