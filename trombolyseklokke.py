from operator import mod
from tkinter import *
import logging
import math
import json
from tinydb import TinyDB, where
from datetime import datetime
import RPi.GPIO as GPIO

class Text:
    def __init__(self, text, x, y, window, size=18, anchor="start"):
        self.x = x
        self.y = y
        self.size = size
        self.anchor = anchor
        self.window = window
        self.label = Label(window, text=text, fg="#000000", bg="#000000", font=("Minion Pro Med", size))
        self.label.place(x=self.x, y=self.y)
        self.update(text)

    def update(self, text, flash=False):
        self.text = text
        if(flash):
            self.label.config(text=self.text, fg="#000000")
        else:
            self.label.config(text=self.text)
        self.window.after(500, lambda:self.position()) # Update with correct color and position after label has been initialized

    def position(self):
        self.label.config(text=self.text, fg="#FFFFFF")
        if(self.anchor == "center"):
            self.label.place(x=self.x - self.label.winfo_width() / 2, y=self.y - self.label.winfo_height() / 2)
        elif(self.anchor == "center-top"):
            self.label.place(x=self.x - self.label.winfo_width() / 2, y=self.y)
        elif(self.anchor == "end"):
            self.label.place(x=self.x - self.label.winfo_width(), y=self.y - self.label.winfo_height())
        else:
            self.label.place(x=self.x, y=self.y)

class Timer:
    def __init__(self, gui, x, y, textSize, anchor=False):
        logging.info("creating Timer")
        self.totalSeconds = 0
        self.GUIWindow = gui.window
        self.gui = gui
        self.text = Text(text=self.format_time(self.totalSeconds), size=textSize, x=x, y=y, window=self.GUIWindow, anchor=anchor)

        # Init for children
        self.init()

        Timer.timers.append(self)

    # Used when initializing classes that inherits this class
    def init(self):
        False

    def format_time(self, totalSeconds):
        seconds = math.floor(totalSeconds % 60)
        minutes = math.floor(totalSeconds / 60)

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

    def update_timer(self, time):
        if(Controller.isRunning):
            self.incrementSeconds(time)
            self.text.update(self.format_time(self.totalSeconds))
        else:
            self.text.update(self.format_time(self.totalSeconds))

    def reset_timer(self):
        self.totalSeconds = 0

    @staticmethod
    def reset_timers():
        for timer in Timer.timers:
            timer.reset_timer()

    @staticmethod
    def update_timers(time):
        for timer in Timer.timers:
            timer.update_timer(time)

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

    def update(self, time):
        self.incrementPassedTime(time)

    def reset(self):
        self.passedSeconds = 0

    @staticmethod
    def reset_bars():
        for bar in ProgressBar.bars:
            bar.reset()

    @staticmethod
    def update_bars(time):
        for bar in ProgressBar.bars:
            bar.update(time)

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

class ButtonListener:
    def __init__(self, input, command):
        #while True:
            #if GPIO.input(input) == GPIO.HIGH:
        GPIO.add_event_detect(input, GPIO.RISING, callback=lambda e:command())

# Static Controller class
class Controller:
    def __init__(self):
        # Read JSON config file
        configFile = open("./config.json", encoding="utf-8")
        Controller.config = json.load(configFile)
        configFile.close()

        Controller.currSequence = 0
        Controller.month = 0
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

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)


        #ButtonListener(27, lambda:[Controller.next_sequence()])
        ButtonListener(13, lambda:[Controller.start()])
        #ButtonListener(25, lambda:[Controller.stop()])

        def on_next_sequence_press(channel):
            ButtonListener(Controller.next_sequence())


        GPIO.add_event_detect(27, GPIO.FALLING, callback=on_next_sequence_press, bouncetime=5000)

        def on_stop_press(channel):
            ButtonListener(Controller.stop())


        GPIO.add_event_detect(25, GPIO.FALLING, callback=on_stop_press, bouncetime=1500)
        # preserves code running
        Controller.gui.window.mainloop()

    @staticmethod
    def calc_total_time():
        totalTime = 0

        for sequence in Controller.sequences:
            totalTime += sequence["seconds"]

        return totalTime

    @staticmethod
    def next_sequence():
        # Don't run again if process is done
        if(not Controller.isRunning):
            return False

        # Stop if currentSequence has passed the number of sequences given in the config file
        if(Controller.currSequence + 1 >= len(Controller.sequences)):
            Controller.gui.sequenceTimer.save_time(Controller.sequences[Controller.currSequence])
            Controller.pause()
            Controller.isDone = True

            # Store session data in tiny DB
            Controller.db.createEntry(Controller.month, Controller.gui.sequenceTimer.times, Controller.gui.totalTimer.totalSeconds)

            Controller.gui.show_end_screen()
            return True

        # Go to the next sequence when program is not done and there is another sequence available
        Controller.gui.sequenceTimer.save_time(Controller.sequences[Controller.currSequence])
        Controller.gui.sequenceProgressbar.reset()
        Controller.gui.sequenceTimer.clear_timer()
        Controller.currSequence += 1
        Controller.gui.update()

    @staticmethod
    def reset():
        Controller.isDone = False
        Controller.isRunning = False
        Controller.hasStarted = False
        Timer.reset_timers()
        ProgressBar.reset_bars()
        Controller.update(lambda time:[Timer.update_timers(time), ProgressBar.update_bars(time)])
        Controller.currSequence = 0
        Controller.gui.update()

    @staticmethod
    def start():
        if(not Controller.isRunning and not Controller.hasStarted):
            currentDay = datetime.today()
            Controller.month = currentDay.month

        if(not Controller.isRunning and not Controller.isDone):
            Controller.isRunning = True
            Controller.isDone = False
            Controller.hasStarted = True
            Controller.update(lambda time:[Timer.update_timers(time), ProgressBar.update_bars(time)])

        if(Controller.isDone and not Controller.isRunning):
            Controller.stop()
            Controller.start()

    @staticmethod
    def pause():
        Controller.isRunning = False

    @staticmethod
    def stop():
        if(Controller.isRunning):
            return Controller.pause()

        Controller.reset()
        Controller.gui.hide_end_screen()

    @staticmethod
    def update(cb=lambda time:[]):
        timeInterval = 1000
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
        self.summaryTexts = []

        self.show_timer()

        self.overlay = Canvas(self.window, width=self.width, height=self.height, bd=0, highlightthickness=0, relief='ridge', bg="#000000")

        # config
        logging.info("configuring GUI")
        self.window.wm_title(self.title)
        self.window.configure(bg="#000000")
        self.window.attributes("-fullscreen", True)

        logging.info("starting GUI")

        # temporary hotkey to close window during dev
        self.window.bind("<Escape>", self.end_fullscreen)

    def update(self):
        self.text.update("Steg " + str(Controller.currSequence + 1) + ": " + Controller.sequences[Controller.currSequence]["name"].upper(), True)

    def end_fullscreen(self, event):
        self.window.attributes("-fullscreen", False)

    def show_end_screen(self):
        self.overlay.place(x=0, y=0)

        text = totalTimeText = Text(text="Totaltid: " + self.totalTimer.format_time(self.totalTimer.totalSeconds), size=70, x=self.width / 2, y=150, window=self.window, anchor="center-top")
        self.summaryTexts.append(text)

        for index, sequence in enumerate(self.sequenceTimer.times):
            text = Text(text=sequence["name"] + ": " + self.sequenceTimer.format_time(sequence['seconds']), size=36, x=self.width / 2, y=150 * 1.5 + (index + 1) * 100, window=self.window, anchor="center-top")
            self.summaryTexts.append(text)

        self.overlay.pack()

    def hide_end_screen(self):
        for text in self.summaryTexts:
            text.label.destroy()

        self.overlay.pack_forget()

    def show_timer(self):
        self.totalTimer = Timer(self, 10, 10, 60)
        self.sequenceTimer = SequenceTimer(self, self.width / 2, self.height / 2, 60 * 4, "center")
        self.totalProgressbar = ProgressBar(self, 0, 4, self.width, 8, Controller.totalTime, "grey")
        self.sequenceProgressbar = SequenceProgressBar(self, self.width / 2 - 800 / 2, self.height / 1.33 - 50 / 2, 800, 50, 0, border=5)

        self.text = Text(text="Steg " + str(Controller.currSequence + 1) + ": " + Controller.sequences[Controller.currSequence]["name"].upper(), size=52, x=self.width - 40, y=self.height - 40, window=self.window, anchor="end")

class DB:
    def __init__(self):
        self.db = TinyDB('db.json')

    def createEntry(self, month, sequences, totalSeconds):
        return self.db.insert({"month": month, "sequences": sequences, "totalSeconds": totalSeconds})

logging.basicConfig(level=logging.INFO)

Controller()
