



def main():
    name = input("name: ")
    user = User(name)
    recovery_schedule = get_diagnosis(user)
    print(recovery_schedule)
    #account.record_activity()


class User():
    def __init__(self, name):
        self.name = name
        self.hand = None
        self.finger = 0
        self.num = 0
        self.pulleys = set()
        self.grade = 0
    def __str__(self):
        return f"{self.name}, grade {self.grade} injury to the {self.hand} {self.finger} digit"

def get_diagnosis(user):
    #get date

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

    while True:
        finger = int(input("Finger 1 to 5? ").strip())
        if finger in range(2, 6):
            user.finger = finger
            break
        else:
            print("usage: 1-thumb, 2-index, 3-middle, 4-ring, 5-pinky")
            continue

    while True:
        try:
            num = [int(input("Number of pulleys affected? "))]
            if num in range(1,4):
                user.num = num
            break
        except ValueError:
            print("range between at least one and maximum three")
            continue
    for num in num:
        pulley = input("Pulley affected: A")
        if pulley in range(2,5):
            if pulley in user.pulleys:
                print("already added")
            else:
                user.pulleys.add(pulley)

    while True:
        print("Grade 1: Minor tear,\nGrade 2: Major tear,\nGrade 3: Single rupture,\nGrade 4: Multiple ruptures")
        grade = int(input("Severity: Grade ").strip())
        if grade in range(1,5):
            user.grade = grade
            break
        else:
            print("Usage: input numeric grade from given scale.")
            continue

    return user




def function_2():
    ...


def function_n():
    ...


if __name__ == "__main__":
    main()
