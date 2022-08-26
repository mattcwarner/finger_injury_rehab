from datetime import datetime, date
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


conn = sqlite3.connect("fingers.db")
db = conn.cursor()


def main():
    create_tables()
    username = input("username: ")
    existing = db.execute("SELECT * FROM users WHERE name = ?", (username,))
    if existing:
        retrv = existing.fetchone()
        user = login(username, retrv)
        print(f"Welcome Back {username.title()}")
    else:
        user = User(username)
        user = get_diagnosis(user)
    print(user)
    sesh = input("Do you want to record actitity? (y/n): ")
    if sesh == "y":
        record = record_hang(user)
        print(record)
    else:
        print("maybe next time.")
    graph(user, get_progress(user))
    conn.close()


class User:
    def __init__(self, name):
        self.name = name
        self.hand = None
        self.finger = 0
        self.num = 0
        self.pulleys = set()
        self.grade = 0
        self.date = None
        self.id = None

    def __str__(self):
        return f"{self.name}, grade {self.grade} injury to the {self.hand} {self.finger} digit"


def login(username, existing):
    user = User(username)
    user.id = existing[0]
    user.date = existing[2]
    user.grade = existing[3]
    user.hand = existing[4]
    user.finger = existing[5]
    user.pulleys = set(existing[6])
    return user


def get_diagnosis(user):

    # get date
    inj_date = input("Injury Date (DD/MM/YYYY) (leave blank to use now): ")
    if not inj_date:
        user.date = date.today()
        print("using today")
    else:
        try:
            day, month, year = inj_date.strip().split("/")
            user.date = date(int(year), int(month), int(day)).isoformat()
        except ValueError:
            print(
                "Didn't recognise date, using todays date, hit Ctr-C to interrupt and start again"
            )

    # hand
    while True:
        hand = input("Left or Right? ").lower().strip()
        if hand == "left" or hand == "l":
            user.hand = "left"
            break
        elif hand == "left" or hand == "r":
            user.hand = "right"
            break
        else:
            print("usage: l or r")
            continue

    # finger
    while True:
        finger = int(input("Finger 1 to 5? ").strip())
        if finger in range(2, 6):
            user.finger = finger
            break
        else:
            print("usage: 1-thumb, 2-index, 3-middle, 4-ring, 5-pinky")
            continue

    # pulleys
    while True:
        try:
            num = int(input("Number of pulleys affected? "))
            if num in range(1, 4):
                user.num = num
                for num in range(num):
                    pulley = int(input("Pulley affected: A"))
                    if pulley in range(1, 5):
                        if pulley in user.pulleys:
                            print("already added")
                        else:
                            user.pulleys.add(pulley)
                break
        except ValueError:
            print("range between at least one and maximum three")
            continue

    # grade
    while True:
        print(
            "Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture,\nGrade 4: Multiple ruptures"
        )
        grade = int(input("Severity: Grade ").strip())
        if grade in range(1, 5):
            user.grade = grade
            break
        else:
            print("Usage: input numeric grade from given scale.")
            continue

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


#test opposite max


def record_hang(user):
    # record activity
    print(
        "you must warm up by doing a pulse raiser followed by 5 hangs/pulls increasing from 30% to 80% max in 10% intervals"
    )
    mode = input("open/ half or full crimp: ")
    sets = int(input("sets: "))
    time = int(input("time(s): "))
    log = {}
    max_weight = 0
    success = 0
    for set in range(sets):
        weight = float(input("new rep, weight(kg): "))
        tick = bool(
            input(f"type y if you hanged {weight}kg, {mode} for {time} seconds...")
            .lower()
            .strip()
            == "y"
        )
        if tick:
            success += 1
            if weight > max_weight:
                max_weight = weight
        log.update({f"set {set}": {"weight": weight, "tick": tick}})
    db.execute(
        "INSERT INTO rehab (user_id, activity_date, sets, time, max_weight, success_rate, log) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user.id, datetime.today(), sets, time, max_weight, (success / sets), str(log)),
    )
    conn.commit()
    return {
        "user": str(user),
        "activity_date": datetime.today().isoformat(),
        "mode": mode,
        "sets": sets,
        "time": time,
        "log": log,
        "max_weight": max_weight,
        "success_rate": success/sets,
    }


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


def graph(user, dict):#sets, time, max_weight, success_rate, date
    dates = [user.date, ]
    max_weights = [0,]
    success_rates = [0, ]
    for result in dict:
        dates.append(result[2])
        sets = result[3]
        time = result[4]
        max_weights.append(result[5])
        success_rates.append(result[6])
    
    plt.plot(dates, max_weights, color="red", linestyle="dashed", linewidth=3, marker="*", markerfacecolor="green", markersize=12 )
    plt.xlabel("Activity Date")
    plt.ylabel("Max Weight")
    plt.title("Weights over time")
    plt.show()


def create_tables():
    db.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, sets INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT)"
    )


if __name__ == "__main__":
    main()
