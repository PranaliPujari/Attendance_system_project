from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from datetime import datetime
import os
import zipfile
import io
import csv
from sms_api import send_sms  # Ensure this module exists and is working

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

# Only one GET route for /scan_qr
@app.route('/scan_qr', methods=['GET'])
def scan_qr():
    return render_template('scanner.html')

# POST route for scanning QR and recording attendance
@app.route('/scan_qr', methods=['POST'])
def scan_qr_db():
    data = request.get_json()
    if not data or 'usn' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    usn = data['usn'].strip()
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')

    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Fetch student details
    c.execute("SELECT * FROM students WHERE usn=?", (usn,))
    student = c.fetchone()

    if not student:
        conn.close()
        return jsonify({'success': False, 'message': 'Student not found'}), 404

    name = student[1]
    phone = student[4]

    # Check if a login record exists for today without logout
    c.execute(
        "SELECT * FROM attendance WHERE usn=? AND date=? AND logout_time IS NULL ORDER BY login_time DESC LIMIT 1",
        (usn, date)
    )
    record = c.fetchone()

    if record:
        login_time = record[2]

        # Existing login, now logging out
        c.execute(
            "UPDATE attendance SET logout_time=? WHERE usn=? AND date=? AND login_time=?",
            (time, usn, date, login_time),
        )
        conn.commit()
        conn.close()

        send_sms(phone, f"Your child {name} (USN: {usn}) logged OUT at {time}.")
        with open('data/attendance.csv', 'a') as f:
            f.write(f"{usn},{date},{login_time},{time}\n")

        return jsonify({'success': True, 'message': '✅ Logout recorded'})
    else:
        # No login yet for today or last session already logged out
        c.execute(
            "INSERT INTO attendance (usn, date, login_time, logout_time) VALUES (?, ?, ?, NULL)",
            (usn, date, time),
        )
        conn.commit()
        conn.close()

        send_sms(phone, f"Your child {name} (USN: {usn}) marked PRESENT at {time}.")
        with open('data/attendance.csv', 'a') as f:
            f.write(f"{usn},{date},{time},\n")

        return jsonify({'success': True, 'message': '✅ Login recorded'})


@app.route('/qrcodes')
def show_qrcodes():
    qr_dir = 'static/qr_codes'
    qr_files = sorted([f for f in os.listdir(qr_dir) if f.endswith('.png')])
    return render_template('qrcodes.html', qr_files=qr_files)


@app.route('/download_all_qrcodes')
def download_all_qrcodes():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename in os.listdir('static/qr_codes'):
            if filename.endswith('.png'):
                filepath = os.path.join('static/qr_codes', filename)
                zip_file.write(filepath, arcname=filename)
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        download_name='All_QR_Codes.zip',
        as_attachment=True,
    )


@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name', '').strip()
    usn = data.get('usn', '').strip()
    department = data.get('department', '').strip()
    phone = data.get('phone', '').strip()

    if not all([name, usn, department, phone]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO students (name, usn, department, phone) VALUES (?, ?, ?, ?)",
            (name, usn, department, phone),
        )
        conn.commit()
        return jsonify({'success': True, 'message': '✅ Student added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '⚠️ USN already exists'})
    finally:
        conn.close()


@app.route('/attendance_report')
def attendance_report():
    usn = request.args.get('usn', '').strip()
    date = request.args.get('date', '').strip()

    query = '''
        SELECT attendance.usn, students.name, students.department, 
               attendance.date, attendance.login_time, attendance.logout_time
        FROM attendance
        JOIN students ON attendance.usn = students.usn
        WHERE 1=1
    '''
    params = []

    if usn:
        query += ' AND attendance.usn LIKE ?'
        params.append(f'%{usn}%')
    if date:
        query += ' AND attendance.date = ?'
        params.append(date)

    query += ' ORDER BY attendance.date DESC'

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute(query, params)
    attendance_data = c.fetchall()
    conn.close()

    return render_template('attendance_report.html', attendance_data=attendance_data)


@app.route('/export_attendance_csv')
def export_attendance_csv():
    date = request.args.get('date')
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    if date:
        c.execute(
            '''
            SELECT attendance.usn, students.name, students.department, attendance.date, attendance.login_time, attendance.logout_time
            FROM attendance
            JOIN students ON attendance.usn = students.usn
            WHERE attendance.date = ?
            ''',
            (date,),
        )
    else:
        c.execute(
            '''
            SELECT attendance.usn, students.name, students.department, attendance.date, attendance.login_time, attendance.logout_time
            FROM attendance
            JOIN students ON attendance.usn = students.usn
            '''
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['USN', 'Name', 'Department', 'Date', 'Login Time', 'Logout Time'])

    for row in c.fetchall():
        writer.writerow(row)

    conn.close()
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='attendance_report.csv',
    )
@app.route('/webcam_test')
def webcam_test():
    return render_template('webcam_test.html')


@app.route('/add_student_form')
def add_student_form():
    return render_template('add_student.html')


def send_sms_to_parent(usn, timestamp):
    try:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE usn=?", (usn,))
        student = c.fetchone()
        conn.close()

        if student:
            phone = student[4]
            name = student[1]
            message = f"Your child {name} (USN: {usn}) marked PRESENT at {timestamp}."
            print(f"Sending SMS to {phone}: {message}")
            send_sms(phone, message)
    except Exception as e:
        print("Error sending SMS:", e)


if __name__ == '__main__':
    app.run(debug=True)
