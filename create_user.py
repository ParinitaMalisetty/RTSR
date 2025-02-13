import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Insert a test user (admin) into the users table
username = 'admin'
password = 'password123'  # You can change this password to something else
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("User 'admin' with password 'password123' has been added to the database.")
