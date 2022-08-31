class Phase:

    recovery_phases = {
        "acute": {
            "physical characteristics": "swelling, inflamation, pain on loading", 
            "recovery activities": "R.I.C.E",
            "precautions": "immobilise finger, avoid loading",
            },
        "proliferation": {
            "physical characteristics": "inflamation dissipates, pain on palpation", 
            "recovery activities": "introduce range of movement, tendon glides, gradually resume day to day use",
            "precautions": "avoid loading during climbing",
            },
        "remodelling": {
            "physical characteristics": "pain reduces, range of movement back to normal", 
            "recovery activities": "gradual progressive loading inducing mild discomfort",
            "precautions": "avoid pain during loading, use tape/pulley splint whilst climbing",
        },
    }
    
    severity = {
        1: {
            "acute": (1,5),
            "proliferation": (3, 42),
            "remodelling": (28, 183),
        },
        2: {
            "acute": [1,7],
            "proliferation": [5, 50],
            "remodelling": [30, 190],
        },
        3: {
            "acute": [1,14],
            "proliferation": [10, 60],
            "remodelling": [40, 200],
        },
        4: {
            "acute": [1,30],
            "proliferation": [25, 100],
            "remodelling": [60, 250],
        }
    }

    def __init__(self, since_inj, grade):
        self.current_phase = []
        self.physical_characteristics = []
        self.current_phase_end_day = None
        self.precautions = []
        self.recovery_activities = []
        self.current_phase_end_day = 0
        self.current_phase_length = 0
        self.current_phase_progress = 0
        if grade in Phase.severity:
            for phase in Phase.severity[grade]:
                start, finish = Phase.severity[grade][phase]
                if since_inj in range(start, finish):
                    self.current_phase.append(phase)
        for phase in self.current_phase:
            self.physical_characteristics.append(Phase.recovery_phases[phase]["physical characteristics"])
            self.precautions.append(Phase.recovery_phases[phase]["precautions"])
            self.recovery_activities.append(Phase.recovery_phases[phase]["recovery activities"])
        self.rehab_start_day = (Phase.severity[grade]['remodelling'][0]) - since_inj
        self.rehab_phase_length = Phase.severity[grade]['remodelling'][1] - Phase.severity[grade]['remodelling'][0] 
        self.rehab_progress = abs(self.rehab_start_day)
        
        def __str__(self):
            print("Hello")
"""
    #CURRENT_PHASE 
    def get_phases(self, since_inj, grade):  
        if grade in Phase.severity:
            for phase in Phase.severity[grade]:
                print(Phase.severity[grade][phase])
                start, finish = Phase.severity[grade][phase]
                if since_inj in range(start, finish):
                    self.current_phase.append(phase)
    
    
    #PHYSICAL CHARACTERISTICS
    for phase in current_phase:
        physical_characteristics.append(Phase.recovery_phases[phase]["physical characteristics"])

    #PRECAUTIONS
    for phase in current_phase:
        precautions.append(Phase.recovery_phases[phase]["precautions"])

    #RECOVERY ACTIVITIES
    for phase in current_phase:
        recovery_activities.append(Phase.recovery_phases[phase]["recovery activities"])
    
    




# get day of recovery, and grade of injury from user

def recovery_sched(since_inj, grade, baseline):
    phase = Phase(since_inj, grade)
    print(phase)
    
    if len(phase.current_phase) > 1:
        print(f"its been {since_inj} days, you're between the {phase.current_phase[0]} and {phase.current_phase[1]} phase, if you're feeling good you should be feeling {phase.physical_characteristics[1]}, otherwise you might still feel {phase.physical_characteristics[0]}, you should still be making sure you {phase.precautions[0]}. But to recover you could start to {phase.recovery_activities[1]} ")    
    else:
        print(f"its been {since_inj} days, you're in {phase.current_phase[0]}, you should be feeling {phase.physical_characteristics[0]}, you should be making sure you {phase.precautions[0]}. To recover you should be {phase.recovery_activities[0]} ")
    if since_inj < phase.rehab_start_day:
        print(f"rehab begins in {phase.rehab_start_day} days.")
    else:
        print(f"rehab began {abs(phase.rehab_start_day)} days ago")
        sched_exp = phase.rehab_progress / phase.rehab_phase_length
        todays_wt = baseline * sched_exp
        print(f"we expect you to hang with {round(todays_wt)}kg, ({round(sched_exp * 100)}% of your baseline, which was {baseline}kgs)")
    return phase
recovery_sched(since_inj=40, grade=1, baseline=15)"""