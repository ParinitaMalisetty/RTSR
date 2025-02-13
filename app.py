from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

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
                    password TEXT NOT NULL)''')  # Make sure this line exists
    conn.commit()
    conn.close()

# Route to display the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Print out the values being checked
        print(f"Attempting to log in with username: {username} and password: {password}")

        # Check the credentials (for simplicity, let's assume the first user in the users table is admin)
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]  # Store user_id in the session
            return redirect(url_for('index'))
        else:
            return "Invalid credentials, please try again."

    return render_template('login.html')

# Route to display all students
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

# Route to add a student (for admin)
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

# Route to mark attendance
@app.route('/mark_attendance/<int:student_id>', methods=['GET', 'POST'])
def mark_attendance(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        status = request.form['status']
        date = request.form['date']
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                  (student_id, date, status))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('mark_attendance.html', student_id=student_id)

# Route to view attendance report
@app.route('/attendance_report')
def attendance_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    sort_by = request.args.get('sort_by', 'name_asc')

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Query to fetch attendance data
    c.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
    """)
    report = c.fetchall()
    conn.close()

    # Organize the data into a dictionary grouped by student name
    grouped_report = {}
    for row in report:
        name, date, status = row
        if name not in grouped_report:
            grouped_report[name] = []
        grouped_report[name].append((date, status))

    # Sort the grouped report based on the selected sort_by parameter
    if sort_by == 'name_asc':
        grouped_report_sorted = {k: v for k, v in sorted(grouped_report.items())}
    elif sort_by == 'name_desc':
        grouped_report_sorted = {k: v for k, v in sorted(grouped_report.items(), reverse=True)}
    elif sort_by == 'date_asc':
        grouped_report_sorted = {k: sorted(v, key=lambda x: x[0]) for k, v in grouped_report.items()}
    elif sort_by == 'date_desc':
        grouped_report_sorted = {k: sorted(v, key=lambda x: x[0], reverse=True) for k, v in grouped_report.items()}
    elif sort_by == 'present':
        # Sorting by 'Present' first (Present = 1, Absent = 0)
        grouped_report_sorted = {k: sorted(v, key=lambda x: (x[1] != 'Present', x[0])) for k, v in grouped_report.items()}
    elif sort_by == 'absent':
        # Sorting by 'Absent' first (Absent = 1, Present = 0)
        grouped_report_sorted = {k: sorted(v, key=lambda x: (x[1] != 'Absent', x[0])) for k, v in grouped_report.items()}
    else:
        grouped_report_sorted = grouped_report  # Default sort

    return render_template('attendance_report.html', grouped_report=grouped_report_sorted)

# Route to log out
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
