from tkinter import *
from tkinter import ttk, messagebox
import time
#from pygame import mixer




class Timer:
    #mixer.init()
    #sound = mixer.Sound("bell.wav")
    # rep timer
    def __init__(self, root, n):
        self.root = root
        self.success = False
        self.n = n
        self.win = Toplevel(self.root)
        self.win.title("Timer")
        #win.minsize(50, 50)
        #win.geometry(f'100x100-5+5')
        self.f = ttk.Frame(self.win, padding=4)
        self.f.grid(column=0, row=0, sticky=(N,E,S,W))
        self.f.columnconfigure(0, weight=1)
        self.f.rowconfigure(0, weight=1)
        self.st_btn = ttk.Button(self.f, text="Start", command=lambda: self.countdown(self.n))
        self.win.bind("<Return>", lambda e: self.countdown((self.n)))
        self.st_btn.grid(column=0, row=1)
        self.st_btn.focus()
        self.secs = StringVar()
        self.secs.set(f"{self.n} seconds, ready?")
        self.secs_label = ttk.Label(self.f, textvariable=self.secs, font=('Arial', 50))
        self.secs_label.grid(column=0, row=0)
        self.win.mainloop()
        
        

    def countdown(self, n):
        self.st_btn.config(text="Reset")
        
        seq = [
            "Ready",
            "Steady",
            "Go!!!!",
        ]
        for i in seq:
            self.secs.set(i)
            self.win.update()
            #Timer.sound.play()
            time.sleep(1)
            
        while n:
            #if n < 4:
                #Timer.sound.play()
            self.secs.set(str(n))
            self.win.update()
            n -= 1
            time.sleep(1)
            
        self.secs.set("Time Up")
        self.win.quit()
        self.success = messagebox.askyesno(message="Did you complete that rep?", icon='question', title="Rep Success?")
        
    

# test script
"""root = Tk()
timer= Timer(root, 3)
print(timer.success)"""