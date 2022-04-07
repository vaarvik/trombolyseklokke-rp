from operator import mod
from tkinter import *
import logging
import math
import json
from tinydb import TinyDB, where
from datetime import datetime

class Text:
    def __init__(self, text, x, y, window, size=18, centerAnchor=False):
        self.x = x
        self.y = y
        self.size = size
        self.centerAnchor = centerAnchor
        self.window = window
        self.label = Label(window, text=text, fg="#000000", bg="#000000", font=("Minion Pro Med", size))
        self.label.place(x=self.x, y=self.y)
        window.after(10, lambda:self.update(text)) # Update with correct color and position after label has been initialized

    def update(self, text):
        self.label.config(text=text, fg="#FFFFFF")
        if(self.centerAnchor):
            self.label.place(x=self.x - self.label.winfo_width() / 2, y=self.y - self.label.winfo_height() / 2)
        else:
            self.label.place(x=self.x, y=self.y)

class Timer:
    def __init__(self, gui, x, y, textSize, centerAnchor=False):
        logging.info("creating Timer")
        self.totalSeconds = 0
        self.GUIWindow = gui.window
        self.gui = gui
        self.text = Text(text=self.format_time(), size=textSize, x=x, y=y, window=self.GUIWindow, centerAnchor=centerAnchor)

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

    def update_timer(self):
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
    def update_timers():
        for timer in Timer.timers:
            timer.update_timer()

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
        self.canvas = Canvas(self.gui.window, width=width, height=height - border, bd=0, highlightthickness=border, highlightbackground="#555555", relief='ridge', bg=bg)
        self.canvas.place(x=self.x, y=self.y)
        self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.fill = self.canvas.create_rectangle(0, 0, self.calc_passed_width(), self.height, fill="#005AE0", outline="", width=0)

        ProgressBar.bars.append(self)

    def calc_passed_width(self):
        if(self.passedSeconds >= self.maxSeconds):
            return self.width * self.maxSeconds

        currentlyPassed = (self.width / self.maxSeconds) * self.passedSeconds
        return currentlyPassed

    def incrementPassedTime(self, time):
        self.passedSeconds += time / 1000
        self.canvas.coords(self.fill, 0, 0, self.calc_passed_width(), self.height)

    def update(self):
        Controller.update(self.incrementPassedTime)

    def reset(self):
        self.passedSeconds = 0

    @staticmethod
    def reset_bars():
        for bar in ProgressBar.bars:
            bar.reset()

    @staticmethod
    def update_bars():
        for bar in ProgressBar.bars:
            bar.update()

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

    def save_time(self, currSequence):
        self.times.append({
            "seconds": self.totalSeconds,
            "name": currSequence["name"]
        })

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
            sequenceTimer.save_time(Controller.sequences[Controller.currSequence])
            Controller.pause()
            Controller.isDone = True

            # Store session data in tiny DB
            Controller.db.createEntry(Controller.startTimestamp, sequenceTimer.times, totalTimer.totalSeconds)
            # This is where we'll make the GUI show the final results
            return True

        # Go to the next sequence when program is not done and there is another sequence available
        sequenceTimer.save_time(Controller.sequences[Controller.currSequence])
        sequenceProgressbar.reset()
        sequenceTimer.clear_timer()
        Controller.currSequence += 1

    @staticmethod
    def reset():
        Controller.isDone = False
        Controller.isRunning = False
        Controller.hasStarted = False
        Timer.reset_timers()
        ProgressBar.reset_bars()
        Timer.update_timers()
        ProgressBar.update_bars()
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
            Timer.update_timers()
            ProgressBar.update_bars()

    @staticmethod
    def pause():
        Controller.isRunning = False


    @staticmethod
    def stop():
        if(Controller.isRunning):
            return Controller.pause()

        Controller.reset()

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

        self.totalTimer = Timer(self, 10, 10, 60)
        self.sequenceTimer = SequenceTimer(self, self.width / 2, self.height / 2, 60 * 4, True)
        self.totalProgressbar = ProgressBar(self, 0, 4, self.width, 4, Controller.totalTime, "grey")
        self.sequenceProgressbar = SequenceProgressBar(self, self.width / 2 - 800 / 2, self.height / 1.33 - 50 / 2, 800, 50, 0, border=5)

        self.add_btn(text="Stop", color="#FF0000", x=50, y=300, command=lambda:[Controller.stop()])
        self.add_btn(text="Start", color="#FFFFFF", x=50, y=500, command=lambda:[Controller.start()])
        self.add_btn(text="Next", color="#FFFFFF", x=50, y=600, command=lambda:[Controller.next_sequence(self.sequenceTimer, self.totalTimer, self.sequenceProgressbar)])

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
