import sqlite3
import qrcode
import os

os.makedirs("static/qr_codes", exist_ok=True)

conn = sqlite3.connect('students.db')
c = conn.cursor()

students = []
for i in range(1, 21):
    usn = f'USN{i:03}'
    name = f'Student{i}'
    phone = f'99999888{i:02}'
    students.append((usn, name, phone))

c.executemany("INSERT OR IGNORE INTO students (usn, name, phone) VALUES (?, ?, ?)", students)
conn.commit()

for usn, name, phone in students:
    img = qrcode.make(usn)
    img.save(f'static/qr_codes/{usn}.png')

print("✅ 20 QR codes generated and stored in static/qr_codes/")
conn.close()
