from timer import Timer
from recovery_schedule import Phase
from diagnosis import Diagnose
from user import User, Dbb


import sqlite3


from datetime import datetime, date, timedelta
import time

import sys
import os

from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


# connect to db
# conn = sqlite3.connect("fingers.db")
# db = conn.cursor()

WIN_WID = 400
WIN_HEI = 500

# TO DO
# login/out as menu option
# get diagnosis in gui
# improve recovery sched data
# fix bugs
# clean up code
# remodelling phases, open 1 finger, 4 finger closed
# break down mainwindow into smaller units
# clean folders


def main():

    root = Tk()
    root.title("Finger Rehabilitator")
    # root.minsize(200, 200)
    root.geometry(f"{WIN_WID+20}x{WIN_HEI}-5-5")
    app = MainWindow(root)
    # root.bind('<Key-Esc>', exit_script())
    # create_tables()
    root.mainloop()
    exit_script(app.user.dbb)


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.logged_in = False

        self.user_name = StringVar()
        # self.user_name.set(None)
        self.user_note = StringVar()
        self.user_note.set("No one logged in")

        self.diagnosis_info = StringVar()
        self.diagnosis_info.set("Login to see your diagnosis information")
        self.recovery_info = StringVar()
        self.progress_info = StringVar()
        self.progress_info.set("Login to see your recovery progress")
        self.progress_graph_path = "0plot.png"
        self.progress_graph_image = None
        self.activity_info = StringVar()
        self.activity_info.set("Login to record activity")

        self.mainframe()
        self.login_window()
        self.notebook()

        self.warmed_up = False

    def mainframe(self):
        self.mainframe = ttk.Frame(self.root, padding=4)
        self.mainframe.grid(column=0, row=0, sticky=(N, E, S, W))
        self.root.columnconfigure(
            0,
            weight=1,
        )
        self.root.rowconfigure(0, weight=1)
        mainframe_label = ttk.Label(
            self.mainframe, text="Rehabilitate your finger injury", justify="center"
        )
        mainframe_label.grid(column=0, row=1, sticky=(N, E, S, W))

    def notebook(self):
        self.notebook = ttk.Notebook(self.mainframe)
        self.notebook.grid(column=0, row=4, sticky=(N, E, S, W), padx=5, pady=5)
        self.mainframe.rowconfigure(4, weight=10)
        self.notebook_diagnosis()
        self.notebook_progress()
        self.notebook_graph()
        self.notebook_activity()

    def notebook_diagnosis(self):
        self.notebook_diagnosis = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_diagnosis, text="Diagnosis")
        diagnosis_label = ttk.Label(
            self.notebook_diagnosis,
            textvariable=self.diagnosis_info,
            wraplength=WIN_WID,
        )
        diagnosis_label.grid(column=0, row=0, sticky=(N, E, S, W))
        recovery_label = ttk.Label(
            self.notebook_diagnosis, textvariable=self.recovery_info, wraplength=WIN_WID
        )
        recovery_label.grid(column=0, row=2, sticky=(N, E, S, W))

    def notebook_progress(self):
        self.notebook_progress = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_progress, text="Progress")
        progress_label = ttk.Label(
            self.notebook_progress, textvariable=self.progress_info, wraplength=WIN_WID
        )
        progress_label.grid(column=0, row=0, sticky=(N, E, S, W))
        self.stage_info = StringVar()
        stage_label = ttk.Label(
            self.notebook_progress, textvariable=self.stage_info, wraplength=WIN_WID
        )
        stage_label.grid(column=0, row=1)

    def notebook_graph(self):
        self.notebook_graph = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_graph, text="Graph")
        self.add_graph()

    def add_graph(self):
        self.graph_info = StringVar()
        self.graph_label = ttk.Label(self.notebook_graph, textvariable=self.graph_info)

        if self.user:
            try:
                tmp = self.user.graph
                if os.path.isfile(tmp):
                    self.progress_graph_path = str(tmp)
            except:
                    print("image does not exist")
                    self.graph_label.grid(row=0, column=0)
                    self.graph_info.set("This is a sample graph")

            try:
                i = Image.open(self.progress_graph_path)
                i = i.resize((WIN_WID, WIN_WID))
                self.progress_graph_image = ImageTk.PhotoImage(i)
            except:
                print("problem getting graph")
            self.graph_img = ttk.Label(
                self.notebook_graph, image=self.progress_graph_image
            )
            self.graph_img.grid(column=0, row=2, sticky=(N, E, S, W))

    def notebook_activity(self):
        self.notebook_activity = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_activity, text="Activity")
        activity_label = ttk.Label(
            self.notebook_activity, textvariable=self.activity_info, wraplength=WIN_WID
        )
        activity_label.grid(column=0, row=0, sticky=(N, E, S, W))

    def login_window(self):
        self.login_window = ttk.Frame(
            self.mainframe, borderwidth=5, relief="ridge", width=200, height=100
        )
        self.login_window.grid(column=0, row=2, sticky=(N, E, S, W))
        self.mainframe.columnconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=1)
        login_label = ttk.Label(self.login_window, text="User Login")
        login_label.grid(column=0, row=0, sticky=(N, E, S, W))
        user_name_entry = ttk.Entry(self.login_window, textvariable=self.user_name)
        user_name_entry.grid(column=0, row=1, sticky=(N, E, S, W), padx=5, pady=5)
        user_name_entry.focus()
        login_button = ttk.Button(
            self.login_window, text="Login", command=lambda: self.login_check()
        )
        login_button.grid(column=0, row=2, sticky=(N, E, W))
        self.root.bind("<Return>", lambda e: self.login_check())
        user_label = ttk.Label(self.login_window, textvariable=self.user_note)
        user_label.grid(column=0, row=3, sticky=(N, E, S, W))

    def login_check(self, *args):
        # try:
        username = self.user_name.get()
        if username != None:
            self.user = User(username)
            if not self.user.lookup_user():
                diagnosis = Diagnose(self)  # change self to frame  # get diagnosis
            else:
                self.populate_info()
                self.logged_in = True

    def populate_info(self):
        self.check_stage()
        self.user_note.set(f"{self.user.name.title()} Logged in")
        if not self.user:
            ...
        self.diagnosis_info.set(str(self.user))
        self.recovery_info.set(str(self.user.recovery_sched()))
        self.progress_info.set(str(self.user.progress_info()))
        self.stage_info.set(str(self.user.rehab_sched()))
        # except:
        #    print("problem getting user info")
        self.add_graph()

        self.baseline_button = ttk.Button(
            self.notebook_activity,
            text="Record Baseline",
            command=lambda: self.new_baseline(),
        )
        self.baseline_button.grid(column=0, row=2, sticky=(N, E, W))

        if "remodelling" in self.user.phase.current_phase:
            self.activity_info.set("Lets Go")
            self.activity_button = ttk.Button(
                self.notebook_activity,
                text="Record Activity",
                command=lambda: self.new_activity(),
            )
            self.activity_button.grid(column=0, row=4, sticky=(N, E, W))
        else:
            self.activity_info.set(
                f"It's too soon for you to start rehab, but you should keep up with your recovery and come back in {self.user.phase.rehab_start_day} days to start rehab."
            )

    def new_activity(self):
        if not self.user.baseline:
            messagebox.showinfo(message="Please record a baseline first")
            return
        attempts = 10
        self.record_mode = "activity"
        self.mode_info = StringVar()
        self.hangs(attempts)

    def new_baseline(self):
        attempts = 3
        self.record_mode = "baseline"
        self.mode_info = StringVar()
        self.mode_info.set(
            f"To gauge your recovery we will need to benchmark your injured finger against the opposite (hopefully) healthy finger on your other hand.\n We will get a baseline strength for that finger now. \n Okay you're going to need your sling or hangboard, let's give it {attempts} attempts, try and hold the weight for 15 seconds"
        )
        self.hangs(attempts)

    def hangs(self, sets):
        self.notebook_recording = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_recording, text=self.record_mode.title())
        self.notebook.select(self.notebook_recording)

        self.sets = StringVar()
        self.sets.set(sets)
        self.sets_entry = ttk.Entry(self.notebook_recording, textvariable=self.sets)
        self.sets_entry.grid(column=0, row=1, sticky=(N, E, S, W), padx=5, pady=5)
        self.sets_label = ttk.Label(self.notebook_recording, text="sets")
        self.sets_label.grid(column=1, row=1, sticky=(N, S, W))

        self.seconds = StringVar()
        self.seconds.set("15")
        self.seconds_entry = ttk.Entry(
            self.notebook_recording, textvariable=self.seconds
        )
        self.seconds_entry.grid(column=0, row=2, sticky=(N, E, S, W), padx=5, pady=5)
        self.seconds_label = ttk.Label(self.notebook_recording, text="seconds")
        self.seconds_label.grid(column=1, row=2, sticky=(N, S, W))

        self.weight = StringVar()
        self.weight.set(str(round(self.user.pb * 0.8)))
        self.weight_entry = ttk.Entry(self.notebook_recording, textvariable=self.weight)
        self.weight_entry.grid(column=0, row=3, sticky=(N, E, S, W), padx=5, pady=5)
        self.weight_label = ttk.Label(self.notebook_recording, text="Kg")
        self.weight_label.grid(column=1, row=3, sticky=(N, S, W))

        self.go_button = ttk.Button(
            self.notebook_recording, text="Go", command=lambda: self.launch_activity()
        )
        self.go_button.grid(column=0, row=4, sticky=(N, E, W))
        self.go_button.focus()

        self.root.bind("<Return>", lambda e: self.launch_activity())

        self.hang_label = ttk.Label(
            self.notebook_recording, textvariable=self.mode_info, wraplength=WIN_WID
        )
        self.hang_label.grid(column=0, row=5, columnspan=2, sticky=(N, E, S, W))

    def launch_activity(self):

        if not self.warmed_up:
            self.warmed_up = self.warmup()

        self.success = 0
        self.max_wt = 0
        self.log = {
            "rehab_stage": self.user.rehab_stage,
        }
        self.rep = 0
        self.attempts = int(self.sets.get())
        self.seconds = int(self.seconds.get())
        self.sets_entry.grid_remove()
        self.sets_label.grid_remove()
        rest_label = ttk.Label(self.notebook_recording, text="Rest, 2-3 mins").grid(
            column=0, row=0
        )
        self.seconds_entry.grid_remove()
        self.seconds_label.grid_remove()
        self.go_button.config(text="New Weight", command=lambda: self.perform_rep())
        self.perform_rep()

    def perform_rep(self):
        # bind enter
        while self.rep < self.attempts:
            try:
                wt = float(self.weight.get())
            except ValueError:
                print("problem getting weight")
            timer = Timer(self.notebook_recording, self.seconds)
            tick = timer.success
            timer.win.destroy()
            if tick:
                self.success += 1
                if wt > self.max_wt:
                    self.max_wt = wt
                else:
                    messagebox.showinfo(
                        message="Well done, consider adding a little bit of weight"
                    )
            self.log.update({f"set {self.rep + 1}": {"weight": wt, "success": tick}})
            self.rep += 1
        self.notebook_recording.destroy()
        if self.record_mode == "activity":
            try:
                self.success_rate = (self.attempts / self.success) * 100
            except ZeroDivisionError():
                self.success_rate = 0
            if self.max_wt > self.user.pb:
                messagebox.showinfo(
                    message=(
                        f"Well Done, thats a new P.B, your old P.B was {self.user.pb}kg, your new P.B is {self.max_wt}kg"
                    )
                )
                self.user.pb = self.max_wt
                self.check_stage()
                self.user.dbb.update_pb()
            self.user.dbb.log_rehab(
                {
                    "max weight": self.max_wt,
                    "success rate": self.success_rate,
                    "time": self.seconds,
                    "sets": self.attempts,
                    "workout log": self.log,
                }
            )
        else:
            if self.max_wt > self.user.baseline:
                self.user.baseline = self.max_wt
                self.user.dbb.update_baseline()
        self.user.print_graph(show=False)
        self.populate_info()

    def warmup(self):
        return (
            messagebox.showinfo(
                message="To warm up, do a 2-5 minutes pulse raiser activity e.g Skipping, followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals."
            )
            == "ok"
        )

    def check_stage(self):
        if self.user.pb >= self.user.baseline:
            messagebox.showinfo(
                message=(
                    f"Nice one, you've caught up to your baseline, it's time to move on to the next phase of recovery."
                )
            )
            self.user.rehab_sched()


def exit_script(dbb):
    dbb.conn.close()
    sys.exit("Thanks for coming")


if __name__ == "__main__":
    main()
