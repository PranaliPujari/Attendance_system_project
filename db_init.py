import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create students table
c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        name TEXT,
        usn TEXT PRIMARY KEY,
        department TEXT,
        phone TEXT
    )
''')

# Create attendance table
c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        usn TEXT,
        date TEXT,
        login_time TEXT,
        logout_time TEXT
    )
''')

conn.commit()
conn.close()

print("✅ Database initialized.")
