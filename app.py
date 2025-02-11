from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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
    conn.commit()
    conn.close()
#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # If already logged in, redirect to home
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            return redirect(url_for('index'))  # Redirect to the home page
        
        flash('Login Unsuccessful. Please check your username and password', 'danger')

    return render_template('login.html', form=form)

# Route to display all students
@app.route('/')
def index():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students)

# Route to add a student (for admin)
@app.route('/add_student', methods=['POST'])
def add_student():
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
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Query to fetch attendance data, sorted by student name and attendance date
    c.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY students.name ASC, attendance.date ASC  -- Sorting by student name and date
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

    return render_template('attendance_report.html', grouped_report=grouped_report)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
