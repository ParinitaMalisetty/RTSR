import sqlite3

# === CONFIGURE ADMIN ACCOUNT HERE ===
username = 'admin'
password = 'admin123'
role = 'admin'
# ====================================
username= 'emp1'
password= 'emp123'
role= 'employee'
# Connect to the SQLite database
conn = sqlite3.connect('attendance.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE students ADD COLUMN user_id INTEGER")
    print("✅ 'user_id' column added to 'students' table.")
except sqlite3.OperationalError as e:
    print("⚠️ Error:", e)

# Insert admin user into users table
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
conn.commit()
