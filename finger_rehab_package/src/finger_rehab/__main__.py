from timer import Timer
from recovery_schedule import Phase
from diagnosis import Diagnose
from user import User
from databaser import Dbb
from activity import Activitywindow

import sqlite3

from datetime import datetime, date, timedelta
import time

import sys
import os

from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


WIN_WID = 400
WIN_HEI = 500

# TO DO
# login/out as menu option
# improve  data
# catch exceptions
# clean folders

# progress info


def main():

    root = Tk()
    root.title("Finger Rehabilitator")
    # root.minsize(200, 200)
    root.geometry(f"{WIN_WID+20}x{WIN_HEI}-5-5")
    app = MainWindow(root)

    root.mainloop()
    app.exit_script()


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.exit_script())
        self.root.bind('<Escape>', lambda e: self.exit_script())
        self.user = None
        self.set_vars()
        self.mainframe()
        self.login_window()
        self.notebook()
        self.WIN_WID = WIN_WID

    def set_vars(self):
        self.logged_in = False
        self.warmed_up = False
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

    def mainframe(self):
        self.mainframe = ttk.Frame(self.root, padding=4)
        self.mainframe.grid(column=0, row=0, sticky=(N, E, S, W))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        #mainframe_label = ttk.Label(self.mainframe, text="Rehabilitate your finger injury", justify="center")
        #mainframe_label.grid(column=0, row=1, sticky=(N, E, S, W))

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

    def notebook_activity(self):
        self.notebook_activity = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_activity, text="Activity")
        activity_label = ttk.Label(
            self.notebook_activity, textvariable=self.activity_info, wraplength=WIN_WID
        )
        activity_label.grid(column=0, row=0, sticky=(N, E, S, W))

    def login_window(self):
        self.login_window = ttk.Frame(
            self.mainframe, borderwidth=5, relief="ridge", width=WIN_WID,
        )
        self.login_window.grid(column=0, row=1, sticky=(N, E, S, W))
        #self.mainframe.columnconfigure(0, weight=0)
        #self.mainframe.rowconfigure(1, weight=1)
        #login_label = ttk.Label(self.login_window, text="User Login")
        #login_label.grid(column=0, row=0, sticky=(N, E, S, W))
        user_name_entry = ttk.Entry(self.login_window, textvariable=self.user_name)
        user_name_entry.grid(column=0, row=0, sticky=(N, E, S, W), padx=5, pady=5)
        user_name_entry.focus()
        login_button = ttk.Button(
            self.login_window, text="Login", command=lambda: self.login_check()
        )
        login_button.grid(column=1, row=0, sticky=(N, E, S, W), padx=5, pady=5)
        self.root.bind("<Return>", lambda e: self.login_check())
        user_label = ttk.Label(self.login_window, textvariable=self.user_note, justify='center')
        user_label.grid(column=0, row=1, sticky=(N, E, S, W), columnspan=2)

    def login_check(self, *args):
        # try:
        if self.logged_in:
            self.set_vars()
        username = self.user_name.get()
        try:
            self.user = User(username)
        except ValueError:
            self.user_note.set("Enter valid user name")
            return
        if not self.user.exists:
            diagnosis = Diagnose(self)  # change self to frame  # get diagnosis
        else:
            self.populate_info()
            self.logged_in = True

    def check_stage(self):
        if self.user.pb >= self.user.baseline and self.user.baseline > 0 and self.user.rehab_stage < 3:
            messagebox.showinfo(
                message=(
                    f"Nice one, you've caught up to your baseline, it's time to move on to the next phase of recovery."
                )
            )
            self.user.rehab_sched()

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
        self.activity_info.set("Log some rehab or record a baseline.")
        self.activity = Activitywindow(self.user, self, self.notebook_activity, width=WIN_WID)
    
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

    def exit_script(self):
        if self.user:
            self.user.dbb.conn.close()
        if self.root:
            self.root.destroy()
        sys.exit("Thanks for coming")


if __name__ == "__main__":
    main()