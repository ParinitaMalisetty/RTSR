from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for session management

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    date TEXT,
                    status TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL)''')  
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]  
            return redirect(url_for('index'))
        else:
            return "Invalid credentials, please try again."

    return render_template('login.html')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/mark_attendance/<int:student_id>', methods=['GET', 'POST'])
def mark_attendance(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form['date']
        status = request.form['status']

        selected_date = datetime.strptime(date, "%Y-%m-%d")
        if selected_date.weekday() == 6:  
            return "Attendance cannot be marked on Sundays. Please select another date."

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()

        c.execute("DELETE FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
        c.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, date, status))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('mark_attendance.html', student_id=student_id)

# Route to view attendance report with percentage calculation
@app.route('/attendance_report')
def attendance_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Fetch attendance records, excluding Sundays
    c.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE strftime('%w', attendance.date) != '0'  -- Exclude Sundays
        ORDER BY students.name ASC, attendance.date DESC
    """)
    report = c.fetchall()
    conn.close()

    # Organize attendance records per student
    grouped_report = {}
    attendance_percentages = {}

    for name, date, status in report:
        if name not in grouped_report:
            grouped_report[name] = []
        grouped_report[name].append((date, status))

    # Calculate attendance percentage excluding sick leaves
    for student, records in grouped_report.items():
        total_classes = sum(1 for _, status in records if status != 'Sick Leave')
        absent_count = sum(1 for _, status in records if status == 'Absent')

        if total_classes > 0:
            attendance_percentage = max(100 - ((absent_count / total_classes) * 100), 0)
        else:
            attendance_percentage = 100  # If no records, assume full attendance

        attendance_percentages[student] = round(attendance_percentage, 2)  # Round to 2 decimal places

    return render_template(
        'attendance_report.html',
        grouped_report=grouped_report,
        attendance_percentages=attendance_percentages
    )

@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
