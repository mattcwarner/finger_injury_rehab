from datetime import datetime, date, timedelta
from recovery_schedule import Phase
import sqlite3

import matplotlib.pyplot as plt
import numpy as np


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
        self.dbb = Dbb(self)
        self.rehab_stage = 0

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
        self.temp = self.dbb.lookup()
        if self.temp:
            return self.login(self.temp)

        else:
            return False

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
            self.rehab_stage,
        ) = existing
        self.since_inj = ((date.today()) - (self.date)).days
        self.phase = Phase(self.since_inj, self.grade)
        self.sched_exp = self.phase.rehab_progress / self.phase.rehab_phase_length
        self.graph = f"{self.id}plot.png"
        return True

    def recovery_sched(self):
        if len(self.phase.current_phase) > 1:
            return f"It's been {self.since_inj} days, you're between the {self.phase.current_phase[0]} and {self.phase.current_phase[1]} phase.\n\n If you're feeling good you should be feeling {self.phase.physical_characteristics[1]}.\n\n Otherwise you might still feel {self.phase.physical_characteristics[0]}.\n\n You should still be making sure you {self.phase.precautions[0]}.\n\n But to recover you could start to {self.phase.recovery_activities[1]}."
        else:
            return f"It's been {self.since_inj} days, you're in the {self.phase.current_phase[0]} phase.\n\n You should be feeling {self.phase.physical_characteristics[0]}.\n\n You should be making sure you {self.phase.precautions[0]}.\n\n To recover you should be {self.phase.recovery_activities[0]}."

    def rehab_sched(self):
        stages = {
            0: [
                "open sling loads",
                "only your injured finger in isolation in an open grip using the last pad until you reach your baseline",
            ],
            1: [
                "half crimp loads",
                "your injured hand in a half crimp position using the last pad until you reach your baseline",
            ],
            2: [
                "full crimp loads",
                "your injured hand in a full crimp position using the last pad until you reach your baseline",
            ],
            3: [
                "both hands loads",
                "both hands in a variety of grip types to continue strengthening your tissues and make you less prone to injury",
            ],
        }
        if self.pb >= self.baseline:
            if self.rehab_stage in range(0, 2):
                self.rehab_stage += 1
                self.dbb.update_rehab_stage()
                self.pb = 0
                self.dbb.update_pb()
                self.baseline = 0
                self.dbb.update_baseline()
            else:
                self.rehab_stage = 3
                self.dbb.update_rehab_stage()

        if not self.baseline:
            return f"You're ready to move into the next phase of your rehab, which is {stages[self.rehab_stage]}.\nPlease record a new baseline for your current rehab stage"

        return f"You are in the {stages[self.rehab_stage][0]} stage of rehab, Please continue progressively load {stages[self.rehab_stage][1]}"

    def metrics_info(self):
        return (
            f"Your baseline strength is {self.baseline}, your current p.b is {self.pb}"
        )

    def print_graph(self, show=True):
        # sets, time, max_weight, success_rate, date #baseline
        results = self.dbb.progress()
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

        if len(dates) == 0:
            dates = [
                0,
            ]
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
        last_sesh = self.dbb.last_sesh()
        if not self.baseline:
            return "We need to test your baseline to find out what to expect from you.\nHead to the activity tab to add a baseline"
        try:
            progress = self.pb / self.baseline
        except ZeroDivisionError:
            progress = 0
        todays_wt = round(self.baseline * self.sched_exp)
        if self.since_inj > 2:
            if last_sesh:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury.\n\nAt this stage you might expect to be using around {todays_wt}kg ({round(self.sched_exp * 100)}% of your baseline, which was {self.baseline}kgs).\n\nYour last session was on {last_sesh[0]}, and your max was {last_sesh[1]}kg.\n\nYour personal best is {self.pb}kg, thats {round((progress)*100)}% of your baseline measurement, which was {self.baseline}kg\n"
            else:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury, this is your first session, try to take it really slow\n"
        else:
            return "Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days"
        # =dt.strftime("%d-%B-%Y")


class Dbb(User):
    def __init__(self, user):
        # connect to db
        self.conn = sqlite3.connect("../fingers.db")
        self.db = self.conn.cursor()
        self.create_tables()
        self.name = user.name
        self.user = user

    def exit_script(self):
        self.conn.close()

    def lookup(self):
        self.create_tables()
        info = self.db.execute(
            "SELECT user_id, name, injury_date, injury_grade, hand, finger, structures, baseline, pb, rehab_stage FROM users WHERE name = ?",
            (self.name,),
        ).fetchone()
        if info:
            self.login(info)
            return info
        else:
            return False

    def progress(self):
        return self.db.execute(
            "SELECT activity_date, sets, time, max_weight, success_rate, rehab_stage FROM rehab WHERE user_id = ?",
            (self.user.id,),
        ).fetchall()

    def log_rehab(self, activity):
        self.db.execute(
            "INSERT INTO rehab (user_id, activity_date, sets, time, max_weight, success_rate, log, rehab_stage) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.user.id,
                date.today(),
                activity["sets"],
                activity["time"],
                activity["max weight"],
                (activity["success rate"]),
                str(activity["workout log"]),
                self.user.rehab_stage,
            ),
        )
        self.conn.commit()

    def update_pb(self):
        self.db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                self.user.pb,
                self.id,
            ),
        )
        self.conn.commit()

    def update_rehab_stage(self):
        self.db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                self.user.rehab_stage,
                self.id,
            ),
        )
        self.conn.commit()

    def update_baseline(self):
        print(f"update bs to {self.user.baseline}")
        self.db.execute(
            "UPDATE users SET baseline = ? WHERE user_id = ?",
            (
                self.user.baseline,
                self.id,
            ),
        )
        self.conn.commit()

    def diagnosis(self, name, grade, hand, finger, pulleys, date):
        self.db.execute(
            "INSERT INTO users (name, injury_grade, hand, finger, structures, injury_date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                name,
                grade,
                hand,
                finger,
                pulleys,
                date,
            ),
        )
        self.conn.commit()

    def last_sesh(self):
        return self.db.execute(
            "SELECT activity_date, max_weight, rehab_stage FROM rehab WHERE user_id = ? ORDER BY activity_date DESC, max_weight DESC LIMIT 1",
            (self.user.id,),
        ).fetchone()

    def create_tables(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT, baseline REAL DEFAULT 0, pb REAL DEFAULT 0, rehab_stage INT DEFAULT 0)"  # , h_baseline REAL DEFAULT 0, h_pb REAL DEFAULT 0, f_baseline REAL DEFAULT, f_pb REAL DEFAULT 0)"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sets INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT)"  # , rehab_stage INT DEFAULT 0)"
        )
