from tkinter import *
from tkinter import ttk, messagebox

from tkcalendar import DateEntry
from databaser import Dbb
from datetime import datetime, date, timedelta

# This is a parent class that takes care of collection and checking variables
# it is meant to be initialised from a tk program which then calls the get_diagnosis function
# it is used to call a further tk window which is dependent on the original tk program and is a subclass of this class
# the diagnose_window class allows for entry of the variables and uses this class' checks and submit function
class Diagnose:
    def __init__(self, parent):
        self.parent = parent

    def get_diagnosis(self):
        self.gui = Diagnose_window(self.parent)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("No name")
        self._name = name

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, inj_date):
        if not type(inj_date) is type(date.today()) or inj_date > date.today():
            raise ValueError("Prob with date.")
        else:
            self._date = inj_date

    @property
    def hand(self):
        return self._hand

    @hand.setter
    def hand(self, hand):
        if hand == "left" or hand == "right":
            self._hand = hand
        else:
            raise ValueError("Prob with hand.")

    @property
    def finger(self):
        return self._finger

    @finger.setter
    def finger(self, finger):
        finger = int(finger)
        if finger in range(1, 5):
            self._finger = finger
        else:
            raise ValueError("Prob with finger.")

    @property
    def pulleys(self):
        return self._pulleys

    @pulleys.setter
    def pulleys(self, pulleys):
        if pulleys:
            self._pulleys = list()
            for i in pulleys:
                i = int(i)
                if i > 2 or i < 0:
                    raise ValueError("Not an injurable pulley")
                self._pulleys.append(i + 2)
        else:
            raise ValueError("Prob with pulleys.")

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, grade):
        try:
            grade = int(grade)
        except TypeError:
            raise ValueError("Grade wasn't a number")
        if grade in range(1, 5):
            self._grade = grade
        else:
            raise ValueError("Prob with grade.")

    def submit_diagnosis(self):
        db = Dbb(self)
        db.diagnosis(
            self.name,
            self.grade,
            self.hand,
            self.finger,
            str(self.pulleys),
            self.date,
        )
        db.exit_script()
        self.parent.root.bind("<Return>", lambda e: my_sev())
        self.parent.login_check()
        self.parent.recovery_info.set(":)")

# This class has sequential functions to get injury imformation from the user in a tk frame.
class Diagnose_window(Diagnose):
    def __init__(self, parent):
        self.parent = parent
        self.name = self.parent.user.name
        self.parent.diagnosis_info.set(
            f"Hello {self.parent.user.name.title()}\nLets get some information from you to help tailor your rehab.\nWe need to find out when you were injured, where and how bad it is.\nFollow the interactive prompts to fill us in..."
        )
        self.parent.recovery_info.set("What date did you get injured?")
        self.get_date()

    # functions are called sequentially by the completed function once the variables are accepted
    def get_date(self):
        # adapted from https://www.plus2net.com/python/tkinter-DateEntry.php
        dates = ttk.Frame(
            self.parent.notebook_diagnosis,
            borderwidth=5,
            relief="ridge",
            width=self.parent.WIN_WID,
        )
        dates.grid(row=3, column=0, padx=5, pady=5, sticky=(N, E, S, W))

        cal = DateEntry(dates, selectmode="day", justify="center")
        cal.grid(row=0, column=0, padx=5, pady=5, sticky=(N, E, S, W))

        def my_upd():
            dt = cal.get_date()
            # str=dt.strftime("%d-%m-%Y") # changing the format
            l1.config(text=dt)
            try:
                self.date = dt
            except ValueError:
                self.parent.recovery_info.set("Date should be in the past")

                return
            dates.grid_forget()
            self.get_structs()
            return True

        l1 = ttk.Label(dates, text="Injury Date")  # Label to display date
        l1.grid(row=2, column=0, sticky=(N, E, S, W), padx=5, pady=5)

        b1 = ttk.Button(dates, text="Set Date", command=lambda: my_upd())
        b1.grid(row=3, column=0, sticky=(N, E, S, W), padx=5, pady=5)
        self.parent.root.bind("<Return>", lambda e: my_upd())

    def get_structs(self):
        self.parent.diagnosis_info.set("Structures Injured:")
        self.parent.recovery_info.set("Where did you get injured?")

        def my_hand():
            try:
                self.hand = str(self.h.get())
            except ValueError:
                l1.config(text="Select Hand")
                return
            try:
                self.finger = int(self.f.get())
            except ValueError:
                l1.config(text="Select Finger")
                return
            try:
                self.pulleys = list(p.curselection())
            except ValueError:
                l1.config(text="Select Pulleys")
                return
            structs.grid_forget()
            self.get_severity()

        self.h = StringVar()
        structs = ttk.Frame(
            self.parent.notebook_diagnosis,
            borderwidth=5,
            relief="ridge",
            width=self.parent.WIN_WID,
        )
        structs.grid(row=4, column=0, sticky=(N, E, S, W), padx=5, pady=5)

        hands = ttk.Frame(
            structs,
            borderwidth=5,
            relief="ridge",
        )
        hands.grid(row=0, column=0, padx=5, pady=5)

        left = ttk.Radiobutton(hands, text="Left Hand", variable=self.h, value="left")
        left.grid(row=0, column=0)
        right = ttk.Radiobutton(
            hands, text="Right Hand", variable=self.h, value="right"
        )
        right.grid(row=0, column=1)

        fingers = ttk.Frame(structs, borderwidth=5, relief="ridge")
        fingers.grid(row=1, column=0, padx=4, pady=5)
        self.f = StringVar()
        f1 = ttk.Radiobutton((fingers), text="First Finger", variable=self.f, value=1)
        f1.grid(
            row=1,
            column=0,
        )
        f2 = ttk.Radiobutton((fingers), text="Middle Finger", variable=self.f, value=2)
        f2.grid(
            row=1,
            column=1,
        )
        f3 = ttk.Radiobutton((fingers), text="Ring Finger", variable=self.f, value=3)
        f3.grid(
            row=2,
            column=0,
        )
        f4 = ttk.Radiobutton((fingers), text="Pinky Finger", variable=self.f, value=4)
        f4.grid(
            row=2,
            column=1,
        )

        self.pulleys_idx = [
            "A2",
            "A3",
            "A4",
        ]
        pulleysvar = StringVar(value=self.pulleys_idx)
        p = Listbox(
            structs,
            height=3,
            selectmode="multiple",
            exportselection=0,
            selectbackground="blue",
            listvariable=pulleysvar,
            justify="center",
        )
        p.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        b1 = ttk.Button(
            structs,
            text="Set Hand",
            command=lambda: my_hand(),
        )
        b1.grid(row=4, column=0, columnspan=2)
        self.parent.root.bind("<Return>", lambda e: my_hand())

        l1 = ttk.Label(structs, text="")
        l1.grid(row=5, column=0)

    def get_severity(self):
        self.parent.diagnosis_info.set("How bad is it?")
        self.parent.recovery_info.set(
            "Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture or multiple tears,\nGrade 4: Multiple ruptures"
        )

        def my_sev():
            try:
                self.grade = int(self.g.get())
            except ValueError:
                self.parent.diagnosis_info.set("Pick an option!")
                return
            sev.grid_forget()
            self.submit_diagnosis()

        self.g = IntVar()
        self.g.set(0)
        sev = ttk.Frame(
            self.parent.notebook_diagnosis,
            borderwidth=5,
            relief="ridge",
        )
        sev.grid(
            row=4,
            column=0,
            sticky=(N, E, S, W),
            padx=5,
            pady=5,
        )
        g1 = ttk.Radiobutton((sev), text="Grade I", variable=self.g, value=1)
        g1.grid(
            row=1,
            column=0,
        )
        g2 = ttk.Radiobutton((sev), text="Grade II", variable=self.g, value=2)
        g2.grid(
            row=2,
            column=0,
        )
        g3 = ttk.Radiobutton((sev), text="Grade III", variable=self.g, value=3)
        g3.grid(
            row=3,
            column=0,
        )
        g4 = ttk.Radiobutton((sev), text="Grade IV", variable=self.g, value=4)
        g4.grid(
            row=4,
            column=0,
        )

        b1 = ttk.Button(sev, text="Set Grade", command=lambda: my_sev())
        b1.grid(
            row=5,
            column=0,
        )
        self.parent.root.bind("<Return>", lambda e: my_sev())
