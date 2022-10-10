from datetime import datetime, date, timedelta
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from recovery_schedule import Phase
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from timer import Timer


# connect to db
conn = sqlite3.connect("fingers.db")
db = conn.cursor()

WIN_WID = 400
WIN_HEI = 450

# TO DO
# login/out as menu option
# get diagnosis in gui
# improve recovery sched data
# fix bugs
# clean up code
# remodelling phases, open 1 finger, 4 finger closed


def main():

    root = Tk()
    root.title("Finger Rehabilitator")
    root.minsize(200, 200)
    root.geometry(f"{WIN_WID+100}x{WIN_HEI}-5-5")
    app = MainWindow(root)
    # root.bind('<Key-Esc>', exit_script())
    # create_tables()
    root.mainloop()
    exit_script()


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
        self.progress_graph_path = "sampleplot.png"
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
        self.root.columnconfigure(0, weight=1)
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

    def notebook_graph(self):
        self.notebook_graph = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_graph, text="Graph")
        self.add_graph()

    def add_graph(self):
        if self.user:
            try:
                tmp = self.user.graph
                if os.path.isfile(tmp):
                    self.progress_graph_path = tmp
                else:
                    print("image does not exist")
            except:
                print("problem getting graph")
            try:
                i = Image.open(self.progress_graph_path)
                i = i.resize((250, 250))
                self.progress_graph_image = ImageTk.PhotoImage(i)
            except:
                print("problem getting graph")
            self.graph_img = ttk.Label(self.notebook_graph, image=self.progress_graph_image)
            self.graph_img.grid(column=0, row=1, sticky=(N, E, S, W))

    def notebook_activity(self):
        self.notebook_activity = ttk.Frame(self.notebook)
        self.notebook.add(self.notebook_activity, text="Activity")
        activity_label = ttk.Label(
            self.notebook_activity, textvariable=self.activity_info
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
        try:
            username = self.user_name.get()
            if username != None:
                self.user = User(username)
                self.user.lookup_user()

        except:
            print("Failure on login")
            return
        self.populate_info()
        self.logged_in = True

    def populate_info(self):
        try:
            self.user_note.set(f"{self.user.name.title()} Logged in")
            if not self.user:
                ...  # get diagnosis

            self.diagnosis_info.set(str(self.user))
            self.recovery_info.set(str(self.user.recovery_sched()))
            self.progress_info.set(str(self.user.progress_info()))
        except:
            print("problem getting user info")
        self.add_graph()

        if "remodelling" in self.user.phase.current_phase:
            self.activity_info.set("Lets Go")
            self.baseline_button = ttk.Button(
                self.notebook_activity,
                text="Record Baseline",
                command=lambda: self.new_baseline(),
            )
            self.baseline_button.grid(column=0, row=2, sticky=(N, E, W))
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
            self.notebook_recording, textvariable=self.mode_info
        )
        self.hang_label.grid(
            column=0, row=5, columnspan=2, sticky=(N, E, S, W)
        )

    def launch_activity(self):
        
        if not self.warmed_up:
            self.warmed_up = self.warmup()
        self.success = 0
        self.max_wt = 0
        self.log = {}
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
        while self.rep < self.attempts:
            try:
                wt = float(self.weight.get())
            except ValueError:
                print("problem getting weight")
            print(wt)
            timer = Timer(self.notebook_recording, self.seconds)
            tick = timer.success
            timer.win.destroy()
            print(tick)
            if tick:
                self.success += 1
                if wt > self.max_wt:
                    self.max_wt = wt
                else:
                    messagebox.showinfo(
                        message="Well done, consider adding a little bit of weight"
                    )
            """if i < attempts - 1:
                messagebox.showinfo(message="Rest for 2-3 minutes")
            else:
                messagebox.showinfo(message="That's all.")"""
            self.log.update({f"set {self.rep + 1}": {"weight": wt, "success": tick}})
            print(self.rep, self.attempts)
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
                self.user.db.update_pb(self.max_wt)
            self.user.db.log_rehab(
                {
                    "max weight": self.max_wt,
                    "success rate": self.success_rate,
                    "time": self.seconds,
                    "sets": self.attempts,
                    "workout log": self.log,
                }
            )
        else:
            self.user.baseline = self.max_wt
            self.user.db.update_baseline(self.user.baseline)
        self.user.print_graph(show=False)
        self.populate_info()

    def warmup(self):
        return (
            messagebox.showinfo(
                message="To warm up, do a 2-5 minutes pulse raiser activity e.g Skipping, followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals."
            )
            == "ok"
        )


class User:
    def __init__(self, name):
        self.name = name
        self.hand = None
        self.finger = 0
        self.num = 0
        self.pulleys = {}
        self.grade = 0
        self.date = 0
        self.id = None
        self.baseline = 0
        self.pb = 0
        self.graph = f"{self.id}plot.png"
        self.lookup = 0
        self.temp = None
        self.since_inj = 0
        self.sched_exp = 0
        self.phase = None
        self.db = Db(self)

    def __str__(self):
        return f"{self.name.title()}: grade {self.grade} injury to the {self.hand}, {self.finger} digit, on {self.date}, {self.since_inj} days ago so you should be roughly {self.sched_exp*100:.2f}% recovered Your baseline strength is {self.baseline}, your current p.b is {self.pb}"

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, inj_date):
        if inj_date != 0:
            inj_date = str(inj_date)
            d_t = datetime.strptime(str(inj_date), "%Y-%m-%d").date()

            self._date = d_t

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Not Name")
        else:
            self._name = name

    def lookup_user(self):
        self.temp = self.db.lookup()
        if self.temp:
            self.login(self.temp)
        else:
            self.get_diagnosis()
            self.lookup_user()

    def login(self, existing):
        (
            self.id,
            self.name,
            self.date,
            self.grade,
            self.hand,
            self.finger,
            self.pulleys,
            self.baseline,
            self.pb,
        ) = existing
        self.since_inj = ((date.today()) - (self.date)).days
        self.phase = Phase(self.since_inj, self.grade)
        self.sched_exp = self.phase.rehab_progress / self.phase.rehab_phase_length
        self.graph = f"{self.id}plot.png"
        #self.db.self.login(existing)

    def recovery_sched(self):
        if len(self.phase.current_phase) > 1:
            return f"It's been {self.since_inj} days, you're between the {self.phase.current_phase[0]} and {self.phase.current_phase[1]} phase.\n\n If you're feeling good you should be feeling {self.phase.physical_characteristics[1]}.\n\n Otherwise you might still feel {self.phase.physical_characteristics[0]}.\n\n You should still be making sure you {self.phase.precautions[0]}.\n\n But to recover you could start to {self.phase.recovery_activities[1]}."
        else:
            return f"It's been {self.since_inj} days, you're in the {self.phase.current_phase[0]} phase.\n\n You should be feeling {self.phase.physical_characteristics[0]}.\n\n You should be making sure you {self.phase.precautions[0]}.\n\n To recover you should be {self.phase.recovery_activities[0]}."

    def get_diagnosis(self):

        # give info
        print(
            f"Hello {self.name.title()}\nLets get some information from you to help tailor your rehab. \n\nWe need to find out when you were injured, where and how bad it is.\n\nFollow the interactive prompts to fill us in..."
        )

        # get date
        while True:
            inj_date = input("Injury Date (DD/MM/YYYY) (leave blank to use now)... ")
            if not inj_date:
                self.date = date.today()
                print("Ok, i'm using today.")
                break
            else:
                try:
                    day, month, year = inj_date.strip().split("/")
                    self.date = date(int(year), int(month), int(day)).isoformat()
                    break
                except ValueError:
                    response = input(
                        "Hmm, I didn't recognise that date, Enter 'y' to try again? (or enter any key to use today)..."
                    )
                    if response == "y":
                        print(
                            "Okay, lets try again, make sure you use the specified date format (use '/' to seperate."
                        )
                        continue
                    else:
                        self.date = date.today()
                        print("Okay, i'll use today's date.")
                        break

        # hand
        while True:
            hand = (
                input("Which hand, Left or Right? (hint: type 'l' or 'r')... ")
                .lower()
                .strip()
            )
            if hand == "left" or hand == "l":
                self.hand = "left"
                break
            elif hand == "right" or hand == "r":
                self.hand = "right"
                break
            else:
                print("usage: l or r.")
                continue

        # finger
        while True:
            finger = int(
                input(
                    "Which finger is it? (where 2 is your index finger and 5 is your pinky)... "
                ).strip()
            )
            if finger in range(2, 6):
                self.finger = finger
                break
            else:
                print(
                    "usage: '2' - (index), '3' - (middle), '4' - (ring), '5' - (pinky)."
                )
                continue

        # pulleys #a1 bug
        while True:
            try:
                num = int(input("How many pulleys are affected? "))
                if num in range(1, 4):
                    self.num = num
                    for n in range(num):  # while len(user.pulleys) < user.num:
                        pulley = int(input("Pulley affected: A"))
                        if pulley in range(2, 5):
                            if pulley in self.pulleys:
                                print("You have already added, that pulley")
                            else:
                                severity = int(
                                    input(
                                        "How bad is it, on a scale of 1 to 3;\n1 - Minor Tear,\n2 - Major Tear,\n3 - Complete Rupture\nSeverity: "
                                    )
                                )
                                if severity in range(1, 4):
                                    self.pulleys[n] = {
                                        "pulley": pulley,
                                        "severity": severity,
                                    }

                    break
            except ValueError:
                print(
                    "Typically climbing related finger injuries affect between at least one and maximum three pulleys, including the A2, A3 and A4, if this doesn't describe your injury then this program will not help you, hit 'Ctrl+C' to exit the program"
                )
                continue

        # severity
        if len(self.pulleys) == 1:
            if self.pulleys[0]["severity"] == 1:
                print("You have a Grade 1 finger injury")
                self.grade = 1
            elif self.pulleys[0]["severity"] == 2:
                print("You have a Grade 2 finger injury")
                self.grade = 2
            elif self.pulleys[0]["severity"] == 3:
                print("You have a Grade 3 finger injury")
                self.grade = 3
            else:
                print("wrong number of injuries")
        elif len(self.pulleys) in range(2, 4):
            ruptures = 0
            for pulley in self.pulleys:
                if self.pulleys[pulley]["severity"] == 3:
                    ruptures += 1
            if ruptures > 1:
                print("You have a grade 4 finger injury")
                self.grade = 4
            else:
                print("You have a grade 3 finger injury")
                self.grade = 3
        print(
            "Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture or multiple pulley tears,\nGrade 4: Multiple ruptures"
        )
        self.db.diagnosis()

    def metrics_info(self):
        return (
            f"Your baseline strength is {self.baseline}, your current p.b is {self.pb}"
        )

    def print_graph(self, show=True):
        # sets, time, max_weight, success_rate, date #baseline
        results = self.db.progress()
        dates = []
        max_weights = [
            0,
        ]
        success_rates = [
            0,
        ]
        sets = [
            0,
        ]
        exp_prog = []

        for result in results:
            if len(dates) == 0:
                dates = [
                    (date.fromisoformat(result[0]) - self.date).days - 1,
                ]
            if result[3] > max_weights[-1]:

                dates.append((date.fromisoformat(result[0]) - self.date).days)
                sets.append(result[1])
                time = result[2]
                max_weights.append(result[3])
                success_rates.append(result[4])

        days = list(range(dates[0], dates[len(dates) - 1]))
        for day in days:
            exp = day / self.phase.rehab_phase_length
            exp_prog.append(self.baseline * exp)

        plt.plot(
            dates,
            max_weights,
            color="red",
            linestyle="dashed",
            linewidth=3,
            marker="*",
            markerfacecolor="green",
            markersize=10,
            label="max-weight progression",
        )
        # plt.errorbar(dates, max_weights, yerr=sets, fmt='o', ecolor='green', color='green')
        plt.axhline(y=self.baseline, color="red", linestyle="--", label="baseline")
        plt.plot(days, exp_prog, label="expected progress")

        plt.xlabel("Days Since Injury")
        plt.ylabel("Max Weight")
        plt.title("Weights over time")
        plt.legend()
        plt.savefig(f"{self.id}plot.png", bbox_inches="tight")
        if show:
            plt.show()

    def progress_info(self):
        last_sesh = self.db.last_sesh()
        if not self.baseline:
            self.test_baseline()
        try:
            progress = self.pb / self.baseline
        except ZeroDivisionError:
            progress = 0
        todays_wt = round(self.baseline * self.sched_exp)
        if self.since_inj > 2:
            if last_sesh:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury.\n\nAt this stage you might expect to be using around {todays_wt}kg ({round(self.sched_exp * 100)}% of your baseline, which was {self.baseline}kgs).\n\nYour last session was on {last_sesh[0]}, and your max was {last_sesh[1]}kg.\n\nYour personal best is {self.pb}kg, thats {(progress)*100}% of your baseline measurement, which was {self.baseline}kg\n"
            else:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury, this is your first session, try to take it really slow\n"
        else:
            return "Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days"

class Db(User):
    def __init__(self, user):
        self.id = user.id
        self.name = user.name
    
    def lookup(self):
        self.create_tables()
        info = db.execute(
            "SELECT user_id, name, injury_date, injury_grade, hand, finger, structures, baseline, pb FROM users WHERE name = ?",
            (self.name,),
        ).fetchone()
        if info:
            self.login(info)
            return info
        else:
            return False

    def progress(self):
        return db.execute(
            "SELECT activity_date, sets, time, max_weight, success_rate FROM rehab WHERE user_id = ?",
            (self.id,),
        ).fetchall()

    def log_rehab(self, activity):
        db.execute(
            "INSERT INTO rehab (user_id, activity_date, sets, time, max_weight, success_rate, log) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self.id,
                date.today(),
                activity["sets"],
                activity["time"],
                activity["max weight"],
                (activity["success rate"]),
                str(activity["workout log"]),
            ),
        )
        conn.commit()

    def update_pb(self, pb):
        db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                pb,
                self.id,
            ),
        )
        conn.commit()

    def update_baseline(self, baseline):
        db.execute(
            "UPDATE users SET baseline = ? WHERE user_id = ?",
            (
                baseline,
                self.id,
            ),
        )
        conn.commit()

    def diagnosis(self):
        db.execute(
            "INSERT INTO users (name, injury_grade, hand, finger, structures, injury_date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.name,
                self.grade,
                self.hand,
                self.finger,
                str(self.pulleys),
                self.date,
            ),
        )
        conn.commit()

    def last_sesh(self):
        return db.execute(
            "SELECT activity_date, max_weight FROM rehab WHERE user_id = ? ORDER BY activity_date DESC, max_weight DESC LIMIT 1",
            (self.id,),
        ).fetchone()

    def create_tables(self):
        db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT, baseline REAL DEFAULT 0, pb REAL DEFAULT 0)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sets INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT)"
        )


def exit_script():
    conn.close()
    sys.exit("Thanks for coming")


if __name__ == "__main__":
    main()
