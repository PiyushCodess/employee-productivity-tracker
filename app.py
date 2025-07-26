import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# ✅ Connect to SQLite database
conn = sqlite3.connect('employees.db', check_same_thread=False)
cursor = conn.cursor()

# ✅ Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL
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

conn.commit()

# 🔧 Add new employee
def add_employee(name, department):
    cursor.execute("INSERT INTO employees (name, department) VALUES (?, ?)", (name, department))
    conn.commit()

# 🔧 Log attendance
def log_attendance(emp_id, check_in, check_out):
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute("INSERT INTO attendance (emp_id, date, check_in, check_out) VALUES (?, ?, ?, ?)",
                   (emp_id, date, check_in, check_out))
    conn.commit()

# 🔧 Log task
def log_task(emp_id, description):
    completed_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO tasks (emp_id, task_description, completed_on) VALUES (?, ?, ?)",
                   (emp_id, description, completed_on))
    conn.commit()

# 🖥️ Streamlit Layout
st.title("🧑‍💻 Employee Productivity Tracker")

menu = st.sidebar.selectbox("Choose Action", ["Add Employee", "Log Attendance", "Log Task", "Reports"])

if menu == "Add Employee":
    st.subheader("Add New Employee")
    name = st.text_input("Name")
    department = st.text_input("Department")
    if st.button("Add"):
        if name and department:
            add_employee(name, department)
            st.success("✅ Employee added successfully!")
        else:
            st.warning("Please fill in all fields.")

elif menu == "Log Attendance":
    st.subheader("Log Attendance")
    emp_id = st.number_input("Employee ID", min_value=1)
    check_in = st.text_input("Check-In Time (HH:MM)")
    check_out = st.text_input("Check-Out Time (HH:MM)")
    if st.button("Submit"):
        if check_in and check_out:
            log_attendance(emp_id, check_in, check_out)
            st.success("✅ Attendance recorded!")
        else:
            st.warning("Please enter both check-in and check-out times.")

elif menu == "Log Task":
    st.subheader("Log Task")
    emp_id = st.number_input("Employee ID", min_value=1)
    task = st.text_input("Task Description")
    if st.button("Submit Task"):
        if task:
            log_task(emp_id, task)
            st.success("✅ Task logged successfully!")
        else:
            st.warning("Please enter a task description.")

elif menu == "Reports":
    st.subheader("📊 Weekly Reports")

    try:
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        df_att = pd.read_sql_query("SELECT * FROM attendance", conn)
        df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)

        st.write("📋 Employees", df_emp)
        st.write("🕒 Attendance (latest 10)", df_att.tail(10))
        st.write("✅ Tasks (latest 10)", df_tasks.tail(10))

        merged = pd.merge(df_tasks, df_emp, on="emp_id", how="left")
        task_summary = merged.groupby("name").count()["task_description"]

        st.subheader("📈 Tasks Completed per Employee")
        st.bar_chart(task_summary)

    except Exception as e:
        st.error(f"Error loading reports: {e}")
