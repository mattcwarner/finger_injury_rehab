from datetime import datetime, date, timedelta
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from recovery_schedule import Phase

conn = sqlite3.connect("fingers.db")
db = conn.cursor()

# TO DO
# more sophisticated user system?
# better graphs?
# improve recovery sched data
# fix bugs
# clean up code
# expectations for remodelling


def main():
        
    create_tables()
    username = input("User Name: ")
    existing = db.execute("SELECT * FROM users WHERE name = ?", (username,))
    if retrv := existing.fetchone():
        user = login(username, retrv)
        print(f"Welcome Back {username.title()}")
    else:
        user = User(username)
        user = get_diagnosis(user)
    since_inj = ((date.today()) - (user.date)).days
    print(user)
    phase = recovery_sched(since_inj, user.grade)
    if 'remodelling' in phase.current_phase:

        sesh = input("Do you want to record actitity? (y/n): ")
        if sesh == "y":
            record = record_hang(user, since_inj, phase)
            print(f"Success rate: {record*100}%")
        else:
            print("maybe next time.")
        graph(user, get_progress(user))
    else:
        print(f"It's too soon for you to start rehab, but you should keep up with your recovery and come back in {phase.rehab_start_day} days to start rehab.")
    conn.close()
    sys.exit("Thanks for coming")




class User:
    def __init__(self, name):
        self.name = name
        self.hand = None
        self.finger = 0
        self.num = 0
        self.pulleys = {}
        self.grade = 0
        self.date = date
        self.id = None
        self.baseline = 0
        self.pb = 0

    def __str__(self):
        return f"{self.name.title()}: grade {self.grade} injury to the {self.hand}, {self.finger} digit, on {self.date}"


def login(username, existing):
    user = User(username)
    (
        user.id,
        user.name,
        user.date,
        user.grade,
        user.hand,
        user.finger,
        user.pulleys,
        user.baseline,
        user.pb,
    ) = existing
    user.date = date.fromisoformat(user.date)
    return user


# get injury info from user
def get_diagnosis(user):

    # give info
    print(
        f"Hello {user.name.title()}\nLets get some information from you to help tailor your rehab. \n\nWe need to find out when you were injured, where and how bad it is.\n\nFollow the interactive prompts to fill us in..."
    )

    # get date
    while True:
        inj_date = input("Injury Date (DD/MM/YYYY) (leave blank to use now)... ")
        if not inj_date:
            user.date = date.today()
            print("Ok, i'm using today.")
            break
        else:
            try:
                day, month, year = inj_date.strip().split("/")
                user.date = date(int(year), int(month), int(day)).isoformat()
                break
            except ValueError:
                response = input(
                    "Hmm, I didn't recognise that date, Enter 'y' to try again? (or enter any key to use today)..."
                )
                if response == "y":
                    print(
                        "Okay, lets try again, make sure you use the specified date format (use '/' to seperate."
                    )
                    continue
                else:
                    user.date = date.today()
                    print("Okay, i'll use today's date.")
                    break

    # hand
    while True:
        hand = (
            input("Which hand, Left or Right? (hint: type 'l' or 'r')... ")
            .lower()
            .strip()
        )
        if hand == "left" or hand == "l":
            user.hand = "left"
            break
        elif hand == "right" or hand == "r":
            user.hand = "right"
            break
        else:
            print("usage: l or r.")
            continue

    # finger
    while True:
        finger = int(
            input(
                "Which finger is it? (where 2 is your index finger and 5 is your pinky)... "
            ).strip()
        )
        if finger in range(2, 6):
            user.finger = finger
            break
        else:
            print("usage: '2' - (index), '3' - (middle), '4' - (ring), '5' - (pinky).")
            continue

    # pulleys #a1 bug
    while True:
        try:
            num = int(input("How many pulleys are affected? "))
            if num in range(1, 4):
                user.num = num
                for n in range(num):  # while len(user.pulleys) < user.num:
                    pulley = int(input("Pulley affected: A"))
                    if pulley in range(2, 5):
                        if pulley in user.pulleys:
                            print("You have already added, that pulley")
                        else:
                            severity = int(
                                input(
                                    "How bad is it, on a scale of 1 to 3;\n1 - Minor Tear,\n2 - Major Tear,\n3 - Complete Rupture\nSeverity: "
                                )
                            )
                            if severity in range(1, 4):
                                user.pulleys[n] = {
                                    "pulley": pulley,
                                    "severity": severity,
                                }

                break
        except ValueError:
            print(
                "Typically climbing related finger injuries affect between at least one and maximum three pulleys, including the A2, A3 and A4, if this doesn't describe your injury then this program will not help you, hit 'Ctrl+C' to exit the program"
            )
            continue

    # severity
    if len(user.pulleys) == 1:
        if user.pulleys[0]["severity"] == 1:
            print("You have a Grade 1 finger injury")
            user.grade = 1
        elif user.pulleys[0]["severity"] == 2:
            print("You have a Grade 2 finger injury")
            user.grade = 2
        elif user.pulleys[0]["severity"] == 3:
            print("You have a Grade 3 finger injury")
            user.grade = 3
        else:
            print("wrong number of injuries")
    elif len(user.pulleys) in range(2, 4):
        ruptures = 0
        for pulley in user.pulleys:
            if user.pulleys[pulley]["severity"] == 3:
                ruptures += 1
        if ruptures > 1:
            print("You have a grade 4 finger injury")
            user.grade = 4
        else:
            print("You have a grade 3 finger injury")
            user.grade = 3
    print(
        "Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture or multiple pulley tears,\nGrade 4: Multiple ruptures"
    )

    # insert into db
    db.execute(
        "INSERT INTO users (name, injury_grade, hand, finger, structures, injury_date) VALUES (?, ?, ?, ?, ?, ?)",
        (
            user.name,
            user.grade,
            user.hand,
            user.finger,
            str(user.pulleys),
            user.date,
        ),
    )
    conn.commit()

    # return something
    return user


# test opposite max
def test_baseline():
    attempts = 3
    print(
        "To gauge your recovery we will need to benchmark your injured finger against the opposite (hopefully) healthy finger on your other hand.\n We will get a baseline strength for that finger now... "
    )
    time.sleep(1)
    print(
        f"Nice, okay you're going to need your sling or hangboard, let's give it {attempts} attempts, try and hold the weight for 7 seconds"
    )
    time.sleep(1)
    activity = perform_sets(attempts)
    while True:
        proceed = input("Are you happy with that score or do you want to give it another go? ('y' to use current max) ...") == "y"
        if proceed:
            break
        else:
            activity = perform_sets(attempts=1)
    return activity


# set iterator
def perform_sets(attempts=3, seconds=7):
    success = 0
    max_wt = 0
    log = {}
    for i in range(attempts):
        while True:
            try:
                weight = float(input("What weight are you using? (kg)... "))
                break
            except ValueError:
                print("Enter a numeric weight")
        timer(seconds)
        tick = bool(
            input(
                f"Did you manage that? (type y if you hanged {weight}kg for {seconds} seconds)..."
            )
            .lower()
            .strip()
            == "y"
        )
        if tick and weight > max_wt:
            success += 1
            max_wt = weight
        if i < attempts - 1:
            input("Give yourself 2-3 minutes rest...")
        else:
            print("Well done.")
        log.update({f"set {i}": {"weight": weight, "success": tick}})
    return {
        "max weight": max_wt,
        "success rate": success,
        "time": seconds,
        "sets": attempts,
        "workout log": log,
    }


# rep timer
def timer(n):
    start = input("OK, when you're ready hit any 'Enter'...")
    seq = [
        "Ready",
        "Steady",
        "Go!!!!",
    ]
    for i in seq:
        print(i, end="\r")
        time.sleep(1)
    print()
    while n:
        print(n, end="\r")
        time.sleep(1)
        n -= 1


# acknowledge warmup message
def warmup():
    input(
        "To warm up, do a 2-5 minutes pulse raiser activity e.g Skipping, followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals. (Hit 'Enter' to continue)..."
    )
    return True


def record_hang(user, since_inj, phase):
    warmed_up = False
    # record activity
    if not warmed_up:
        warmed_up = warmup()
    last_sesh = db.execute("SELECT activity_date, max_weight FROM rehab WHERE user_id = ? ORDER BY activity_date DESC LIMIT 1", (user.id,)).fetchone()  # user.last
    #since_inj = ((date.today()) - (user.date)).days
    baseline = user.baseline
    if not baseline:
        activity = test_baseline()
        user.baseline = activity["max weight"]
        print(user.baseline, activity["max weight"])
        db.execute(
            "UPDATE users SET baseline = ? WHERE user_id = ?",
            (
                activity["max weight"],
                user.id,
            ),
        )
        conn.commit()
    print(user.baseline, user.pb)
    try:
        progress = user.pb / user.baseline
    except ZeroDivisionError:
        progress = 0


    sched_exp = phase.rehab_progress / phase.rehab_phase_length
    todays_wt = round(user.baseline * sched_exp)
    
    
    if since_inj > 2:
        if last_sesh:
            print(f"Okay {user.name.title()}, it's been {since_inj} days since your injury.\n\nAt this stage you might expect to be using around {todays_wt}kg ({round(sched_exp * 100)}% of your baseline, which was {baseline}kgs).\n\nYour last session was on {last_sesh[0]}, and your max was {last_sesh[1]}kg.\n\nYour personal best is {user.pb}kg, thats {(progress)*100}% of your baseline measurement, which was {user.baseline}kg\n")
        else: 
            print(f"Okay {user.name.title()}, it's been {since_inj} days since your injury, this is your first session, try to take it really slow\n")
    else:
        print("Okay take it easy, you need to wait for the acute phase to pass, come back in 3-5 days")
    mode = input(
        "Record if you're using your finger in an open, half crimp or crimp position. ('open'/'half-crimp'/'crimp')... "
    )
    try:
        attempts = int(input("sets: (leave blank to use 3 sets)..."))
    except ValueError:
        attempts = 3
    try:
        seconds = int(input("time(s): (leave blank to use 7s)... "))
    except ValueError:
        seconds = 7
    activity = perform_sets(attempts, seconds)
    if activity["max weight"] > user.pb:
        print(f"Well Done, thats a new P.B, your old P.B was {user.pb}kg, your new P.B is {activity['max weight']}kg")
        db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                activity['max weight'],
                user.id,
            ),
        )
        conn.commit()
    db.execute(
        "INSERT INTO rehab (user_id, activity_date, sets, time, max_weight, success_rate, log) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            user.id,
            date.today(),
            activity["sets"],
            activity["time"],
            activity["max weight"],
            (activity["success rate"] / activity["sets"]),
            str(activity["workout log"]),
        ),
    )
    conn.commit()
    return round(activity["success rate"] / activity["sets"])


# progress schedule
def recovery_sched(since_inj, grade):
    phase = Phase(since_inj, grade)
    if len(phase.current_phase) > 1:
        print(f"its been {since_inj} days, you're between the {phase.current_phase[0]} and {phase.current_phase[1]} phase, if you're feeling good you should be feeling {phase.physical_characteristics[1]}, otherwise you might still feel {phase.physical_characteristics[0]}, you should still be making sure you {phase.precautions[0]}. But to recover you could start to {phase.recovery_activities[1]} ")    
    else:
        print(f"its been {since_inj} days, you're in {phase.current_phase[0]}, you should be feeling {phase.physical_characteristics[0]}, you should be making sure you {phase.precautions[0]}. To recover you should be {phase.recovery_activities[0]} ")
    return phase


def get_progress(user):
    # print results and return graph of recover
    results = db.execute("SELECT * FROM rehab WHERE user_id = ?", (user.id,)).fetchall()

    for result in results:
        date = result[2]
        sets = result[3]
        time = result[4]
        max_weight = result[5]
        success_rate = result[6]
    return results


def graph(user, dict):  # sets, time, max_weight, success_rate, date #baseline
    dates = [
        0
    ]
    max_weights = [
        0,
    ]
    success_rates = [
        0,
    ]
    for result in dict:
        dates.append((date.fromisoformat(result[2]) - user.date).days)
        sets = result[3]
        time = result[4]
        max_weights.append(result[5])
        success_rates.append(result[6])

    plt.plot(
        dates,
        max_weights,
        color="red",
        linestyle="dashed",
        linewidth=3,
        marker="*",
        markerfacecolor="green",
        markersize=12,
    )
    plt.xlabel("Days Since Injury")
    plt.ylabel("Max Weight")
    plt.title("Weights over time")
    plt.show()


def create_tables():
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT, baseline REAL DEFAULT 0, pb REAL DEFAULT 0)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sets INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT)"
    )


if __name__ == "__main__":
    main()
