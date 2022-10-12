from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry 
from user import Dbb
 


class Diagnose:
    def __init__(self, parent):
        print(parent.user.name)
        self.parent = parent
        self.parent.diagnosis_info.set(
            f"Hello {self.parent.user.name.title()}\nLets get some information from you to help tailor your rehab.\nWe need to find out when you were injured, where and how bad it is.\nFollow the interactive prompts to fill us in..."
        )
        self.name = self.parent.user.name
        print(self.name)
        self.get_date()
            
        
        # parent.notebook_diagnosis
        

    def get_date(self):
                
        self.parent.recovery_info.set(
            'What date did you get injured?'
        )
        #adapted from https://www.plus2net.com/python/tkinter-DateEntry.php
        cal=DateEntry(self.parent.notebook_diagnosis,selectmode='day')
        cal.grid(row=3,column=0,padx=20,pady=30, sticky=(N,W))

        def my_upd(): # triggered on Button Click
            #l1.config(text=cal.get_date()) # read and display date
            #l1.config(text=cal.get()) #  using Entry widget get() 
            dt=cal.get_date()
            # str=dt.strftime("%d-%m-%Y") # changing the format 
            l1.config(text=dt)
            self.date = dt
            print(self.date)
            
            cal.grid_forget()
            l1.grid_forget()
            b1.grid_forget()
            self.get_structs()
            return True

        l1=ttk.Label(self.parent.notebook_diagnosis,text='Injury Date')  # Label to display date 
        l1.grid(row=4,column=0, sticky=(N,W))

        b1=ttk.Button(self.parent.notebook_diagnosis,text='Set Date', command=lambda:my_upd())
        b1.grid(row=5,column=0, sticky=(N,W))

    def get_structs(self):
        self.parent.diagnosis_info.set('Structures Injured:')
        self.parent.recovery_info.set(
            'Where did you get injured?'
        )
        def my_hand():
            self.hand = str(self.hand.get())
            print(self.hand)
            
            self.finger = int(self.finger.get())
            print(self.finger)
            
            self.pulleys = list(p.curselection())
            for i in self.pulleys:
                print(self.pulleys_idx[i])
            
            structs.grid_forget()
            self.get_severity()


        self.hand = StringVar()
        structs = ttk.Frame(self.parent.notebook_diagnosis)
        structs.grid(row=4, column=0, columnspan=1)
        
        left = ttk.Radiobutton(structs, text="Left Hand", variable=self.hand, value='left')
        left.grid(row=0, column=0)
        right = ttk.Radiobutton(structs, text="Right Hand", variable=self.hand, value='right')
        right.grid(row=0, column=1)

        self.finger = StringVar()
        f1 = ttk.Radiobutton((structs), text="First Finger", variable=self.finger, value=1)
        f1.grid(row=1, column=0,)
        f2 = ttk.Radiobutton((structs), text="Middle Finger", variable=self.finger, value=2)
        f2.grid(row=1, column=1,)
        f3 = ttk.Radiobutton((structs), text="Ring Finger", variable=self.finger, value=3)
        f3.grid(row=2, column=0,)
        f4 = ttk.Radiobutton((structs), text="Pinky Finger", variable=self.finger, value=4)
        f4.grid(row=2, column=1,)

        self.pulleys_idx = ['A2', 'A3', 'A4',]
        pulleysvar = StringVar(value=self.pulleys_idx)
        p = Listbox(structs, height=3, selectmode='multiple', listvariable=pulleysvar)
        p.grid(row=3, column=0)
        
        b1=ttk.Button(structs, text='Set Hand', command=lambda:my_hand())
        b1.grid(row=4,column=0,)

        
    def get_severity(self):
        self.parent.diagnosis_info.set('How bad is it?')
        self.parent.recovery_info.set("Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture or multiple pulley tears,\nGrade 4: Multiple ruptures")

        def my_sev():
            self.grade = int(self.grade.get())
            print (self.grade)
            sev.grid_forget()
            self.submit_diagnosis()

        self.grade = StringVar()
        sev = ttk.Frame(self.parent.notebook_diagnosis)
        sev.grid(row=4, column=0, columnspan=1)
        g1 = ttk.Radiobutton((sev), text="Grade I", variable=self.grade, value=1)
        g1.grid(row=1, column=0,)
        g2 = ttk.Radiobutton((sev), text="Grade II", variable=self.grade, value=2)
        g2.grid(row=2, column=0,)
        g3 = ttk.Radiobutton((sev), text="Grade III", variable=self.grade, value=3)
        g3.grid(row=3, column=0,)
        g4 = ttk.Radiobutton((sev), text="Grade IV", variable=self.grade, value=4)
        g4.grid(row=4, column=0,)

        b1=ttk.Button(sev, text='Set Grade', command=lambda:my_sev())
        b1.grid(row=5,column=0,)

    def submit_diagnosis(self):
        """self.parent.user.grade = self.grade
        self.parent.user.hand = self.hand
        self.parent.user.finger = self.finger
        self.parent.user.pulleys = self.pulley
        self.parent.user.date = self.date"""

        dbbb = Dbb(self)
        dbbb.diagnosis(self.name, self.grade, self.hand, self.finger, str(self.pulleys), self.date,)
        dbbb.exit_script()
        self.parent.login_check()
        self.parent.recovery_info.set(":)")
        
