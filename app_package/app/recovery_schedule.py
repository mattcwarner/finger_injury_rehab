class Phase:
    # stages in progressive loading
    stages = {
            0: [
                "single finger, open sling",
                "only your injured finger in isolation in an open grip using the last pad until you reach your baseline",
                (0, .25), # expected proportion of rehab time
            ],
            1: [
                "half crimp",
                "your injured hand in a half crimp position using the last pad until you reach your baseline",
                (.26, .49),
            ],
            2: [
                "full crimp",
                "your injured hand in a full crimp position using the last pad until you reach your baseline",
                (.5, .74),
            ],
            3: [
                "both hands",
                "both hands in a variety of grip types to continue strengthening your tissues and make you less prone to injury",
                (.75, 1),
            ],
        }

    recovery_phases = {
        "acute": {
            "physical characteristics": "swelling, inflamation, pain on loading",
            "recovery activities": "resting finger, icing, comfortable compression, elevation",
            "precautions": "immobilise finger, avoid loading",
        },
        "proliferation": {
            "physical characteristics": "inflamation beginning to dissipate, pain on palpation, discomfort or pain on loading",
            "recovery activities": "introducing range of movement exercises such as tendon glides, gradually resume day to day use",
            "precautions": "avoid loading injured finger, especially during climbing, perhaps keeping it immobilised",
        },
        "remodelling": {
            "physical characteristics": "pain reducing, range of movement returning to normal",
            "recovery activities": "introducing gradual progressive loading inducing mild discomfort but not to the point of pain",
            "precautions": "avoid pain during loading, use tape/pulley splint whilst climbing",
        },
    }

    # for grades of injury from 1 to 4:
    # tuples are start and finish of each phase of recovery from the day of injury
    severity = {
        1: {
            "acute": (0, 5),
            "proliferation": (3, 42),
            "remodelling": (28, 183),
        },
        2: {
            "acute": (0, 7),
            "proliferation": (5, 50),
            "remodelling": (30, 190),
        },
        3: {
            "acute": (0, 14),
            "proliferation": (10, 60),
            "remodelling": (40, 200),
        },
        4: {
            "acute": (0, 30),
            "proliferation": (25, 100),
            "remodelling": (6, 250),
        },
    }

    def __init__(self, since_inj, grade, stage):
        self.current_phase = []
        self.physical_characteristics = []
        self.current_phase_end_day = None
        self.precautions = []
        self.recovery_activities = []
        if grade in Phase.severity:
            for phase in Phase.severity[grade]:
                start, finish = Phase.severity[grade][phase]
                if since_inj in range(start, finish):
                    self.current_phase.append(phase)
                    self.rehab_length = finish
        for phase in self.current_phase:
            self.physical_characteristics.append(
                Phase.recovery_phases[phase]["physical characteristics"]
            )
            self.precautions.append(Phase.recovery_phases[phase]["precautions"])
            self.recovery_activities.append(
                Phase.recovery_phases[phase]["recovery activities"]
            )
        self.rehab_start_day = (Phase.severity[grade]["remodelling"][0]) - since_inj
        self.rehab_phase_length = (
            Phase.severity[grade]["remodelling"][1]
            - Phase.severity[grade]["remodelling"][0]
        )
        self.rehab_progress = abs(self.rehab_start_day)
        self.rehab_exp = self.get_stage_exp(stage)
        

        def __str__(self):
            return "Hello, This is the Phase class"

    def get_stage_exp(self, stage):
        current_stage_tuple = Phase.stages[stage][2]
        print(current_stage_tuple)
        st , fin = current_stage_tuple
        len_days = int(round(self.rehab_phase_length * (fin - st)))
        st_days = int(round(self.rehab_phase_length * st))
        fin_days = int(round(self.rehab_phase_length * fin))
        print(len_days, st_days, fin_days)
        print(self.rehab_progress)
        if (self.rehab_progress) in range(st_days, fin_days):
            days_in = self.rehab_progress - st_days
            print(f"days into stage = {days_in}")
            return ((days_in / len_days))
        elif self.rehab_progress > fin_days:
            return "behind schedule"
        elif self.rehab_progress < st_days:
            return "ahead of schedule"
        else:
            return "something unexpected happened"