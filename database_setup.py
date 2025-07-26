import sqlite3

conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    emp_id INTEGER,
    date TEXT,
    check_in TEXT,
    check_out TEXT,
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER,
    task_description TEXT,
    completed_on TEXT,
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
''')

print("Database and tables created successfully.")
conn.commit()
conn.close()
