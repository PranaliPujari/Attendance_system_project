import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create the students table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    usn TEXT NOT NULL UNIQUE,
    department TEXT,
    phone TEXT NOT NULL
)
''')

# Optional: Insert test data
c.execute('INSERT OR IGNORE INTO students (name, usn, department, phone) VALUES (?, ?, ?, ?)',
          ('Test Student', '1RV23CS001', 'CSE', '9876543210'))

conn.commit()
conn.close()

print("✅ Table created and test data inserted.")
