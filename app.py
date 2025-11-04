import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import os

# ✅ Ensure database exists in Render's environment
DB_PATH = os.path.join(os.getcwd(), "employees.db")

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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

# 🔧 Helper functions
def add_employee(name, department):
    cursor.execute("INSERT INTO employees (name, department) VALUES (?, ?)", (name, department))
    conn.commit()

def log_attendance(emp_id, check_in, check_out):
    date = datetime.today().strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO attendance (emp_id, date, check_in, check_out) VALUES (?, ?, ?, ?)",
        (emp_id, date, check_in, check_out)
    )
    conn.commit()

def log_task(emp_id, description):
    completed_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO tasks (emp_id, task_description, completed_on) VALUES (?, ?, ?)",
        (emp_id, description, completed_on)
    )
    conn.commit()

# 🖥️ Streamlit Layout
st.set_page_config(page_title="Employee Productivity Tracker", page_icon="🧑‍💻", layout="wide")
st.title("🧑‍💻 Employee Productivity Tracker")

menu = st.sidebar.selectbox("📌 Choose Action", ["Add Employee", "Log Attendance", "Log Task", "Reports"])

if menu == "Add Employee":
    st.subheader("➕ Add New Employee")
    name = st.text_input("Employee Name")
    department = st.text_input("Department")
    if st.button("Add Employee"):
        if name.strip() and department.strip():
            add_employee(name, department)
            st.success(f"✅ Employee '{name}' added successfully!")
        else:
            st.warning("⚠️ Please fill in all fields.")

elif menu == "Log Attendance":
    st.subheader("🕒 Log Attendance")
    emp_id = st.number_input("Employee ID", min_value=1)
    check_in = st.text_input("Check-In Time (HH:MM)")
    check_out = st.text_input("Check-Out Time (HH:MM)")
    if st.button("Submit Attendance"):
        if check_in and check_out:
            log_attendance(emp_id, check_in, check_out)
            st.success("✅ Attendance recorded successfully!")
        else:
            st.warning("⚠️ Please enter both check-in and check-out times.")

elif menu == "Log Task":
    st.subheader("🧾 Log Task")
    emp_id = st.number_input("Employee ID", min_value=1)
    task = st.text_area("Task Description")
    if st.button("Submit Task"):
        if task.strip():
            log_task(emp_id, task)
            st.success("✅ Task logged successfully!")
        else:
            st.warning("⚠️ Please enter a task description.")

elif menu == "Reports":
    st.subheader("📊 Employee Productivity Reports")

    try:
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        df_att = pd.read_sql_query("SELECT * FROM attendance", conn)
        df_tasks = pd.read_sql_query("SELECT * FROM tasks", conn)

        col1, col2 = st.columns(2)
        with col1:
            st.write("📋 Employees")
            st.dataframe(df_emp)

        with col2:
            st.write("🕒 Recent Attendance Records")
            st.dataframe(df_att.tail(10))

        st.write("✅ Recent Tasks")
        st.dataframe(df_tasks.tail(10))

        # 📈 Task Summary Chart
        if not df_tasks.empty:
            merged = pd.merge(df_tasks, df_emp, on="emp_id", how="left")
            task_summary = merged.groupby("name").count()["task_description"]
            st.subheader("📈 Tasks Completed per Employee")
            st.bar_chart(task_summary)
        else:
            st.info("No tasks logged yet to display chart.")

    except Exception as e:
        st.error(f"⚠️ Error loading reports: {e}")

st.caption("© 2025 Employee Productivity Tracker | Built with Streamlit & SQLite")
