from datetime import datetime, date, timedelta
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from recovery_schedule import Phase
from tkinter import *
from tkinter import ttk, messagebox

conn = sqlite3.connect("fingers.db")
db = conn.cursor()

root = Tk()

root.title("Finger Rehabilitator")

# TO DO
# add gui
# more sophisticated user system?
# better graphs?
# improve recovery sched data
# fix bugs
# clean up code
# expectations for remodelling


def main():

    create_tables()
    user = User(input("User Name: "))
    user.lookup_user()
    print(user)

    phase = user.recovery_sched()
    if "remodelling" in phase.current_phase:

        sesh = input("Do you want to record actitity? (y/n): ")
        if sesh == "y":
            record = user.record_hang(phase)
            print(f"Success rate: {record}%")
        else:
            print("maybe next time.")
        results = user.db_progress()

        user.print_graph(results, phase)
    else:
        print(
            f"It's too soon for you to start rehab, but you should keep up with your recovery and come back in {phase.rehab_start_day} days to start rehab."
        )
    conn.close()
    sys.exit("Thanks for coming")


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

    def __str__(self):
        return f"{self.name.title()}: grade {self.grade} injury to the {self.hand}, {self.finger} digit, on {self.date}"

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, inj_date):
        # print(inj_date)

        if inj_date != 0:
            inj_date = str(inj_date)
            d_t = datetime.strptime(str(inj_date), "%Y-%m-%d").date()

            self._date = d_t

        """if not date:
            raise ValueError("Not Date")
            self._date = date.today()
        else:
            try:
                print(inj_date)
                self._date = datetime.strptime(str(inj_date), '%Y,-%m,-%d').date()
                print(self._date)
                
            except ValueError:
                try:
                    day, month, year = inj_date.strip().split("/")
                    self._date = date(int(year), int(month), int(day)).isoformat()
                except:
                    print("Didn't work")
                    self.date = None"""

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
        self.temp = db.execute(
            "SELECT user_id, name, injury_date, injury_grade, hand, finger, structures, baseline, pb FROM users WHERE name = ?",
            (self.name,),
        )

        lookup = self.temp.fetchone()
        if lookup:
            self.login(lookup)
            print(f"Welcome Back {self.name.title()}")
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

    def db_diagnosis(self):
        # insert into db
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

    def db_last_sesh(self):
        return db.execute(
            "SELECT activity_date, max_weight FROM rehab WHERE user_id = ? ORDER BY activity_date DESC, max_weight DESC LIMIT 1",
            (self.id,),
        ).fetchone()

    def db_update_baseline(self):
        db.execute(
            "UPDATE users SET baseline = ? WHERE user_id = ?",
            (
                self.baseline,
                self.id,
            ),
        )
        conn.commit()

    def db_update_pb(self, pb):
        db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                pb,
                self.id,
            ),
        )
        conn.commit()

    def db_log_rehab(self, activity):
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

    def db_progress(self):
        return db.execute(
            "SELECT activity_date, sets, time, max_weight, success_rate FROM rehab WHERE user_id = ?",
            (self.id,),
        ).fetchall()

    def recovery_sched(self):
        phase = Phase(self.since_inj, self.grade)
        if len(phase.current_phase) > 1:
            print(
                f"It's been {self.since_inj} days, you're between the {phase.current_phase[0]} and {phase.current_phase[1]} phase, if you're feeling good you should be feeling {phase.physical_characteristics[1]}, otherwise you might still feel {phase.physical_characteristics[0]}, you should still be making sure you {phase.precautions[0]}. But to recover you could start to {phase.recovery_activities[1]}."
            )
        else:
            print(
                f"It's been {self.since_inj} days, you're in the {phase.current_phase[0]} phase, you should be feeling {phase.physical_characteristics[0]}, you should be making sure you {phase.precautions[0]}. To recover you should be {phase.recovery_activities[0]}."
            )
        return phase

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
        self.db_diagnosis()

    def test_baseline(self):
        attempts = 3
        print(
            "To gauge your recovery we will need to benchmark your injured finger against the opposite (hopefully) healthy finger on your other hand.\n We will get a baseline strength for that finger now... "
        )
        time.sleep(1)
        print(
            f"Nice, okay you're going to need your sling or hangboard, let's give it {attempts} attempts, try and hold the weight for 7 seconds"
        )
        time.sleep(1)
        activity = perform_sets(attempts)
        while True:
            proceed = (
                input(
                    "Are you happy with that score or do you want to give it another go? ('y' to use current max) ..."
                )
                == "y"
            )
            if proceed:
                break
            else:
                activity = perform_sets(attempts=1)

        self.baseline = activity["max weight"]
        print(self.baseline, activity["max weight"])
        self.db_update_baseline()
        print(self.baseline, self.pb)
        # return activity

    def record_hang(self, phase):
        warmed_up = False
        # record activity
        if not warmed_up:
            warmed_up = warmup()
        last_sesh = self.db_last_sesh()

        baseline = self.baseline
        if not baseline:
            self.test_baseline()

        try:
            progress = self.pb / self.baseline
        except ZeroDivisionError:
            progress = 0

        self.sched_exp = phase.rehab_progress / phase.rehab_phase_length
        todays_wt = round(self.baseline * sched_exp)

        if self.since_inj > 2:
            if last_sesh:
                print(
                    f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury.\n\nAt this stage you might expect to be using around {todays_wt}kg ({round(sched_exp * 100)}% of your baseline, which was {self.baseline}kgs).\n\nYour last session was on {last_sesh[0]}, and your max was {last_sesh[1]}kg.\n\nYour personal best is {self.pb}kg, thats {(progress)*100}% of your baseline measurement, which was {self.baseline}kg\n"
                )
            else:
                print(
                    f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury, this is your first session, try to take it really slow\n"
                )
        else:
            print(
                "Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days"
            )
        mode = input(
            "Record if you're using your finger in an open, half crimp or crimp position. ('open'/'half-crimp'/'crimp')... "
        )
        try:
            attempts = 10
            attempts = int(input(f"sets: (leave blank to use {attempts} sets)..."))
        except ValueError:
            attempts = 3
        try:
            seconds = 15
            seconds = int(input(f"time(s): (leave blank to use {seconds}s)... "))
        except ValueError:
            seconds = 7
        activity = perform_sets(attempts, seconds)
        if activity["max weight"] > self.pb:
            print(
                f"Well Done, thats a new P.B, your old P.B was {self.pb}kg, your new P.B is {activity['max weight']}kg"
            )
            self.db_update_pb(activity["max weight"])
        self.db_log_rehab(activity)

        return round(activity["success rate"])

    def print_graph(self, results, phase):
        # sets, time, max_weight, success_rate, date #baseline
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
        
        days = list(range(dates[0], dates[len(dates)-1]))
        for day in days:
            exp = day / phase.rehab_phase_length
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
        plt.plot(days, exp_prog, label='expected progress')

        plt.xlabel("Days Since Injury")
        plt.ylabel("Max Weight")
        plt.title("Weights over time")
        plt.legend()
        plt.show()


# set iterator
def perform_sets(attempts=10, seconds=15):
    success = 0
    max_wt = 0
    log = {}
    for i in range(attempts):
        while True:
            try:
                weight = float(input("What weight are you using? (kg)... "))
                break
            except ValueError:
                print("Enter a numeric weight")
        timer(seconds)
        tick = bool(
            input(
                f"Did you manage that? (type y if you hanged {weight}kg for {seconds} seconds)..."
            )
            .lower()
            .strip()
            == "y"
        )

        if tick:
            success += 1
            if weight > max_wt:
                max_wt = weight
        if i < attempts - 1:
            input("Give yourself 2-3 minutes rest...")
        else:
            print("Well done.")
        log.update({f"set {i}": {"weight": weight, "success": tick}})

        try:
            success_rate = (attempts / success) * 100
        except ZeroDivisionError():
            success_rate = 0
    return {
        "max weight": max_wt,
        "success rate": success_rate,
        "time": seconds,
        "sets": attempts,
        "workout log": log,
    }


# rep timer
def timer(n):
    start = input("OK, when you're ready hit any 'Enter'...")
    seq = [
        "Ready",
        "Steady",
        "Go!!!!",
    ]
    for i in seq:
        print(i, end="\r")
        time.sleep(1)
    print()
    while n:
        print(n, end="\r")
        time.sleep(1)
        n -= 1


# acknowledge warmup message
def warmup():
    input(
        "To warm up, do a 2-5 minutes pulse raiser activity e.g Skipping, followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals. (Hit 'Enter' to continue)..."
    )
    return True


def create_tables():
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT, baseline REAL DEFAULT 0, pb REAL DEFAULT 0)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sets INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT)"
    )


if __name__ == "__main__":
    main()
