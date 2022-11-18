from tkinter import *
from tkinter import ttk, messagebox
import time


class Timer:
    def __init__(self, root, n, s=False):
        self.root = root
        self.success = False
        self.check = s
        self.n = n
        self.tmp = n
        self.finished = False
        self.start_timer()

    def start_timer(self):
        self.set_window()
        self.f.mainloop()

    def set_window(self):
        self.f = ttk.Frame(self.root, padding=4)
        self.f.grid(column=0, row=0, sticky=(N,E,S,W))
        self.f.columnconfigure(0, weight=1)
        self.f.rowconfigure(0, weight=1)
        self.st_btn = ttk.Button(self.f, text="Start", command=lambda: self.countdown())
        self.root.bind("<Return>", lambda e: self.countdown(()))
        self.st_btn.grid(column=0, row=1)
        self.st_btn.focus()
        self.cancel_btn = ttk.Button(self.f, text="Finish", command=lambda: self.exit_timer())
        self.cancel_btn.grid(column=0, row=2)
        self.secs = StringVar()
        self.secs.set(f"{self.n} seconds...")
        self.secs_label = ttk.Label(self.f, textvariable=self.secs, font=('Arial', 50))
        self.secs_label.grid(column=0, row=0)
           
    def exit_timer(self):
        self.n = 0
        self.f.destroy()
        self.f.quit()
        if not self.check:
            self.success = messagebox.askyesno(message="Did you complete that rep?", icon='question', title="Rep Success?")
            self.check = True
        self.root.unbind("<Return>")
        self.finished = True
        return 1
    
    def get_success(self):
        return self.success

    def countdown(self, r=0):
        """if r:
           
            self.n = self.tmp
            self.start_timer

        self.st_btn.config(text="Reset", command=lambda: self.countdown(r=1))
        self.root.bind("<Return>", lambda e: self.countdown(r=1))"""
        
        seq = [
            "Ready",
            "Steady",
            "Go!!!!",
        ]
        for i in seq:
            self.secs.set(i)
            self.f.update()
            #Timer.sound.play()
            time.sleep(1)
            
        while self.n:
            #if n < 4:
                #Timer.sound.play()
            self.secs.set(str(self.n))
            self.f.update()
            self.n -= 1
            time.sleep(1)
            
        self.secs.set("Time Up")
        self.f.update()
        time.sleep(1)
        self.exit_timer()

# test script
"""root = Tk()
timer= Timer(root, 3)
print(timer.success)"""