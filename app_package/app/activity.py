from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry 
from datetime import datetime, date, timedelta
from timer import Timer
from recovery_schedule import Phase

WIN_WID = 400

# display editable log
# free timer
# bind enter (change path)
# new weight button / rm weight entry from first display
class Activitywindow():
    def __init__(self, user, root, parent, width=WIN_WID) :
        self.user = user
        self.mainwindow = root
        self.root = root.root 
        self.parent = parent
        self.WIN_WID = WIN_WID
        self.activity_info = StringVar()
        self.record_mode = None
        self.mode_info = StringVar()
        self.act_date = date.today()
        self.stage = None

        self.populate()

    def timer_instance(self, n=0, s=False):

        if not n:
            def start_timer():
                try:
                    n = int(self._seconds.get())
                except ValueError:
                    self.seconds_label.config(text= "Enter a number")
                    return
                timer = Timer(self.root, n, s)
            self.s_frame(self.parent, row=8)

            self.go_button = ttk.Button(
                self.f1, text="Go", command=lambda: start_timer()
            )
            self.go_button.grid(column=0, row=3, sticky=(N, E, W))
            self.go_button.focus()
            self.root.bind("<Return>", lambda e: start_timer())
        else:
            timer = Timer(self.root, n, s)

    def s_frame(self, parent, row=0):
        self.f1 = ttk.Frame(parent, width=self.WIN_WID)
        self.f1.grid(row=row, column=0)
        self._seconds = StringVar()
        self._seconds.set("15")
        seconds_entry = ttk.Entry(self.f1, textvariable=self._seconds)
        seconds_entry.grid(column=0, row=2, sticky=(N, S, W), padx=5, pady=5)
        self.seconds_label = ttk.Label(self.f1, text="seconds")
        self.seconds_label.grid(column=1, row=2, sticky=(N, S, W))


    def populate(self):
        bs_btns = {}
        for stage in Phase.stages:
            # from stackoverflow.(https://stackoverflow.com/questions/10865116/tkinter-creating-buttons-in-for-loop-passing-command-arguments).This may look magical, but here's what's happening. When you use that lambda to define your function, the open_this call doesn't get the value of the variable i at the time you define the function. Instead, it makes a closure, which is sort of like a note to itself saying "I should look for what the value of the variable i is at the time that I am called". Of course, the function is called after the loop is over, so at that time i will always be equal to the last value from the loop.
            # Using the i=i trick causes your function to store the current value of i at the time your lambda is defined, instead of waiting to look up the value of i later.
            bs_btns[stage] = ttk.Button(self.parent, text=f"Record {Phase.stages[stage][0].title()} Baseline", command= lambda stage=stage: self.new_baseline(stage),)
            bs_btns[stage].grid(column=0, row=2+stage, sticky=(N,E,W))

        self.activity_info.set("Lets Go")
        activity_button = ttk.Button(
            self.parent,
            text="Record Activity",
            command=lambda: self.new_activity(),
        )
        activity_button.grid(column=0, row=6, sticky=(N, E, W))
        free_tim = ttk.Button(self.parent, text="Custom Timer", command=lambda: self.timer_instance(s=True))
        free_tim.grid(column=0, row=7, sticky=(N,E,W))

        if "remodelling" not in self.mainwindow.user.phase.current_phase:
            self.activity_info.set(
                f"It's too soon for you to start rehab, but you should keep up with your recovery and come back in {self.user.phase.rehab_start_day} days to start rehab."
            )
            activity_button['state'] = 'disabled'

    def new_activity(self):
        if not self.user.baseline:
            messagebox.showinfo(message="Please record a baseline first")
            return
        attempts = 10
        self.record_mode = "activity"
        self.mode_info.set('Long duration low intensity loading is reccommended, grab your sling or hangboard')
        self.hangs(attempts)

    def new_baseline(self, stage):
        attempts = 3
        self.record_mode = "baseline"
        print(f"stage from button {stage}")
        self.stage = stage
        self.mode_info.set(
            f"To gauge your recovery we will need to benchmark your injured finger against the opposite (hopefully) healthy finger on your other hand.\n We will get a baseline strength for that finger now. \n Okay you're going to need your sling or hangboard, let's give it {attempts} attempts, try and hold the weight for 15 seconds"
        )
        self.hangs(attempts)

    def hangs(self, sets):
        if not self.stage:
            self.stage = self.user.rehab_stage
        self.recording = ttk.Frame(self.mainwindow.notebook, width=self.WIN_WID)
        self.mainwindow.notebook.add(self.recording, text=self.record_mode.title())
        self.mainwindow.notebook.select(self.recording)

        self.entry_mod = ttk.Frame(self.recording, width=WIN_WID)
        self.entry_mod.grid(row=0, column=0)
        self.entry_mode = StringVar()
        self.entry_mode.set('live')
        lbl = ttk.Label(self.entry_mod, text='Recording Entry Mode: ')
        lbl.grid(row=0, column=0)
        manual = ttk.Checkbutton(self.entry_mod, text='Use Manual Entry', command=lambda: self.entry_changed(), variable=self.entry_mode, onvalue='manual', offvalue='live')
        manual.grid(row=0, column=1)
        """live = ttk.Radiobutton(self.entry_mod, text="Live", variable=self.entry_mode, value='live')
        live.grid(row=0, column=1)
        manual = ttk.Radiobutton(self.entry_mod, text="Manual", variable=self.entry_mode, value='manual')
        manual.grid(row=0, column=2)"""

        self.f1 = ttk.Frame(self.recording, width=self.WIN_WID)
        self.f1.grid(row=1, column=0)
        self._sets = StringVar()
        self._sets.set(sets)
        sets_entry = ttk.Entry(self.f1, textvariable=self._sets)
        sets_entry.grid(column=0, row=1, sticky=(N, S, W), padx=5, pady=5)
        sets_label = ttk.Label(self.f1, text="reps")
        sets_label.grid(column=1, row=1, sticky=(N, S, W))
        self._seconds = StringVar()
        self._seconds.set("15")
        seconds_entry = ttk.Entry(self.f1, textvariable=self._seconds)
        seconds_entry.grid(column=0, row=2, sticky=(N, S, W), padx=5, pady=5)
        seconds_label = ttk.Label(self.f1, text="seconds")
        seconds_label.grid(column=1, row=2, sticky=(N, S, W))

        self.f2 = ttk.Frame(self.recording, width=self.WIN_WID)
        self.f2.grid(row=2, column=0)
        self._weight = StringVar()
        self._weight.set(str(round(self.user.pb * 0.8)))
        weight_entry = ttk.Entry(self.f2, textvariable=self._weight)
        weight_entry.grid(column=0, row=0, sticky=(N, S, W), padx=5, pady=5)
        weight_label = ttk.Label(self.f2, text="Kg")
        weight_label.grid(column=1, row=0, sticky=(N, S, W))

        self.go_button = ttk.Button(
            self.f2, text="Go", command=lambda: self.launch_activity()
        )
        self.go_button.grid(column=0, row=3, sticky=(N, E, W))
        self.go_button.focus()
        self.root.bind("<Return>", lambda e: self.launch_activity())

        self.hang_label = ttk.Label(
            self.recording, textvariable=self.mode_info, wraplength=WIN_WID
        )
        self.hang_label.grid(column=0, row=4, columnspan=2, sticky=(N, E, S, W))

        self.cal=DateEntry(self.recording,selectmode='day')
        
    def entry_changed(self):
        if self.entry_mode.get() == 'manual':

            self.cal=DateEntry(self.recording,selectmode='day')
            self.cal.grid(row=3,column=0,padx=20,pady=30, sticky=(N,W))
            self.go_button.config(text='Record manually', command=lambda: self.rec_manual())
            self.root.bind("<Return>", lambda e: self.rec_manual())
        else:
            self.cal.grid_forget()
            self.go_button.config(text='Go', command=lambda: self.launch_activity())
            self.root.bind("<Return>", lambda e: self.launch_activity())

    def rec_manual(self):
        self.mainwindow.warmed_up = True
        self.act_date = (self.cal.get_date())
        self.max_wt = float(self._weight.get())
        self.attempts = int(self._sets.get())
        self.seconds = int(self._seconds.get())
        self.success = self.attempts
        self.log = {
            "entry type": "manual",
            "rehab_stage": self.stage,
            "baseline": self.user.baseline,
        }
        self.finish_activity()


    def launch_activity(self):
        if not self.mainwindow.warmed_up:
            self.mainwindow.warmed_up = self.warmup()

        self.success = 0
        self.max_wt = 0
        self.log = {
            "rehab_stage": self.user.rehab_stage,
            "baseline": self.user.baseline,
        }
        self.rep = 0
        self.attempts = int(self._sets.get())
        self.seconds = int(self._seconds.get())
        self.f1.grid_remove()
        if self.cal:
            self.cal.grid_forget()
        
        self.act_info = StringVar()
        self.act_info.set(f"Rest 2-3 minutes between reps.\nRep: {self.rep} / {self.attempts}.\nLog: {self.log}")
        self.info_label = ttk.Label(self.recording, textvariable=self.act_info, wraplength=self.WIN_WID)
        self.info_label.grid(column=0, row=10)

        # weight_entry.focus
        self.go_button.config(text="New Rep", command=lambda: self.perform_rep())
        self.root.bind("<Return>", lambda e: self.perform_rep())
        self.perform_rep()

        """while self.rep < self.attempts:
            self.perform_rep()
        self.finish_activity()"""

    def perform_rep(self):
        # self.root.bind("<Return>", lambda e: self.launch_activity())
        timer = Timer(self.root, self.seconds)
        complete = False
        while complete == False:
            try:
                wt = float(self.weight.get())
            except ValueError:
                print("problem getting weight")
            #timer = Timer(self.recording, self.seconds)
            tick = timer.success
            if tick:
                self.success += 1
                if wt > self.max_wt:
                    self.max_wt = wt
                else:
                    messagebox.showinfo(
                        message="Well done, consider adding a little bit of weight"
                    )
            self.log.update({f"rep: {self.rep + 1}": {"weight": {wt}, "success": {tick}}})
            self.rep += 1
            complete = True
        timer.win.destroy()
        self.act_info.set(f"Activity in progress.\nRest 2-3 minutes between reps.\nRep: {self.rep} / {self.attempts}.\nLog: {self.log}")
        if self.rep == self.attempts:
            self.finish_activity()

    def finish_activity(self):
        self.recording.destroy()
        if self.record_mode == "activity":
            self.r = 1
            if self.max_wt > self.user.pb:
                messagebox.showinfo(
                    message=(
                        f"Well Done, thats a new P.B, your old P.B was {self.user.pb}kg, your new P.B is {self.max_wt}kg"
                    )
                )
                self.user.pb = self.max_wt
                self.user.dbb.update_pb()
                #self.check_stage()
        else:
            self.r = 0
            if self.max_wt > self.user.baseline and self.stage == self.user.rehab_stage:
                print("stage in stage updating bs")
                self.user.baseline = self.max_wt
                self.user.dbb.update_baseline()
        try:
            self.success_rate = (self.attempts / self.success) * 100
        except ZeroDivisionError:
            self.success_rate = 0
        self.user.dbb.log_rehab(
            {
                "max weight": self.max_wt,
                "success rate": self.success_rate,
                "time": self.seconds,
                "reps": self.attempts,
                "workout log": str(self.log),
                "activity date": self.act_date,
                "rehab": self.r,
                "stage": self.stage,
            } )
        self.user.print_graph(show=False)
        self.mainwindow.populate_info()

    def warmup(self):
        return (
            messagebox.showinfo(
                message="To warm up, do a 2-5 minutes pulse raiser activity e.g Skipping, followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals."
            )
            == "ok"
        )

    #def change_tab(self):
