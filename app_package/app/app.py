
from timer import Timer
from recovery_schedule import Phase

from diagnosis import Diagnose
from user import User
from activity import Activitywindow
from databaser import Dbb
import sqlite3

from datetime import datetime, date, timedelta
import time
from pathlib import Path
import sys
import os
import tkinter
from tkinter import *
from tkinter import ttk, messagebox
import PIL
from PIL import Image, ImageTk


WIN_WID = 400
WIN_HEI = 500

# TO DO

# .exe command:
# pyinstaller --onefile --windowed --hiddenimport=babel.numbers, --hiddenimport=_cffi_backend -i"images\fingers.ico" app/app.py

# finger.ico = Iconsmind-Outline-Finger License: Linkware (Backlink to http://www.iconsmind.com required)


def main():

    root = Tk()
    root.title("Finger Rehabilitator")
    # root.minsize(200, 200)
    root.geometry(f"{WIN_WID+20}x{WIN_HEI}-5-5")
    app = MainWindow(root)

    root.mainloop()
    app.exit_script()


class MainWindow:
    WIN_WID = WIN_WID

    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.exit_script())
        self.root.bind("<Escape>", lambda e: self.exit_script())

        self.user = None
        self.set_vars()

        self.create_mainframe()
        self.create_menu()
        self.create_login_window()
        self.create_notebook()

    def create_menu(self):
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.menu_options = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.menu_options, label="Options")
        self.menu_options.add_command(
            label="Change User", command=lambda: self.__init__(self.root)
        )
        self.menu_options.add_command(
            label="Refresh",
            command=lambda: self.populate_info()
            if self.logged_in
            else self.__init__(self.root),
        )

    def set_vars(self):
        self.logged_in = False
        self.warmed_up = False
        self.user_name = StringVar()
        self.user_note = StringVar()
        self.user_note.set("No one logged in")
        self.diagnosis_info = StringVar()
        self.diagnosis_info.set("Login to see your diagnosis information")
        self.recovery_info = StringVar()
        self.progress_info = StringVar()
        self.progress_info.set("Login to see your recovery progress")
        self.progress_graph_path = Path.cwd() / ("graphs") / "0plot.png"#Path.cwd().parent / ("graphs") / "0plot.png"
        self.progress_graph_image = None
        self.activity_info = StringVar()
        self.activity_info.set("Login to record activity")

    def create_mainframe(self):
        self.mainframe = ttk.Frame(self.root, padding=4, width=WIN_WID)
        self.mainframe.grid(column=0, row=0, sticky=(N, E, S, W))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.mainframe, width=WIN_WID)
        self.notebook.grid(column=0, row=4, sticky=(N, E, S, W), padx=5, pady=5)
        self.mainframe.rowconfigure(4, weight=10)
        self.create_notebook_diagnosis()
        self.create_notebook_progress()
        self.create_notebook_graph()
        self.create_notebook_activity()

    def create_notebook_diagnosis(self):
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

    def create_notebook_progress(self):
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
        stage_btn = ttk.Button(self.notebook_progress, text="Change rehab stage.", command= lambda: self.change_stage())
        stage_btn.grid(column=0, row=2, padx=10, pady=10)

    def create_notebook_graph(self):
        self.notebook_graph = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_graph, text="Graph")
        self.add_graph()

    def create_notebook_activity(self):
        self.notebook_activity = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_activity, text="Activity")
        activity_label = ttk.Label(
            self.notebook_activity, textvariable=self.activity_info, wraplength=WIN_WID
        )
        activity_label.grid(column=0, row=0, sticky=(N, E, S, W))

    def create_login_window(self):
        self.login_window = ttk.Frame(
            self.mainframe,
            borderwidth=5,
            relief="ridge",
            width=WIN_WID,
        )
        self.login_window.grid(column=0, row=1, sticky=(N, E, S, W))
        # self.mainframe.columnconfigure(0, weight=0)
        # self.mainframe.rowconfigure(1, weight=1)
        # login_label = ttk.Label(self.login_window, text="User Login")
        # login_label.grid(column=0, row=0, sticky=(N, E, S, W))
        user_name_entry = ttk.Entry(self.login_window, textvariable=self.user_name)
        user_name_entry.grid(column=0, row=0, sticky=(N, E, S, W), padx=5, pady=5)
        user_name_entry.focus()
        login_button = ttk.Button(
            self.login_window, text="Select User", command=lambda: self.login_check()
        )
        login_button.grid(column=1, row=0, sticky=(N, E, S, W), padx=5, pady=5)
        self.root.bind("<Return>", lambda e: self.login_check())
        user_label = ttk.Label(
            self.login_window, textvariable=self.user_note, justify="center"
        )
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
            dg = Diagnose(self)
            dg.get_diagnosis()  # change self to frame  # get diagnosis
        else:
            self.populate_info()
            self.logged_in = True
        self.login_window.grid_forget()

    def check_stage(self):
        if (
            self.user.pb >= self.user.baseline
            and self.user.baseline > 0
            and self.user.rehab_stage < len(Phase.stages)-1
        ):
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
        self.activity = Activitywindow(
            self.user, self, self.notebook_activity, width=WIN_WID
        )

    def add_graph(self):
        self.graph_info = StringVar()
        self.graph_label = ttk.Label(self.notebook_graph, textvariable=self.graph_info)

        if self.user:
            self.user.print_graph(show=False)
            try:
                tmp = self.user.path

                if os.path.isfile(tmp):
                    self.progress_graph_path = str(tmp)
            except:
                print(f"{self.user.path} does not exist")
                self.graph_label.grid(row=0, column=0)
                self.graph_info.set("This is a sample graph")
                self.progress_graph_path = Path.cwd().parent / ("graphs") / "0plot.png"

            try:
                with Image.open(self.progress_graph_path) as i:
                    i = i.resize((WIN_WID, WIN_WID))
                    self.progress_graph_image = ImageTk.PhotoImage(i)
            except:
                print(f"couldn't open {self.progress_graph_path}")

                return 1

            self.graph_img = ttk.Label(
                self.notebook_graph, image=self.progress_graph_image
            )
            self.graph_img.grid(column=0, row=2, sticky=(N, E, S, W))

    def change_stage(self):
        f0 = ttk.Frame(self.notebook_progress, borderwidth=5, relief='ridge',
            )
        f0.grid(column=0, row=2, padx=5, pady=5, sticky=NSEW)
        def my_stage():
            try:
                self.user.rehab_stage = int(self.s.get())
            except:
                print("problem changing stage")
                return
            f0.grid_forget()
            self.populate_info()
            self.user.baseline = 0

        def reset_stage():
            my_stage()
            self.user.dbb.update_stage()
            self.user.dbb.update_baseline()
            

        self.s = IntVar()
        self.s.set(self.user.rehab_stage)
        r_dict = {}
        for num, stage in enumerate(Phase.stages):
            r_dict[stage] = ttk.Radiobutton(f0 ,text=Phase.stages[stage][0].title(), variable=self.s, value=num)
            r_dict[stage].grid(column=0, row=num, columnspan=2, sticky=W)


        b1 = ttk.Button(f0, text="Temporarily change stage", command=lambda: my_stage())
        b1.grid(
            row=len(r_dict.keys()),
            column=0,
        )
        b2 = ttk.Button(f0, text="Permanently change stage", command=lambda: reset_stage())
        b2.grid(
            row=len(r_dict.keys()),
            column=1,
        )
        


    def exit_script(self):
        if self.user:
            self.user.dbb.conn.close()
        if self.root:
            self.root.destroy()
        sys.exit("Thanks for coming")


if __name__ == "__main__":
    main()
