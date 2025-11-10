import sqlite3
from app.db import db_path

schema = """

CREATE TABLE IF NOT EXISTS applications (
    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_name TEXT NOT NULL,
    country_name TEXT NOT NULL,
    course_name TEXT NOT NULL,
    degree_type TEXT,
    course_url TEXT,

    intake_type TEXT,
    intake_year INTEGER,

    application_open_date TEXT,
    deadline_date TEXT,

    ielts_required REAL,
    german_required TEXT,
    extra_requirements TEXT,

    application_mode TEXT,

    status TEXT NOT NULL,
    date_submitted TEXT,
    decision_date TEXT
);

CREATE TABLE IF NOT EXISTS documents_required (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    doc_name TEXT NOT NULL,
    is_required TEXT DEFAULT 'yes',
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS documents_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    doc_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'not started',
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    payment_type TEXT,
    status TEXT,
    date TEXT,
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS submission_info (
    app_id INTEGER PRIMARY KEY,
    portal_status_message TEXT,
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

CREATE TABLE IF NOT EXISTS timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    event_date TEXT,
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

"""

def db_init():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    db_init()
