import sqlite3

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE students ADD COLUMN user_id INTEGER")
    print("✅ 'user_id' column added to 'students' table.")
except sqlite3.OperationalError as e:
    print("⚠️ Error:", e)

# === Add Admin Account ===
admin = ('admin', 'admin123', 'admin')
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", admin)

# === Add Employee Account ===

conn.commit()
print("✅ Users added successfully.")
