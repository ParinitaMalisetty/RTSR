from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__, static_folder='static')
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
    password TEXT NOT NULL,
    role TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exam_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    exam_type TEXT CHECK(exam_type IN ('Mid 1', 'Mid 2', 'End Sem')),
    subject TEXT,
    marks INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id)
)''')


    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            if role == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            return "Invalid credentials or role. Please try again."

    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    username = session.get('username')

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Attendance records
    c.execute("""
        SELECT attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE students.name = ?
        ORDER BY attendance.date DESC
    """, (username,))
    records = c.fetchall()

    # Attendance percentage
    total_classes = sum(1 for _, status in records if status != 'Sick Leave')
    absent_count = sum(1 for _, status in records if status == 'Absent')
    attendance_percentage = max(100 - ((absent_count / total_classes) * 100), 0) if total_classes > 0 else 100

    # Fetch student ID
    c.execute("SELECT id FROM students WHERE name = ?", (username,))
    student_id = c.fetchone()[0]

    # Fetch exam marks
    c.execute("""
        SELECT exam_type, subject, marks
        FROM exam_marks
        WHERE student_id = ?
        ORDER BY exam_type, subject
    """, (student_id,))
    exam_data = c.fetchall()

    # Organize by exam type
    from collections import defaultdict
    exams = defaultdict(list)
    for exam_type, subject, marks in exam_data:
        exams[exam_type].append((subject, marks))

    conn.close()

    return render_template(
        'student_dashboard.html',
        username=username,
        records=records,
        attendance_percentage=round(attendance_percentage, 2),
        exams=exams
    )


@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    is_admin = 'user_id' in session and session.get('role') == 'admin'

    if request.method == 'POST':
        name = request.form['name']
        username = name  # using name as username
        password = request.form.get('password') or 'student123'
        role = 'student'

        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()

        # Check if user already exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return f"Username '{username}' already exists."

        # Create user
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, password, role))
        user_id = c.lastrowid

        # Create student linked to user
        c.execute("INSERT INTO students (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        conn.close()

        if is_admin:
            return f"✅ Student '{name}' added with default password."
        else:
            return "✅ Registration successful! <a href='/login'>Login here</a>"

    return render_template('student_register.html', is_admin=is_admin)

@app.route('/admin/exam_marks', methods=['GET', 'POST'])
def manage_exam_marks():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Fetch students for dropdown
    c.execute("SELECT id, name FROM students")
    students = c.fetchall()

    message = ''

    if request.method == 'POST':
        student_id = request.form['student_id']
        exam_type = request.form['exam_type']
        subject = request.form['subject']
        marks = request.form['marks']

        # Check if record exists
        c.execute("""
            SELECT id FROM exam_marks
            WHERE student_id = ? AND exam_type = ? AND subject = ?
        """, (student_id, exam_type, subject))
        existing = c.fetchone()

        if existing:
            # Update existing record
            c.execute("""
                UPDATE exam_marks
                SET marks = ?
                WHERE id = ?
            """, (marks, existing[0]))
            message = '✅ Marks updated successfully.'
        else:
            # Insert new record
            c.execute("""
                INSERT INTO exam_marks (student_id, exam_type, subject, marks)
                VALUES (?, ?, ?, ?)
            """, (student_id, exam_type, subject, marks))
            message = '✅ Marks added successfully.'

        conn.commit()

    conn.close()
    return render_template('manage_exam_marks.html', students=students, message=message)
@app.route('/student/exam_report')
def student_exam_report():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    username = session.get('username')

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Get student ID
    c.execute("SELECT id FROM students WHERE name = ?", (username,))
    student_id = c.fetchone()[0]

    # Get marks
    c.execute("""
        SELECT exam_type, subject, marks
        FROM exam_marks
        WHERE student_id = ?
    """, (student_id,))
    records = c.fetchall()
    conn.close()

    # Organize by subject
    from collections import defaultdict
    subject_scores = defaultdict(dict)
    for exam_type, subject, marks in records:
        subject_scores[subject][exam_type] = marks

    # Calculate mid average
    for subject in subject_scores:
        mid1 = subject_scores[subject].get('Mid 1', 0)
        mid2 = subject_scores[subject].get('Mid 2', 0)
        avg = (mid1 + mid2) / 2 if 'Mid 1' in subject_scores[subject] or 'Mid 2' in subject_scores[subject] else None
        subject_scores[subject]['Mid Avg'] = round(avg, 2) if avg is not None else 'N/A'

    return render_template('exam_report.html', username=username, subject_scores=subject_scores)

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

    search_query = request.args.get('search', '').strip().lower()

    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    c.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE strftime('%w', attendance.date) != '0'
        ORDER BY students.name ASC, attendance.date DESC
    """)
    report = c.fetchall()
    conn.close()

    grouped_report = {}
    attendance_percentages = {}

    for name, date, status in report:
        if name not in grouped_report:
            grouped_report[name] = []
        grouped_report[name].append((date, status))

    # 🔍 Filter by search query
    if search_query:
        grouped_report = {
            name: records for name, records in grouped_report.items()
            if search_query in name.lower()
        }

    for student, records in grouped_report.items():
        total_classes = sum(1 for _, status in records if status != 'Sick Leave')
        absent_count = sum(1 for _, status in records if status == 'Absent')

        attendance_percentage = (
            max(100 - ((absent_count / total_classes) * 100), 0) if total_classes > 0 else 100
        )
        attendance_percentages[student] = round(attendance_percentage, 2)

    return render_template(
        'attendance_report.html',
        grouped_report=grouped_report,
        attendance_percentages=attendance_percentages
    )

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    with sqlite3.connect('attendance.db') as conn:
        c = conn.cursor()

        # Delete related attendance and exam records first to maintain integrity
        c.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        c.execute("DELETE FROM exam_marks WHERE student_id = ?", (student_id,))

        # Get the user_id of the student to delete from users table
        c.execute("SELECT user_id FROM students WHERE id = ?", (student_id,))
        user = c.fetchone()
        if user:
            c.execute("DELETE FROM users WHERE id = ?", (user[0],))

        # Delete from students table
        c.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

    return redirect(url_for('login'))

    

@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
