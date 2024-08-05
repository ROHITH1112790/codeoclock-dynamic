import sqlite3

def init_db():
    conn = sqlite3.connect('form_submissions.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT,
            consent BOOLEAN NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
