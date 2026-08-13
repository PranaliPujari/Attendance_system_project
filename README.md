# Student Attendance System with QR Code and SMS Notifications

This is a comprehensive Student Attendance System built with Python, Flask, and SQLite. It simplifies the process of tracking student attendance by using QR code scanning for quick login and logout, and automatically notifies parents via SMS about their child's attendance status.

## Features

- **QR Code Scanning**: Students can scan their unique QR codes to mark attendance (login/logout).
- **Automated SMS Notifications**: Parents receive instant SMS alerts via Twilio when their child logs in or logs out.
- **Student Management**: Add new students manually through the web interface or via initialization scripts.
- **QR Code Generation**: Automatically generate and download QR codes for all registered students.
- **Attendance Reports**: View detailed attendance logs and filter them by USN or date.
- **Data Export**: Export attendance records to a CSV file for record-keeping.

## Project Structure

- `app.py`: The main Flask application that handles routing, database interactions, and business logic.
- `db_init.py` & `create_students_table.py`: Scripts to initialize the SQLite database (`students.db`) with required tables (`students`, `attendance`).
- `generate_qr_codes.py`: Script to insert default students and generate their corresponding QR codes, saving them to the `static/qr_codes` directory.
- `sms_api.py`: Module handling SMS dispatch to parents using the Twilio API.
- `students.db`: The SQLite database storing student profiles and attendance logs.
- `static/`: Directory containing static assets like generated QR code images.
- `templates/`: Directory containing HTML templates for the web application UI.

## Prerequisites

- Python 3.x
- [Twilio Account](https://www.twilio.com/) (for sending SMS notifications)

## Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd e:\CLGproject\CLGproject
   ```

2. **Install required Python packages:**
   ```bash
   pip install Flask python-dotenv twilio qrcode pillow
   ```
   *(Note: `sqlite3`, `csv`, `zipfile`, `os`, `io`, and `datetime` are part of the Python standard library).*

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (if not already present) and add your Twilio credentials:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
   ```

4. **Initialize the Database:**
   Run the initialization script to create the necessary tables in `students.db`.
   ```bash
   python db_init.py
   ```
   *(You can also use `create_students_table.py` for testing specific table creations).*

5. **Generate QR Codes:**
   Run the script to insert some dummy student records and generate their QR codes.
   ```bash
   python generate_qr_codes.py
   ```
   The generated QR codes will be saved in `static/qr_codes/`.

6. **Run the Application:**
   Start the Flask development server.
   ```bash
   python app.py
   ```

7. **Access the Web Interface:**
   Open your web browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage Workflow

1. **Add Students**: Go to the web interface to add new students, ensuring they have a valid phone number.
2. **Download QR Codes**: Navigate to the QR Codes page to view or download a ZIP file of all student QR codes.
3. **Scan QR Code**: Use the scanner interface on the web app to scan a student's QR code. 
   - On the **first scan** of the day, it marks the student as **Present (Login)** and sends an SMS to the parent.
   - On the **second scan** of the same day, it marks the student as **Logged Out** and sends an SMS to the parent.
4. **View Reports**: Check the Attendance Report page to see all logs and export them as a CSV file if needed.
