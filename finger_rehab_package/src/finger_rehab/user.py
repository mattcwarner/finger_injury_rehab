from datetime import datetime, date, timedelta
from recovery_schedule import Phase
from databaser import Dbb

import matplotlib.pyplot as plt
import numpy as np


class User:
    def __init__(self, name):
        self.name = name
        self.dbb = Dbb(self)
        if not self.login():
            self.exists = False
        
    def login(self):
        tmp = self.dbb.lookup()
        if not tmp:
            return False
        else:
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
            ) = tmp
            self.since_inj = ((date.today()) - (self.date)).days
            self.phase = Phase(self.since_inj, self.grade)
            self.sched_exp = self.since_inj / self.phase.rehab_length
            self.graph = f"{self.id}plot.png"
            self.exists = True
            return True

    def __str__(self):
        return f"{self.name.title()}: grade {self.grade} injury to the {self.hand}, {self.finger} digit, on {self.date}, {self.since_inj} days ago so you should be roughly {self.sched_exp*100:.2f}% recovered Your baseline strength is {self.baseline}, your current p.b is {self.pb}"

    @property
    def baseline(self):
        return self._baseline

    @baseline.setter
    def baseline(self, wt):
        if wt == None:
            self._baseline = 0
        elif int(wt) > 0:
            self._baseline = int(wt)
        else:
            self._baseline = 0

    @property
    def rehab_stage(self):
        return self._rehab_stage

    @rehab_stage.setter
    def rehab_stage(self, stage):
        if stage == None:
            self._rehab_stage = 0
        elif int(stage) in range(4):
            self._rehab_stage = int(stage)
        else:
            self._rehab_stage = 0

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

    def recovery_sched(self):
        if len(self.phase.current_phase) > 1:
            return f"It's been {self.since_inj} days, you're between the {self.phase.current_phase[0]} and {self.phase.current_phase[1]} phase.\n\n If you're feeling good you should be feeling {self.phase.physical_characteristics[1]}.\n\n Otherwise you might still feel {self.phase.physical_characteristics[0]}.\n\n You should still be making sure you {self.phase.precautions[0]}.\n\n But to recover you could start to {self.phase.recovery_activities[1]}."
        else:
            return f"It's been {self.since_inj} days, you're in the {self.phase.current_phase[0]} phase.\n\n You should be feeling {self.phase.physical_characteristics[0]}.\n\n You should be making sure you {self.phase.precautions[0]}.\n\n To recover you should be {self.phase.recovery_activities[0]}."

    def rehab_sched(self):
        stages = {
            0: [
                "open sling",
                "only your injured finger in isolation in an open grip using the last pad until you reach your baseline",
            ],
            1: [
                "half crimp",
                "your injured hand in a half crimp position using the last pad until you reach your baseline",
            ],
            2: [
                "full crimp",
                "your injured hand in a full crimp position using the last pad until you reach your baseline",
            ],
            3: [
                "both hands",
                "both hands in a variety of grip types to continue strengthening your tissues and make you less prone to injury",
            ],
        }
        if self.pb >= self.baseline and self.baseline > 0:
            if self.rehab_stage in range(0, 2):
                self.rehab_stage += 1
                self.dbb.update_stage()
                self.pb = 0
                self.dbb.update_pb()
                self.baseline = 0
                self.dbb.update_baseline()
            else:
                self.rehab_stage = 3
                self.dbb.update_stage()
        prev_info_str = ""
        if self.rehab_stage > 0:
            prev_info_str += "In previous stages, these were your records:\n"
            for stage in range(self.rehab_stage):
                baseline =  (self.dbb.get_max(stage, mode=0)[0][0])
                pb = ((self.dbb.get_max(stage))[0][0])
                prev_info_str += f"{stages[stage][0].title()}, Baseline: {baseline}, PB: {pb}.\n"
        try:
            progress = self.pb / self.baseline
        except ZeroDivisionError:
            progress = 0

        if not self.baseline:
            return f"You're ready to move into the next phase of your rehab, which is {stages[self.rehab_stage][0]}.\n\nThis is going to involve progressively loading {stages[self.rehab_stage][1]}.\n\n{prev_info_str}"

        return f"You are in the {stages[self.rehab_stage][0]} stage of rehab.\n\n Your {stages[self.rehab_stage][0]} baseline strength is {self.baseline}kg, your current {stages[self.rehab_stage][0]} P.B is {self.pb} thats {round((progress)*100)}% of your baseline measurement.\n\nContinue progressively loading {stages[self.rehab_stage][1]}.\n\n{prev_info_str}"



    def progress_info(self):
        last_sesh = self.dbb.last_sesh()
        if not self.baseline:
            return "We need to test your baseline to find out what to expect from you.\nHead to the activity tab to add one."
        todays_wt = round(self.baseline * self.sched_exp)
        if self.since_inj > 2:
            if last_sesh:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury.\n\nAt this stage you might expect to be using around {todays_wt}kg ({round(self.sched_exp * 100)}% of your baseline.\n"
            else:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury, this is your first session, try to take it really slow\n"
        else:
            return "Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days"
        # =dt.strftime("%d-%B-%Y")


    def print_graph(self, show=True):

        colours = ['red', 'orange', 'green', 'blue',]
        labels = ['single finger', 'half crimp', 'full crimp', 'both hands',]

        data = {}
        for s in range(self.rehab_stage + 1):
            pbs = self.dbb.get_max(stage=s, mode=1)
            dates = []
            weights = []
            for pb in pbs:
                dates.append((date.fromisoformat(pb[1]) - self.date).days)
                weights.append(pb[0]) 
            print(weights)
            bs = self.dbb.get_max(stage=s, mode=0)
            bs_dates = []
            bs_weights = []
            for bs in bs:
                bs_dates.append(((date.fromisoformat(bs[1]) - self.date).days))
                bs_weights.append(bs[0])
            bs_dates.append((date.today() - self.date).days)
            bs_weights.append(bs_weights[-1])

            data[s] = {'dates': dates, 'weights': weights, 'baselines': {'dates': bs_dates, 'weights': bs_weights}}

        for i in data:
            plt.plot(data[i]['dates'], data[i]['weights'], color=colours[i], linestyle="dashed", linewidth=3, marker="*", markerfacecolor="green", markersize=7, label=labels[i],)
            plt.plot(data[i]['baselines']['dates'], data[i]['baselines']['weights'], color=colours[i], linestyle="--")


        plt.xlabel("Days Since Injury")
        plt.ylabel("Max Weight")
        plt.title("Weights over time")
        plt.legend()
        plt.savefig(f"{self.id}plot.png", bbox_inches="tight")
        if show:
            plt.show()

