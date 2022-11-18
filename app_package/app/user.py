from datetime import datetime, date, timedelta
from recovery_schedule import Phase
from databaser import Dbb

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class User:
    ind_fingers = {1:'Thumb', 2:'Index', 3:'Middle', 4:'Ring', 5:'Pinky',}
    def __init__(self, name):
        self.name = name
        self.dbb = Dbb(self)
        if not self.login():
            self.exists = False

    def login(self):
        tmp = self.dbb.lookup()
        if not tmp:
            return False
        # have lookup return dicitonary
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
        self.phase = Phase(self.since_inj, self.grade, self.rehab_stage)
        self.sched_exp = self.since_inj / self.phase.rehab_length
        #self.rehab_exp = self.phase.get_stage_exp(self.rehab_stage) # this should come for free two lines before
        #print(f"percentage of rehab stage: {self.rehab_exp * 100}%")

        # self.graph = f"{self.id}plot.png"
        self.path = Path.cwd() / ("graphs") / f"{self.id}plot.png" #Path.cwd().parent / ("graphs") / f"{self.id}plot.png"
        self.exists = True
        self.baseline = self.manual_baseline()
        
        return True

    def __str__(self):
        return f"Name: {self.name.title()}\nGrade {self.grade} injury to the {self.hand}, {User.ind_fingers[self.finger]} finger.\nInjured on {self.date}, so you should be roughly {self.sched_exp*100:.2f}% recovered.\n"
    @property
    def baseline(self):
        return self._baseline

    @baseline.setter
    def baseline(self, wt):
        if wt == None:
            self._baseline = 0
        elif float(wt) > 0:
            self._baseline = float(wt)
        else:
            self._baseline = 0

    def manual_baseline(self):
        try:
            result = (self.dbb.get_max(self.rehab_stage, mode=0, date=0)[0])
            print(f"manual baseline: {result}, rehab stage: {self.rehab_stage}")

            return result
        except:
            return 0

    @property
    def rehab_stage(self):
        return self._rehab_stage

    @rehab_stage.setter
    def rehab_stage(self, stage):
        if stage == None:
            self._rehab_stage = 0
        elif int(stage) in range(len(Phase.stages)):
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
        name = name.strip().split()
        if len(name) > 1:
            raise ValueError("Name too long")
        else:
            self._name = name[0]

    def recovery_sched(self):
        if len(self.phase.current_phase) > 1:
            return f"It's been {self.since_inj} days, you're between the {self.phase.current_phase[0]} and {self.phase.current_phase[1]} phase.\n\n If you're feeling good you should be feeling {self.phase.physical_characteristics[1]}.\n\n Otherwise you might still feel {self.phase.physical_characteristics[0]}.\n\n You should still be making sure you {self.phase.precautions[0]}.\n\n But to recover you could start to {self.phase.recovery_activities[1]}."
        else:
            return f"It's been {self.since_inj} days, you're in the {self.phase.current_phase[0]} phase.\nYour injury is expected to take {self.phase.rehab_phase_length} days to recover from, so you still have {self.phase.rehab_phase_length - self.since_inj} days left.\n\n You should be feeling {self.phase.physical_characteristics[0]}.\n\n You should be making sure you {self.phase.precautions[0]}.\n\n To recover you should be {self.phase.recovery_activities[0]}."

    def rehab_sched(self):
        if self.pb >= self.baseline and self.baseline > 0:
            
            if self.rehab_stage == len(Phase.stages) - 1:
                print(f"final rehab stage: {self.rehab_stage}")
            elif self.rehab_stage in range(len(Phase.stages) - 1):
                self.rehab_stage += 1
                self.dbb.update_stage()
                tmp = self.dbb.get_max(self.rehab_stage, date=0)
                try:
                    self.pb = tmp[0]
                except TypeError:
                    self.pb = 0
                
                self.dbb.update_pb()
                self.manual_baseline()
                self.dbb.update_baseline()
                
            else:
                print("exception")

        stage_info = "These are your stage records:"
        baselines = {}
        pbs = {}
        for n, stage in enumerate(Phase.stages):
            try:
                baseline = self.dbb.get_max(stage, mode=0, date=0)[0]  
            except TypeError:
                baseline = 0
            try:
                pb = self.dbb.get_max(stage, date=0)[0]
            except TypeError:
                pb = 0
            baselines[n] = baseline
            pbs[n] = pb
            stage_info += f"\n{Phase.stages[stage][0].title()}, Baseline: {baseline} kgs, PB: {pb} kgs."
        print(baselines, pbs)
        b = baselines[self.rehab_stage]
        p = pbs[self.rehab_stage]
        try:
            progress = p / b
        except ZeroDivisionError:
            progress = 0

        if not self.baseline:
            return f"You're ready to move into the next phase of your rehab, which is {Phase.stages[self.rehab_stage][0]}.\n\nThis is going to involve progressively loading {Phase.stages[self.rehab_stage][1]}.\n\n{stage_info}"
        info = [f"You are in the {Phase.stages[self.rehab_stage][0]} stage of rehab.",
                f"Your {Phase.stages[self.rehab_stage][0]} baseline strength is {b}kg.",
                f"Your current {Phase.stages[self.rehab_stage][0]} P.B is {p}.", 
                f"Thats {round((progress)*100)}% of your baseline measurement.",
                f"Expected loading at this time: {round(b * self.phase.rehab_exp)} kgs, ({round(self.phase.rehab_exp * 100)} %).",
                f"Continue progressively loading {Phase.stages[self.rehab_stage][1]}.",
                stage_info,
        ]
        return ("\n\n".join(info))
        #return f"You are in the {Phase.stages[self.rehab_stage][0]} stage of rehab.\nYour {Phase.stages[self.rehab_stage][0]} baseline strength is {b}kg, your current {Phase.stages[self.rehab_stage][0]} P.B is {p} thats {round((progress)*100)}% of your baseline measurement.\nContinue progressively loading {Phase.stages[self.rehab_stage][1]}.\n\n{stage_info}"

    def progress_info(self):
        last_sesh = self.dbb.last_sesh()
        print(self.baseline)
        if not self.baseline:
            return "We need to test your baseline to find out what to expect from you.\nHead to the activity tab to add one.\n"
        todays_wt = round(self.baseline * self.sched_exp)
        if self.since_inj > 2:
            if last_sesh:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury.\nThis might mean that you are roughly ({round(self.sched_exp * 100)}% through your rehab journey.\n" #At this stage you might expect to be using around {todays_wt}kg ({round(self.sched_exp * 100)}% of your baseline.\n"
            else:
                return f"Okay {self.name.title()}, it's been {self.since_inj} days since your injury, this is your first session, try to take it really slow\n"
        else:
            return "Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days"
        # =dt.strftime("%d-%B-%Y")

    def print_graph(self, show=True):

        colours = [
            "red",
            "orange",
            "green",
            "blue",
            "brown", 
            "purple",
            "pink",
        ]
        labels = [Phase.stages[stage][0] for stage in Phase.stages]
       
        data = {}
        for s in range(self.rehab_stage + 1):
            pbs = self.dbb.get_max(stage=s, mode=1)
            dates = []
            weights = []
            if not pbs:
                print("no pbs")
                dates = [
                    (date.today() - self.date).days,
                ]
                weights = [
                    0,
                ]
            else:
                for pb in pbs:
                    dates.append((date.fromisoformat(pb[1]) - self.date).days)
                    weights.append(pb[0])

            bs = self.dbb.get_max(stage=s, mode=0)
            bs_dates = []
            bs_weights = []
            if not bs:
                print("no bs")
                bs_dates = [
                    (date.today() - self.date).days,
                ]
                bs_weights = [
                    0,
                ]
            else:
                for b in bs:
                    bs_dates.append(((date.fromisoformat(b[1]) - self.date).days))
                    bs_weights.append(b[0])
                bs_dates.append((date.today() - self.date).days)
                bs_weights.append(bs_weights[-1])

            data[s] = {
                "dates": dates,
                "weights": weights,
                "baselines": {"dates": bs_dates, "weights": bs_weights},
            }
        print(data)
        for i in data:
            plt.plot(
                data[i]["dates"],
                data[i]["weights"],
                color=colours[i],
                linestyle="dashed",
                linewidth=3,
                marker="*",
                markerfacecolor="green",
                markersize=7,
                label=labels[i],
            )
            plt.plot(
                data[i]["baselines"]["dates"],
                data[i]["baselines"]["weights"],
                color=colours[i],
                linestyle="--",
            )

        plt.xlabel("Days Since Injury")
        plt.ylabel("Max Weight (Kg)")
        plt.title("Weights over time")
        plt.legend()

        plt.savefig(self.path, bbox_inches="tight")
        if show:
            plt.show()
