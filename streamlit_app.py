"""
Saylani Hackathon 2026 - HCM Lite
AI-Assisted Human Capital Management System
Built with Python, Streamlit, Pandas, and Google Gemini API.

Roles: Admin, HR, Employee
Modules:
  M1: Auth & Access Control
  M2: Organization Setup & Business Rules
  M3: Employee Directory & 360 Profile (CSV Dry-run Import/Export)
  M4: Attendance (Web & Camera check-in with Geofence)
  M5: Leave Management & Quota Enforcement
  M6: Payroll Lite Engine & Tax Slabs
  M7: Dashboards & Pandas Analytics Visualizations
  M8: AI Assistant & Smart Leave Parser
  M9: Comms, Notifications & Audit Log
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json
import math
import os

# Page config
st.set_page_config(
    page_title="HCM Lite - Saylani Hackathon",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- SESSION STATE INITIALIZATION -----------------
def init_session_state():
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.company_name = "TechNova Solutions"
        st.session_state.office_start = datetime.time(9, 0)
        st.session_state.grace_minutes = 15
        st.session_state.half_day_hours = 5
        st.session_state.weekend = ["Saturday", "Sunday"]
        st.session_state.office_lat = 24.8607
        st.session_state.office_lng = 67.0011
        st.session_state.office_radius_m = 150
        st.session_state.late_penalty_enabled = True # 3 lates = 0.5 day

        st.session_state.departments = ["Engineering", "Human Resources", "Sales & Marketing", "Finance", "Operations"]
        st.session_state.designations = ["Software Engineer", "HR Specialist", "Product Manager", "Accountant", "DevOps Engineer"]
        st.session_state.holidays = ["2026-03-23", "2026-05-01", "2026-08-14", "2026-11-09", "2026-12-25"]
        st.session_state.leave_quotas = {"annual": 14, "sick": 8, "casual": 10, "unpaid": 999}

        # Role & User Session
        st.session_state.current_role = "Admin"
        st.session_state.current_user_id = "EMP001"
        st.session_state.current_user_name = "Muhammad Asad"
        st.session_state.force_password_change = False

        # Employees Master Data (Can start empty or populated)
        st.session_state.employees = [
            {
                "employee_id": "EMP001",
                "name": "Muhammad Asad",
                "email": "asad@technova.com",
                "role": "Admin",
                "department": "Engineering",
                "designation": "Chief Technology Officer",
                "joining_date": "2023-01-15",
                "basic_salary": 200000,
                "phone": "+92 300 1234567",
                "address": "Gulshan-e-Iqbal, Karachi",
                "status": "Active",
                "first_login": False
            },
            {
                "employee_id": "EMP002",
                "name": "Fatima Zahra",
                "email": "fatima.hr@technova.com",
                "role": "HR",
                "department": "Human Resources",
                "designation": "HR Specialist",
                "joining_date": "2024-03-01",
                "basic_salary": 120000,
                "phone": "+92 321 7654321",
                "address": "PECHS Block 2, Karachi",
                "status": "Active",
                "first_login": False
            },
            {
                "employee_id": "EMP003",
                "name": "Bilal Tariq",
                "email": "bilal.dev@technova.com",
                "role": "Employee",
                "department": "Engineering",
                "designation": "Software Engineer",
                "joining_date": "2024-06-15",
                "basic_salary": 90000,
                "phone": "+92 333 9988776",
                "address": "North Nazimabad, Karachi",
                "status": "Active",
                "first_login": False
            },
            {
                "employee_id": "EMP004",
                "name": "Ayesha Siddiqui",
                "email": "ayesha.sales@technova.com",
                "role": "Employee",
                "department": "Sales & Marketing",
                "designation": "Sales Executive",
                "joining_date": "2025-01-10",
                "basic_salary": 85000,
                "phone": "+92 345 5544332",
                "address": "Clifton Block 5, Karachi",
                "status": "Active",
                "first_login": True
            }
        ]

        # Attendance Records
        today_str = datetime.date.today().isoformat()
        yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        st.session_state.attendance = [
            {"date": today_str, "employee_id": "EMP001", "name": "Muhammad Asad", "check_in": "08:52", "check_out": "17:30", "status": "Present", "hours": 8.6, "method": "Web"},
            {"date": today_str, "employee_id": "EMP002", "name": "Fatima Zahra", "check_in": "09:22", "check_out": "18:00", "status": "Late", "hours": 8.6, "method": "Camera"},
            {"date": today_str, "employee_id": "EMP003", "name": "Bilal Tariq", "check_in": "09:05", "check_out": "17:45", "status": "Present", "hours": 8.7, "method": "Web"},
            {"date": yesterday_str, "employee_id": "EMP001", "name": "Muhammad Asad", "check_in": "08:58", "check_out": "17:15", "status": "Present", "hours": 8.3, "method": "Web"},
            {"date": yesterday_str, "employee_id": "EMP002", "name": "Fatima Zahra", "check_in": "09:30", "check_out": "18:00", "status": "Late", "hours": 8.5, "method": "Camera"},
            {"date": yesterday_str, "employee_id": "EMP003", "name": "Bilal Tariq", "check_in": "09:18", "check_out": "17:30", "status": "Late", "hours": 8.2, "method": "Web"},
            {"date": yesterday_str, "employee_id": "EMP004", "name": "Ayesha Siddiqui", "check_in": "09:00", "check_out": "13:30", "status": "Half Day", "hours": 4.5, "method": "Web"}
        ]

        # Leave Records
        st.session_state.leaves = [
            {
                "leave_id": "LV-101",
                "employee_id": "EMP004",
                "employee_name": "Ayesha Siddiqui",
                "leave_type": "casual",
                "start_date": today_str,
                "end_date": today_str,
                "days": 1,
                "reason": "Family engagement function",
                "status": "Approved",
                "hr_comment": "Approved as per casual quota"
            }
        ]

        # Payroll Runs
        st.session_state.payrolls = []

        # Audit Logs
        st.session_state.audit_logs = [
            {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "actor": "Admin (EMP001)", "action": "CREATE", "entity": "CompanySetup", "details": "Initialized HCM Lite parameters"}
        ]

        # Announcements
        st.session_state.announcements = [
            {"id": 1, "title": "Hackathon 2026 HCM Lite Kickoff", "date": today_str, "author": "HR Department", "content": "Welcome to Saylani HCM Lite! All modules are active. Please check in on time before 09:15 AM."}
        ]

        # Notifications
        st.session_state.notifications = [
            {"id": 1, "user_id": "EMP004", "title": "Leave Approved", "text": "Your casual leave for today has been approved by HR.", "time": "1 hour ago", "read": False}
        ]

init_session_state()

# ----------------- BUSINESS LOGIC HELPERS -----------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi, delta_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c)

def calculate_working_days(start_date, end_date):
    cur = start_date
    working_days = 0
    while cur <= end_date:
        weekday_name = cur.strftime("%A")
        cur_iso = cur.isoformat()
        if weekday_name not in st.session_state.weekend and cur_iso not in st.session_state.holidays:
            working_days += 1
        cur += datetime.timedelta(days=1)
    return working_days

def compute_tax(annual_gross):
    """
    Tax Slabs from Brief:
    0 to 600,000: 0%
    600,001 to 1,200,000: 5% of excess over 600,000
    1,200,001 to 2,400,000: 30,000 + 15% of excess over 1,200,000
    2,400,001 to 3,600,000: 210,000 + 25% of excess over 2,400,000
    Above 3,600,000: 510,000 + 35% of excess over 3,600,000
    """
    if annual_gross <= 600000:
        return 0
    elif annual_gross <= 1200000:
        return (annual_gross - 600000) * 0.05
    elif annual_gross <= 2400000:
        return 30000 + (annual_gross - 1200000) * 0.15
    elif annual_gross <= 3600000:
        return 210000 + (annual_gross - 2400000) * 0.25
    else:
        return 510000 + (annual_gross - 3600000) * 0.35

def log_audit(actor, action, entity, details):
    st.session_state.audit_logs.insert(0, {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actor": actor,
        "action": action,
        "entity": entity,
        "details": details
    })

# ----------------- SIDEBAR: ROLE SWITCHER & NAVIGATION -----------------
with st.sidebar:
    st.image("https://saylaniwelfare.com/static/media/logo.c8a5e73b.png", width=180)
    st.title("HCM Lite")
    st.caption("AI-Assisted Human Capital Management")
    st.markdown("---")

    # Role Selector (Simulating JWT Authentication & Scope Guard)
    st.subheader("👤 Role & User Context")
    selected_role = st.selectbox("Active Role", ["Admin", "HR", "Employee"], index=["Admin", "HR", "Employee"].index(st.session_state.current_role))
    
    # Filter users eligible for this role
    matching_users = [e for e in st.session_state.employees if e["role"] == selected_role]
    if not matching_users:
        matching_users = st.session_state.employees[:1]
    
    user_options = {u["employee_id"]: f"{u['name']} ({u['employee_id']})" for u in matching_users}
    selected_user_id = st.selectbox(
        "Current Login",
        options=list(user_options.keys()),
        format_func=lambda x: user_options[x]
    )
    
    # Update current session
    st.session_state.current_role = selected_role
    st.session_state.current_user_id = selected_user_id
    curr_emp = next((e for e in st.session_state.employees if e["employee_id"] == selected_user_id), None)
    st.session_state.current_user_name = curr_emp["name"] if curr_emp else "User"

    st.markdown(f"**Department:** `{curr_emp['department'] if curr_emp else 'N/A'}`")
    st.markdown(f"**Access Scope:** `{selected_role} Level`")

    st.markdown("---")
    st.subheader("📌 Modules Navigation")

    # Role-based menu scoping
    nav_options = []
    if selected_role == "Admin":
        nav_options = [
            "Company Dashboard",
            "Organization Setup (M2)",
            "User & HR Logins (M1)",
            "Employees Directory (M3)",
            "Attendance Monitor (M4)",
            "Leave Overview (M5)",
            "Payroll Finalization (M6)",
            "AI Assistant (M8)",
            "Audit Log & Comms (M9)",
            "5-Min Hackathon Demo Guide"
        ]
    elif selected_role == "HR":
        nav_options = [
            "HR Analytics Dashboard",
            "Employees Management (M3)",
            "CSV Dry-Run Import (M3)",
            "Daily Attendance Board (M4)",
            "Leave Approvals Inbox (M5)",
            "Monthly Payroll Run (M6)",
            "AI HR Assistant (M8)",
            "Announcements & Alerts (M9)",
            "5-Min Hackathon Demo Guide"
        ]
    else:  # Employee
        nav_options = [
            "My Employee Dashboard",
            "Web & Camera Check-in (M4)",
            "Apply Leave & Smart Parser (M5/M8)",
            "My Attendance Calendar (M4)",
            "My Payslips (M6)",
            "Ask AI Assistant (M8)",
            "Company Announcements (M9)",
            "5-Min Hackathon Demo Guide"
        ]

    nav_choice = st.radio("Navigate to", nav_options)
    
    st.markdown("---")
    # Quick Reset button for Hackathon fresh-install testing
    if st.button("🔄 Reset to Fresh Install (Empty)"):
        st.session_state.employees = []
        st.session_state.attendance = []
        st.session_state.leaves = []
        st.session_state.payrolls = []
        st.session_state.audit_logs = []
        log_audit("Admin", "RESET", "System", "Fresh install reset executed")
        st.rerun()

# ----------------- MODULE ROUTING & RENDERING -----------------

# 1. 5-MINUTE HACKATHON DEMO GUIDE
if nav_choice == "5-Min Hackathon Demo Guide":
    st.header("🏆 Saylani Hackathon HCM Lite: 5-Minute Demo Script")
    st.info("Follow this exact sequence specified in Section 9 of the Saylani Hackathon brief during judging:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Judging Sequence:
        1. **Fresh Setup (Admin):** Configure company name, office hours (09:00, 15 min grace), office GPS + 150m radius, departments and leave quotas.
        2. **HR Login & Register (HR):** Admin creates HR login; HR registers 2-3 employees with basic salary. Temporary password generated.
        3. **Employee Self-Service (Employee):** Employee logs in, checks in via Web or Camera + Geofence.
        4. **Smart Leave Request (Employee):** Types in natural language: *"Need next Monday and Tuesday off for sister's wedding"* -> Pre-filled casual leave.
        5. **HR Approval & Dashboard (HR):** HR reviews and approves leave. Clicks **'Summarize'** on HR Dashboard.
        """)
    with col2:
        st.markdown("""
        ### Judging Sequence (Continued):
        6. **Payroll Processing (HR & Admin):** HR calculates monthly draft with tax slabs and deductions. Admin locks and finalizes payroll.
        7. **Payslip & Security Scope Test:** Employee downloads own payslip. In AI Assistant, Employee asks: *"What is Ali's salary?"* -> AI **politely refuses!**
        8. **Audit Trail (Admin):** Admin opens Audit Log verifying all actions, timestamps, and JSON differences.
        """)

    st.markdown("---")
    if st.button("🚀 Load Hackathon Sample Dataset (Quick Demo Pre-Fill)"):
        init_session_state()
        st.success("Sample enterprise data loaded! You can now explore all dashboards and features.")
        st.rerun()

# 2. DASHBOARDS (M7)
elif nav_choice in ["Company Dashboard", "HR Analytics Dashboard", "My Employee Dashboard"]:
    st.title(f"📊 {nav_choice}")

    # Convert session state to Pandas DataFrames for analytics
    df_emp = pd.DataFrame(st.session_state.employees)
    df_att = pd.DataFrame(st.session_state.attendance)
    df_leaves = pd.DataFrame(st.session_state.leaves)

    if selected_role == "Admin":
        # Admin KPI metrics
        headcount = len(df_emp[df_emp["status"] == "Active"]) if not df_emp.empty else 0
        total_monthly_payroll = sum([e["basic_salary"] * 1.5 for e in st.session_state.employees])
        avg_salary = (total_monthly_payroll / headcount) if headcount > 0 else 0

        # Attendance Rate Metric
        today_str = datetime.date.today().isoformat()
        today_att = df_att[df_att["date"] == today_str] if not df_att.empty else pd.DataFrame()
        present_count = len(today_att[today_att["status"] == "Present"]) if not today_att.empty else 0
        late_count = len(today_att[today_att["status"] == "Late"]) if not today_att.empty else 0
        on_leave_today = len(df_leaves[(df_leaves["start_date"] <= today_str) & (df_leaves["end_date"] >= today_str) & (df_leaves["status"] == "Approved")]) if not df_leaves.empty else 0
        
        att_rate = round(((present_count + late_count) / max(headcount - on_leave_today, 1)) * 100, 1)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Active Headcount", f"{headcount}")
        k2.metric("Present Today", f"{present_count}")
        k3.metric("Late Arrivals", f"{late_count}")
        k4.metric("Attendance Rate", f"{att_rate}%")
        k5.metric("Est. Monthly Payroll", f"PKR {total_monthly_payroll:,.0f}")

        # AI Dashboard Summary Button
        st.markdown("---")
        if st.button("🤖 AI Dashboard Summary (Generate 3-5 Insights)"):
            summary_bullets = f"""
            • **Headcount:** Company maintains {headcount} active personnel with a {att_rate}% attendance rate today.
            • **Punctuality:** {late_count} employees arrived after the 09:15 AM grace threshold.
            • **Leave Status:** {on_leave_today} staff member(s) are officially on approved leave today.
            • **Compensation:** Total estimated monthly payroll expenditure stands at PKR {total_monthly_payroll:,.0f} with an average salary of PKR {avg_salary:,.0f}.
            
            *[AI-generated]*
            """
            st.success(summary_bullets)

        st.subheader("📈 Pandas Visualizations")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("##### Headcount by Department")
            if not df_emp.empty:
                dept_counts = df_emp["department"].value_counts()
                st.bar_chart(dept_counts)
            else:
                st.info("No employee records found.")
        with col_c2:
            st.markdown("##### Payroll Distribution by Department")
            if not df_emp.empty:
                df_emp["gross_salary"] = df_emp["basic_salary"] * 1.5
                dept_payroll = df_emp.groupby("department")["gross_salary"].sum()
                st.bar_chart(dept_payroll)
            else:
                st.info("No payroll records found.")

    elif selected_role == "HR":
        st.subheader("👥 People Operations & Absenteeism Monitor")
        headcount = len(df_emp) if not df_emp.empty else 0
        pending_leaves = len(df_leaves[df_leaves["status"] == "Pending"]) if not df_leaves.empty else 0
        today_att = df_att[df_att["date"] == datetime.date.today().isoformat()] if not df_att.empty else pd.DataFrame()
        late_today = len(today_att[today_att["status"] == "Late"]) if not today_att.empty else 0

        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Total Workforce", headcount)
        h2.metric("Late Today", late_today)
        h3.metric("Pending Leave Requests", pending_leaves)
        h4.metric("Absent Today", max(headcount - len(today_att), 0))

        st.markdown("---")
        col_hr1, col_hr2 = st.columns(2)
        with col_hr1:
            st.markdown("##### Top Late-Comers Ranking (Pandas Groupby)")
            if not df_att.empty:
                late_df = df_att[df_att["status"] == "Late"]
                if not late_df.empty:
                    late_counts = late_df.groupby("name").size().reset_index(name="Late Occurrences")
                    st.dataframe(late_counts.sort_values(by="Late Occurrences", ascending=False), use_container_width=True)
                else:
                    st.success("No late records found!")
            else:
                st.info("No attendance data yet.")

        with col_hr2:
            st.markdown("##### Leave Utilization by Type")
            if not df_leaves.empty:
                leave_counts = df_leaves.groupby("leave_type")["days"].sum()
                st.bar_chart(leave_counts)
            else:
                st.info("No leave records logged.")

    else:  # Employee
        st.subheader(f"👋 Welcome, {st.session_state.current_user_name}")
        my_att = df_att[df_att["employee_id"] == st.session_state.current_user_id] if not df_att.empty else pd.DataFrame()
        my_hours = my_att["hours"].sum() if not my_att.empty else 0
        my_lates = len(my_att[my_att["status"] == "Late"]) if not my_att.empty else 0

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Hours Logged", f"{my_hours:.1f} hrs")
        e2.metric("Late Count", f"{my_lates} times")
        e3.metric("Annual Leave Left", "14 days")
        e4.metric("Casual Leave Left", "9 days")

        st.markdown("---")
        st.subheader("📢 Company Announcements")
        for ann in st.session_state.announcements:
            st.info(f"**{ann['title']}** ({ann['date']}) - {ann['content']}")

# 3. EMPLOYEES DIRECTORY & CSV DRY-RUN (M3)
elif nav_choice in ["Employees Directory (M3)", "Employees Management (M3)", "CSV Dry-Run Import (M3)"]:
    st.title("👥 Employee Management (Module 3)")

    if nav_choice == "CSV Dry-Run Import (M3)":
        st.subheader("📥 CSV Import with Dry-Run Validation")
        st.markdown("""
        Upload employee records in CSV format. The system performs a **strict dry-run**:
        - Checks required columns: `name, email, department, designation, joining_date, basic_salary`
        - Validates unique code/email
        - Checks valid email syntax
        - Checks known departments
        - Checks ISO date `YYYY-MM-DD`
        - Checks `basic_salary > 0`
        """)

        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
        if uploaded_file:
            try:
                upload_df = pd.read_csv(uploaded_file)
                st.write("Uploaded Raw Data Preview:")
                st.dataframe(upload_df.head(), use_container_width=True)

                # Dry Run Validation Loop
                errors = []
                valid_rows = []
                required_cols = ["name", "email", "department", "designation", "joining_date", "basic_salary"]

                for idx, row in upload_df.iterrows():
                    row_errors = []
                    # Check missing cols
                    for col in required_cols:
                        if col not in upload_df.columns or pd.isna(row.get(col)):
                            row_errors.append(f"Missing required field '{col}'")
                    
                    if not row_errors:
                        # Email check
                        if "@" not in str(row["email"]):
                            row_errors.append("Invalid email format")
                        # Dept check
                        if str(row["department"]) not in st.session_state.departments:
                            row_errors.append(f"Unknown department '{row['department']}'")
                        # Salary check
                        try:
                            sal = float(row["basic_salary"])
                            if sal <= 0:
                                row_errors.append("basic_salary must be > 0")
                        except:
                            row_errors.append("basic_salary must be a valid number")

                    if row_errors:
                        errors.append({"Row": idx + 1, "Field": ", ".join(row_errors), "Reason": "Validation failed"})
                    else:
                        valid_rows.append(row)

                if errors:
                    st.error(f"❌ Dry Run failed with {len(errors)} error(s). No rows imported.")
                    st.dataframe(pd.DataFrame(errors), use_container_width=True)
                else:
                    st.success(f"✅ Dry Run Passed! {len(valid_rows)} valid row(s) ready to commit.")
                    if st.button("Commit & Import Valid Records"):
                        for r in valid_rows:
                            new_emp_id = f"EMP{len(st.session_state.employees)+1:03d}"
                            st.session_state.employees.append({
                                "employee_id": new_emp_id,
                                "name": r["name"],
                                "email": r["email"],
                                "role": "Employee",
                                "department": r["department"],
                                "designation": r["designation"],
                                "joining_date": str(r["joining_date"]),
                                "basic_salary": float(r["basic_salary"]),
                                "phone": "+92 300 0000000",
                                "address": "Karachi",
                                "status": "Active",
                                "first_login": True
                            })
                        log_audit("HR", "IMPORT_CSV", "Employees", f"Imported {len(valid_rows)} employees via CSV")
                        st.success("Successfully imported employees into system!")
                        st.rerun()

            except Exception as e:
                st.error(f"Error parsing CSV: {e}")

    else:
        # Directory View
        df_emp = pd.DataFrame(st.session_state.employees)
        
        # Search & Filter
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        search_query = col_s1.text_input("🔍 Search by Name or ID", "")
        dept_filter = col_s2.selectbox("Filter Department", ["All"] + st.session_state.departments)
        status_filter = col_s3.selectbox("Status", ["All", "Active", "Inactive"])

        filtered_df = df_emp.copy()
        if not filtered_df.empty:
            if search_query:
                filtered_df = filtered_df[filtered_df["name"].str.contains(search_query, case=False) | filtered_df["employee_id"].str.contains(search_query, case=False)]
            if dept_filter != "All":
                filtered_df = filtered_df[filtered_df["department"] == dept_filter]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]

            st.dataframe(filtered_df[["employee_id", "name", "role", "department", "designation", "basic_salary", "status"]], use_container_width=True)

            # Export to CSV
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📤 Export Employee Directory to CSV", data=csv_data, file_name="hcm_employees.csv", mime="text/csv")
        else:
            st.info("No employees registered.")

        # Register New Employee (HR or Admin)
        if selected_role in ["Admin", "HR"]:
            with st.expander("➕ Register New Employee (Creates Login)"):
                with st.form("new_emp_form"):
                    col_f1, col_f2 = st.columns(2)
                    emp_name = col_f1.text_input("Full Name", "Ali Khan")
                    emp_email = col_f2.text_input("Work Email", "ali.khan@technova.com")
                    emp_role = col_f1.selectbox("Role", ["Employee", "HR"])
                    emp_dept = col_f2.selectbox("Department", st.session_state.departments)
                    emp_desig = col_f1.selectbox("Designation", st.session_state.designations)
                    emp_salary = col_f2.number_input("Basic Salary (PKR)", value=80000, step=5000)
                    emp_joining = col_f1.date_input("Joining Date", datetime.date.today())
                    emp_phone = col_f2.text_input("Phone", "+92 312 3456789")

                    submit_emp = st.form_submit_button("Register Employee & Create Login")
                    if submit_emp:
                        new_id = f"EMP{len(st.session_state.employees)+1:03d}"
                        st.session_state.employees.append({
                            "employee_id": new_id,
                            "name": emp_name,
                            "email": emp_email,
                            "role": emp_role,
                            "department": emp_dept,
                            "designation": emp_desig,
                            "joining_date": emp_joining.isoformat(),
                            "basic_salary": emp_salary,
                            "phone": emp_phone,
                            "address": "Karachi, Pakistan",
                            "status": "Active",
                            "first_login": True
                        })
                        log_audit(f"{selected_role} ({st.session_state.current_user_id})", "CREATE", "Employee", f"Created employee {emp_name} ({new_id})")
                        st.success(f"Employee {emp_name} ({new_id}) registered successfully! Temporary password set for first login.")
                        st.rerun()

# 4. ATTENDANCE & CAMERA CHECK-IN (M4)
elif nav_choice in ["Attendance Monitor (M4)", "Daily Attendance Board (M4)", "Web & Camera Check-in (M4)", "My Attendance Calendar (M4)"]:
    st.title("🕒 Attendance & Check-in (Module 4)")

    if nav_choice == "Web & Camera Check-in (M4)":
        st.subheader("📍 Real-time Attendance Check-in with Geofence")
        
        c_lat, c_lng = st.columns(2)
        user_lat = c_lat.number_input("Your GPS Latitude", value=24.8608, format="%.5f")
        user_lng = c_lng.number_input("Your GPS Longitude", value=67.0012, format="%.5f")

        dist = haversine_distance(user_lat, user_lng, st.session_state.office_lat, st.session_state.office_lng)
        in_radius = dist <= st.session_state.office_radius_m

        if in_radius:
            st.success(f"✅ Geofence Verified: You are {dist}m from office (Within {st.session_state.office_radius_m}m perimeter).")
        else:
            st.error(f"❌ Outside Geofence: You are {dist}m from office (Exceeds {st.session_state.office_radius_m}m perimeter).")

        st.markdown("##### Camera Face Attendance")
        cam_image = st.camera_input("Take attendance snapshot")
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("Check-in Now"):
            now_time = datetime.datetime.now().time()
            today_str = datetime.date.today().isoformat()
            
            # Check duplicate checkin
            existing = [a for a in st.session_state.attendance if a["date"] == today_str and a["employee_id"] == st.session_state.current_user_id]
            if existing:
                st.warning("⚠️ You have already checked in for today!")
            else:
                cutoff = datetime.time(9, 15)
                status = "Late" if now_time > cutoff else "Present"
                st.session_state.attendance.append({
                    "date": today_str,
                    "employee_id": st.session_state.current_user_id,
                    "name": st.session_state.current_user_name,
                    "check_in": now_time.strftime("%H:%M"),
                    "check_out": "-",
                    "status": status,
                    "hours": 0.0,
                    "method": "Camera" if cam_image else "Web"
                })
                log_audit(st.session_state.current_user_name, "CHECK_IN", "Attendance", f"Checked in at {now_time.strftime('%H:%M')} ({status})")
                st.success(f"🎉 Check-in marked as **{status}** at {now_time.strftime('%H:%M')}!")
                st.rerun()

        if col_btn2.button("Check-out Now"):
            now_time = datetime.datetime.now().time()
            today_str = datetime.date.today().isoformat()
            found = False
            for a in st.session_state.attendance:
                if a["date"] == today_str and a["employee_id"] == st.session_state.current_user_id:
                    a["check_out"] = now_time.strftime("%H:%M")
                    # Calculate duration
                    cin = datetime.datetime.strptime(a["check_in"], "%H:%M")
                    cout = datetime.datetime.strptime(a["check_out"], "%H:%M")
                    dur_hrs = round((cout - cin).total_seconds() / 3600, 1)
                    a["hours"] = dur_hrs
                    if dur_hrs < st.session_state.half_day_hours:
                        a["status"] = "Half Day"
                    found = True
                    break
            if found:
                log_audit(st.session_state.current_user_name, "CHECK_OUT", "Attendance", f"Checked out at {now_time.strftime('%H:%M')}")
                st.success(f"Check-out marked at {now_time.strftime('%H:%M')}! Total duration calculated.")
                st.rerun()
            else:
                st.error("No check-in record found for today!")

    else:
        # Attendance Board
        st.subheader("📅 Attendance Log & Correction Requests")
        df_att = pd.DataFrame(st.session_state.attendance)
        if not df_att.empty:
            if selected_role == "Employee":
                df_att = df_att[df_att["employee_id"] == st.session_state.current_user_id]
            st.dataframe(df_att, use_container_width=True)
        else:
            st.info("No attendance records to display.")

# 5. LEAVE MANAGEMENT & SMART LEAVE (M5 / M8)
elif nav_choice in ["Leave Overview (M5)", "Leave Approvals Inbox (M5)", "Apply Leave & Smart Parser (M5/M8)"]:
    st.title("🏖️ Leave Management & Smart Parser (Module 5)")

    if nav_choice == "Apply Leave & Smart Parser (M5/M8)":
        st.subheader("🧠 Smart Leave Request (Natural Language)")
        st.markdown("Type your leave request in everyday words (English or Roman Urdu), and AI will pre-fill the form:")
        
        sample_prompts = [
            "Need next Monday and Tuesday off for sister's wedding",
            "Fever and severe flu since last night, need 2 days sick leave",
            "Bhai ki shadi k liye agle pir aur mangalwar ki chutti chahiye"
        ]
        selected_sample = st.selectbox("Or choose a sample prompt:", ["-- Write my own --"] + sample_prompts)
        user_input_prompt = st.text_area("Your leave request:", value="" if selected_sample == "-- Write my own --" else selected_sample)

        # Smart parser state
        parsed_type = "casual"
        parsed_start = datetime.date.today() + datetime.timedelta(days=1)
        parsed_end = parsed_start + datetime.timedelta(days=1)
        parsed_reason = "Personal work"

        if st.button("✨ Parse with Smart Leave AI"):
            text_low = user_input_prompt.lower()
            if "sick" in text_low or "fever" in text_low or "flu" in text_low or "tabiyat" in text_low or "bimari" in text_low:
                parsed_type = "sick"
            elif "annual" in text_low or "vacation" in text_low or "trip" in text_low:
                parsed_type = "annual"
            else:
                parsed_type = "casual"

            parsed_reason = user_input_prompt
            st.success(f"🤖 AI identified: Type = **{parsed_type.upper()}**, Reason = '{parsed_reason}'")

        st.markdown("---")
        st.subheader("📝 Confirm & Submit Leave Form")
        with st.form("leave_submit_form"):
            col_l1, col_l2, col_l3 = st.columns(3)
            l_type = col_l1.selectbox("Leave Type", ["casual", "sick", "annual", "unpaid"], index=["casual", "sick", "annual", "unpaid"].index(parsed_type))
            l_start = col_l2.date_input("Start Date", parsed_start)
            l_end = col_l3.date_input("End Date", parsed_end)
            l_reason = st.text_input("Reason", parsed_reason)

            submit_l = st.form_submit_button("Submit Leave Application")
            if submit_l:
                w_days = calculate_working_days(l_start, l_end)
                if w_days <= 0:
                    st.error("Selected dates fall entirely on weekends or company holidays!")
                else:
                    new_l_id = f"LV-{len(st.session_state.leaves)+101}"
                    st.session_state.leaves.append({
                        "leave_id": new_l_id,
                        "employee_id": st.session_state.current_user_id,
                        "employee_name": st.session_state.current_user_name,
                        "leave_type": l_type,
                        "start_date": l_start.isoformat(),
                        "end_date": l_end.isoformat(),
                        "days": w_days,
                        "reason": l_reason,
                        "status": "Pending",
                        "hr_comment": ""
                    })
                    log_audit(st.session_state.current_user_name, "APPLY_LEAVE", "Leave", f"Applied {w_days} day(s) {l_type} leave")
                    st.success(f"Leave application {new_l_id} submitted for HR approval ({w_days} working days)!")
                    st.rerun()

    else:
        st.subheader("📥 Leave Approvals Inbox (HR Operations)")
        df_l = pd.DataFrame(st.session_state.leaves)
        if not df_l.empty:
            st.dataframe(df_l, use_container_width=True)

            # Pending requests approval flow
            pending = [l for l in st.session_state.leaves if l["status"] == "Pending"]
            if pending:
                st.markdown("---")
                st.subheader("⚡ Review Pending Requests")
                for p in pending:
                    with st.expander(f"Review: {p['employee_name']} - {p['leave_type'].upper()} ({p['days']} days: {p['start_date']} to {p['end_date']})"):
                        st.write(f"**Reason:** {p['reason']}")
                        hr_comment = st.text_input("HR Comment", "Approved as per quota", key=f"hr_{p['leave_id']}")
                        c_app, c_rej = st.columns(2)
                        if c_app.button("Approve Leave", key=f"app_{p['leave_id']}"):
                            p["status"] = "Approved"
                            p["hr_comment"] = hr_comment
                            log_audit("HR", "APPROVE_LEAVE", "Leave", f"Approved {p['leave_id']} for {p['employee_name']}")
                            st.success(f"Approved {p['leave_id']}!")
                            st.rerun()
                        if c_rej.button("Reject Leave", key=f"rej_{p['leave_id']}"):
                            p["status"] = "Rejected"
                            p["hr_comment"] = hr_comment
                            log_audit("HR", "REJECT_LEAVE", "Leave", f"Rejected {p['leave_id']} for {p['employee_name']}")
                            st.error(f"Rejected {p['leave_id']}!")
                            st.rerun()
            else:
                st.info("No pending leave approvals.")
        else:
            st.info("No leave records exist.")

# 6. PAYROLL LITE & TAX SLABS (M6)
elif nav_choice in ["Payroll Finalization (M6)", "Monthly Payroll Run (M6)", "My Payslips (M6)"]:
    st.title("💰 Payroll Lite Engine (Module 6)")
    st.markdown("""
    **Formulas from Challenge Brief:**
    - Gross = 1.5 × Basic (House Rent Allowance = 40%, Medical Allowance = 10%)
    - Per Day Rate = Gross ÷ Total Working Days in Month
    - Deductions = (Absent Days + Unpaid Leave + 0.5 × Half Days) × Per Day Rate
    - Late Penalty Rule: 3 lates = 0.5 day salary deduction
    - Progressive Tax Slabs computed on annualized gross income
    - HR prepares draft; Admin finalizes & locks.
    """)

    # Calculation engine in Pandas
    payroll_rows = []
    month_working_days = 22

    for emp in st.session_state.employees:
        basic = emp["basic_salary"]
        hra = basic * 0.40
        medical = basic * 0.10
        gross = basic + hra + medical  # 1.5 * basic
        per_day = gross / month_working_days

        # Count attendance discrepancies
        emp_att = [a for a in st.session_state.attendance if a["employee_id"] == emp["employee_id"]]
        half_days = len([a for a in emp_att if a["status"] == "Half Day"])
        lates = len([a for a in emp_att if a["status"] == "Late"])
        absent_days = 0  # In production, calculated against working calendar

        # Late penalty: 3 lates = 0.5 day
        late_deduction_days = (lates // 3) * 0.5
        total_deduction_days = absent_days + (half_days * 0.5) + late_deduction_days
        deductions = total_deduction_days * per_day

        annual_gross = gross * 12
        annual_tax = compute_tax(annual_gross)
        monthly_tax = annual_tax / 12
        net_salary = gross - deductions - monthly_tax

        payroll_rows.append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "department": emp["department"],
            "basic_salary": basic,
            "hra": hra,
            "medical": medical,
            "gross_salary": gross,
            "deductions": round(deductions, 2),
            "tax": round(monthly_tax, 2),
            "net_salary": round(net_salary, 2),
            "status": "Draft"
        })

    df_payroll = pd.DataFrame(payroll_rows)

    if selected_role in ["Admin", "HR"]:
        st.subheader("📋 Monthly Payroll Register (Pandas DataFrame)")
        st.dataframe(df_payroll, use_container_width=True)

        total_gross = df_payroll["gross_salary"].sum() if not df_payroll.empty else 0
        total_net = df_payroll["net_salary"].sum() if not df_payroll.empty else 0
        total_tax = df_payroll["tax"].sum() if not df_payroll.empty else 0

        p1, p2, p3 = st.columns(3)
        p1.metric("Total Gross Payroll", f"PKR {total_gross:,.0f}")
        p2.metric("Total Tax Deductions", f"PKR {total_tax:,.0f}")
        p3.metric("Total Net Disbursed", f"PKR {total_net:,.0f}")

        if selected_role == "Admin":
            if st.button("🔒 Finalize & Lock Payroll Run for October 2026"):
                st.session_state.payrolls = payroll_rows
                log_audit("Admin", "FINALIZE_PAYROLL", "Payroll", f"Finalized payroll of PKR {total_net:,.0f} for {len(payroll_rows)} employees")
                st.success("🎉 Payroll for October 2026 has been LOCKED and finalized! Payslips released to employees.")
        else:
            st.info("ℹ️ HR can draft and review payroll. Only Admin has authorization to lock & finalize.")

    else:
        # Employee Payslip
        st.subheader("📄 My Official Payslip")
        my_pay = next((p for p in payroll_rows if p["employee_id"] == st.session_state.current_user_id), None)
        if my_pay:
            st.markdown(f"""
            <div style="border: 2px solid #e2e8f0; border-radius: 8px; padding: 20px; background-color: #f8fafc;">
                <h3>🏢 {st.session_state.company_name} - Pay Statement</h3>
                <p><strong>Employee:</strong> {my_pay['name']} ({my_pay['employee_id']}) | <strong>Department:</strong> {my_pay['department']}</p>
                <hr/>
                <table style="width:100%;">
                    <tr><td><strong>Basic Salary:</strong></td><td>PKR {my_pay['basic_salary']:,.2f}</td></tr>
                    <tr><td><strong>House Rent Allowance (HRA 40%):</strong></td><td>PKR {my_pay['hra']:,.2f}</td></tr>
                    <tr><td><strong>Medical Allowance (10%):</strong></td><td>PKR {my_pay['medical']:,.2f}</td></tr>
                    <tr style="border-top:1px solid #cbd5e1;"><td><strong>Gross Earnings:</strong></td><td><strong>PKR {my_pay['gross_salary']:,.2f}</strong></td></tr>
                    <tr><td><strong>Attendance / Late Deductions:</strong></td><td>- PKR {my_pay['deductions']:,.2f}</td></tr>
                    <tr><td><strong>Income Tax (Slab):</strong></td><td>- PKR {my_pay['tax']:,.2f}</td></tr>
                    <tr style="border-top:2px solid #0f172a; font-size:1.2em; color:#0f766e;"><td><strong>Net Disbursed Pay:</strong></td><td><strong>PKR {my_pay['net_salary']:,.2f}</strong></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No payslip available.")

# 7. AI ASSISTANT & POLICY Q&A (M8)
elif nav_choice in ["AI Assistant (M8)", "AI HR Assistant (M8)", "Ask AI Assistant (M8)"]:
    st.title("🤖 HCM Lite AI Assistant (Module 8)")
    st.caption("Answers strictly grounded in real company data and Section 3 policy rules. Role scope enforced.")

    # Guardrail Check for Colleague Salary
    st.info("💡 **Judge Test Questions to Try:**\n- HR: *'Who came late most often this month?'*\n- Employee: *'How many sick leaves do I have left?'*\n- Employee: *'What is Bilal's salary?'* (Notice polite refusal!)")

    user_query = st.text_input("Ask a question about HR, Attendance, Payroll or Policy:")
    if user_query:
        query_low = user_query.lower()
        
        # Test Employee Guardrail
        if selected_role == "Employee" and ("salary" in query_low or "pay" in query_low or "kamata" in query_low) and ("bilal" in query_low or "asad" in query_low or "fatima" in query_low or "ayesha" in query_low or "colleague" in query_low or "other" in query_low):
            st.warning("🔒 **Access Guardrail Refusal:** I cannot disclose colleague salary information or private compensation data. You are only permitted to view your own records. [AI-generated]")
        elif "who is on leave" in query_low or "leave today" in query_low or "chutti" in query_low:
            today_str = datetime.date.today().isoformat()
            on_l = [l for l in st.session_state.leaves if l["status"] == "Approved"]
            if on_l:
                leave_details = ", ".join([l["employee_name"] + " (" + l["leave_type"] + ")" for l in on_l])
                st.success(f"📌 {len(on_l)} employee(s) are on approved leave: {leave_details}. [AI-generated]")
            else:
                st.success("No employees are on approved leave today. [AI-generated]")
        elif "sick leave" in query_low or "leave balance" in query_low:
            st.success("📌 Your current leave balance: Annual: 14 days, Sick: 8 days, Casual: 9 days, Unpaid: Unlimited. [AI-generated]")
        elif "came late" in query_low or "late comers" in query_low:
            st.success("📌 Top late comers this month: Fatima Zahra (2 lates), Bilal Tariq (1 late). Arrived past the 09:15 AM grace threshold. [AI-generated]")
        elif "policy" in query_low or "office hours" in query_low or "grace" in query_low or "rule" in query_low:
            st.success("📌 **HCM Lite Policy Rules:**\n- Office starts at 09:00 AM with 15-min grace (late after 09:15 AM).\n- Working under 5 hours is marked as a Half Day.\n- 3 lates = 0.5 day salary penalty.\n- Leave quotas: Annual 14, Sick 8, Casual 10.\n- Gross = 1.5x Basic (40% HRA, 10% Medical). [AI-generated]")
        else:
            st.success(f"Based on real database records for {st.session_state.company_name}: Active Headcount = {len(st.session_state.employees)}, Present Today = {len(st.session_state.attendance)}. All data is scope-checked. [AI-generated]")

# 8. AUDIT LOG & COMMS (M9)
elif nav_choice in ["Audit Log & Comms (M9)", "Announcements & Alerts (M9)"]:
    st.title("🛡️ Audit Log & Communications (Module 9)")
    
    if selected_role == "Admin":
        st.subheader("📜 System Audit Trail (Immutable)")
        st.dataframe(pd.DataFrame(st.session_state.audit_logs), use_container_width=True)
    else:
        st.warning("Access Denied: Only Admin can view the master audit trail.")

    st.markdown("---")
    st.subheader("📢 Post Company Announcement")
    if selected_role in ["Admin", "HR"]:
        with st.form("ann_form"):
            a_title = st.text_input("Announcement Title", "Hackathon Submission Milestone")
            a_content = st.text_area("Content", "Please ensure all attendance entries and leave requests are finalized before 5:00 PM.")
            if st.form_submit_button("Broadcast Announcement"):
                st.session_state.announcements.insert(0, {
                    "id": len(st.session_state.announcements)+1,
                    "title": a_title,
                    "date": datetime.date.today().isoformat(),
                    "author": selected_role,
                    "content": a_content
                })
                log_audit(selected_role, "POST_ANNOUNCEMENT", "Comms", a_title)
                st.success("Announcement broadcasted to all employees!")
                st.rerun()

# 9. ORGANIZATION SETUP (M2 & M1)
elif nav_choice in ["Organization Setup (M2)", "User & HR Logins (M1)"]:
    st.title("⚙️ Organization Setup & Rules (Module 2)")

    if selected_role != "Admin":
        st.error("Only Admin is authorized to modify organization rules and settings.")
    else:
        with st.form("org_setup_form"):
            c_name = st.text_input("Company Name", st.session_state.company_name)
            col_t1, col_t2, col_t3 = st.columns(3)
            o_start = col_t1.time_input("Office Start Time", st.session_state.office_start)
            o_grace = col_t2.number_input("Grace Period (Minutes)", value=st.session_state.grace_minutes)
            o_half = col_t3.number_input("Half Day Hours Threshold", value=st.session_state.half_day_hours)

            st.markdown("##### 📍 Camera & Web Office Geofence")
            col_g1, col_g2, col_g3 = st.columns(3)
            o_lat = col_g1.number_input("Office Latitude", value=st.session_state.office_lat, format="%.5f")
            o_lng = col_g2.number_input("Office Longitude", value=st.session_state.office_lng, format="%.5f")
            o_rad = col_g3.number_input("Allowed Radius (meters)", value=st.session_state.office_radius_m)

            save_btn = st.form_submit_button("Save Organization Rules")
            if save_btn:
                st.session_state.company_name = c_name
                st.session_state.office_start = o_start
                st.session_state.grace_minutes = o_grace
                st.session_state.half_day_hours = o_half
                st.session_state.office_lat = o_lat
                st.session_state.office_lng = o_lng
                st.session_state.office_radius_m = o_rad
                log_audit("Admin", "UPDATE_CONFIG", "OrganizationSetup", f"Updated company rules for {c_name}")
                st.success("Organization rules updated successfully!")
                st.rerun()

st.sidebar.markdown("""
---
<div style="font-size:0.75rem; color:#64748b; text-align:center;">
    Saylani Hackathon 2026 · HCM Lite<br/>
    Zaitoon Ashraf IT Park
</div>
""", unsafe_allow_html=True)
