UPASTHITI - Digitalized Register

**UPASTHITI** is a digitalized attendance register system built using Flask and SQLite, designed to simplify and streamline attendance tracking for educational institutions.

---

## 📌 Features

- ✅ Student registration and management  
- 🕒 Attendance marking with real-time validation  
- 📅 Calendar-based attendance viewing  
- 📊 Attendance reports with percentage calculation  
- 🔐 Login/logout functionality for staff  
- 🚫 Prevents attendance on Sundays  
- 🟡 Sick leave marking with no effect on overall percentage  
- 🔍 Searchable student reports  
- 📱 Offline support via PWA (Progressive Web App) features

---

## 📁 Project Structure

```

UPASTHITI-Digitalized-Register/
│
├── app.py                # Main Flask backend
├── templates/            # HTML templates (Jinja2)
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── attendance.html
│   └── report.html
├── static/               # Static files (CSS, JS, icons)
│   └── ...
├── database/             # SQLite database file
│   └── attendance.db
├── service-worker.js     # Offline PWA support
└── README.md             # This file

````

---

## ⚙️ Requirements

- Python 3.x
- Flask
- SQLite3

Install dependencies (if needed):
```bash
pip install flask
````

---

## 🚀 Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ParinitaMalisetty/UPASTHITI-Digitalized-Register.git
   cd UPASTHITI-Digitalized-Register
   ```

2. **Run the Flask app**:

   ```bash
   python app.py
   ```

3. Open your browser and go to `http://localhost:5000`

---

## 🧪 Usage

* Login as an admin/staff.
* Add students to the system.
* Mark daily attendance (with sick leave option).
* View attendance reports with color-coded statuses:

  * ✅ Present
  * ❌ Absent
  * 🟡 Sick Leave
* Export or analyze attendance by date or student.

---

## 🛠️ Developer Notes

* Sunday attendance is automatically disabled in the calendar.
* All logic for marking attendance, calculating reports, and sick leave handling is in `app.py`.
* Works offline using service workers and cache-based storage.

---

## 👩‍💻 Author

**Parinita Malisetty**
📎 [GitHub Profile](https://github.com/ParinitaMalisetty)

---

## 📃 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⭐️ Support

If you find this project helpful, give it a ⭐️ on GitHub!

