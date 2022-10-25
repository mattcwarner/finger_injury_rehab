import sqlite3


class Dbb():
    def __init__(self, user):
        # connect to db
        self.conn = sqlite3.connect("../fingers.db")
        self.db = self.conn.cursor()
        self.create_tables()
        self.user = user

    def exit_script(self):
        self.conn.close()

    def lookup(self):
        self.create_tables()
        info = self.db.execute(
            "SELECT user_id, name, injury_date, injury_grade, hand, finger, structures, baseline, pb, rehab_stage FROM users WHERE name = ?",
            (self.user.name,),
        ).fetchone()
        if info:
            return info
        else:
            return False

    def get_max(self, stage, mode=1, date=1):
        # mode represents whether the activity was a baseline recording (0/False), or rehab activity (1/True)
        if date:
            values = self.db.execute("SELECT max_weight, activity_date from rehab WHERE user_id = ? AND rehab_stage = ? AND rehab = ?", (self.user.id, stage, mode,), ).fetchall()
        else: 
            values = self.db.execute("SELECT max_weight from rehab WHERE user_id = ? AND rehab_stage = ? AND rehab = ? ORDER BY max_weight DESC LIMIT 1", (self.user.id, stage, mode,), ).fetchone()
        if values:
            return values
        else:
            return 0

    def progress(self):
        return self.db.execute(
            "SELECT activity_date, reps, time, max_weight, success_rate, rehab_stage FROM rehab WHERE user_id = ?",
            (self.user.id,),
        ).fetchall()

    def log_rehab(self, activity):
        self.db.execute(
            "INSERT INTO rehab (user_id, activity_date, rehab, reps, time, max_weight, success_rate, log, rehab_stage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.user.id,
                activity["activity date"],
                activity["rehab"],
                activity["reps"],
                activity["time"],
                activity["max weight"],
                (activity["success rate"]),
                str(activity["workout log"]),
                activity["stage"],
            ),
        )
        self.conn.commit()

    def update_pb(self):
        self.db.execute(
            "UPDATE users SET pb = ? WHERE user_id = ?",
            (
                self.user.pb,
                self.user.id,
            ),
        )
        self.conn.commit()

    def update_stage(self):
        print(f"user rehab stage updated to {self.user.rehab_stage}")
        self.db.execute(
            "UPDATE users SET rehab_stage = ? WHERE user_id = ?",
            (
                self.user.rehab_stage,
                self.user.id,
            ),
        )
        self.conn.commit()

    def update_baseline(self):
        self.db.execute(
            "UPDATE users SET baseline = ? WHERE user_id = ?",
            (
                self.user.baseline,
                self.user.id,
            ),
        )
        self.conn.commit()

    def diagnosis(self, name, grade, hand, finger, pulleys, date):
        self.db.execute(
            "INSERT INTO users (name, injury_grade, hand, finger, structures, injury_date) VALUES (?, ?, ?, ?, ?, ?)",
            (
                name,
                grade,
                hand,
                finger,
                pulleys,
                date,
            ),
        )
        self.conn.commit()

    def last_sesh(self):
        return self.db.execute(
            "SELECT activity_date, max_weight, rehab_stage FROM rehab WHERE user_id = ? AND rehab = 1 ORDER BY activity_date DESC, max_weight DESC LIMIT 1",
            (self.user.id,),
        ).fetchone()

    def create_tables(self):
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, name TEXT NOT NULL, injury_date TEXT NOT NULL DEFAULT CURRENT_DATE, injury_grade INTEGER, hand TEXT, finger INTEGER, structures TEXT, baseline REAL DEFAULT 0, pb REAL DEFAULT 0, rehab_stage INTEGER DEFAULT 0)"  # , h_baseline REAL DEFAULT 0, h_pb REAL DEFAULT 0, f_baseline REAL DEFAULT, f_pb REAL DEFAULT 0)"
        )
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS rehab (activity_id INTEGER PRIMARY KEY ASC AUTOINCREMENT, user_id REFERENCES users (user_id), activity_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, rehab INTEGER DEFAULT TRUE, reps INTEGER, time INTEGER, max_weight REAL, success_rate REAL, log TEXT, rehab_stage INTEGER DEFAULT 0)"
        )
        self.db.execute("CREATE INDEX IF NOT EXISTS name_index ON users (name)")
