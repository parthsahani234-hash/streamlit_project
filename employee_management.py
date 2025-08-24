import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime

# Database configuration
db_config = {
    'host': 'localhost',
    'database': 'company',
    'user': 'root',  # Replace with your MySQL username
    'password': 'root'   # Replace with your MySQL password
}

def create_connection():
    """Create a database connection"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def create_table():
    """Create employees table if it doesn't exist"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                department VARCHAR(100),
                position VARCHAR(100),
                salary DECIMAL(10, 2),
                hire_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            st.error(f"Error creating table: {e}")

def insert_employee(name, email, department, position, salary, hire_date):
    """Insert a new employee into the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO employees (name, email, department, position, salary, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, email, department, position, salary, hire_date))
            conn.commit()
            st.success("Employee added successfully!")
            cursor.close()
            conn.close()
            return True
        except Error as e:
            st.error(f"Error inserting employee: {e}")
            return False

def fetch_all_employees():
    """Fetch all employees from the database"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees ORDER BY created_at DESC")
            employees = cursor.fetchall()
            cursor.close()
            conn.close()
            return employees
        except Error as e:
            st.error(f"Error fetching employees: {e}")
            return None

def search_employees(search_term):
    """Search employees by name, email, or department"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            search_query = """
            SELECT * FROM employees 
            WHERE name LIKE %s OR email LIKE %s OR department LIKE %s
            ORDER BY created_at DESC
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(search_query, (search_pattern, search_pattern, search_pattern))
            employees = cursor.fetchall()
            cursor.close()
            conn.close()
            return employees
        except Error as e:
            st.error(f"Error searching employees: {e}")
            return None

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Employee Management System",
        page_icon="👥",
        layout="wide"
    )
    
    # Create table if it doesn't exist
    create_table()
    
    # App title
    st.title("👥 Employee Management System")
    st.markdown("---")
    
    # Sidebar for navigation
    menu = ["Add Employee", "View Employees", "Search Employees"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Add Employee":
        st.header("Add New Employee")
        
        with st.form("employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                department = st.selectbox(
                    "Department",
                    ["IT", "HR", "Finance", "Marketing", "Operations", "Sales"]
                )
            
            with col2:
                position = st.text_input("Position")
                salary = st.number_input("Salary", min_value=0.0, step=500.0)
                hire_date = st.date_input("Hire Date")
            
            submitted = st.form_submit_button("Add Employee")
            
            if submitted:
                if name and email and department and position and salary and hire_date:
                    if insert_employee(name, email, department, position, salary, hire_date):
                        st.balloons()
                else:
                    st.warning("Please fill in all fields")
    
    elif choice == "View Employees":
        st.header("Employee Directory")
        
        employees = fetch_all_employees()
        if employees:
            # Convert to DataFrame for better display
            df = pd.DataFrame(employees, columns=[
                "ID", "Name", "Email", "Department", "Position", 
                "Salary", "Hire Date", "Created At"
            ])
            
            # Format the date columns
            df["Hire Date"] = pd.to_datetime(df["Hire Date"]).dt.date
            df["Created At"] = pd.to_datetime(df["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
            
            # Format salary
            df["Salary"] = df["Salary"].apply(lambda x: f"${x:,.2f}")
            
            # Display the table
            st.dataframe(df, use_container_width=True)
            
            # Show some statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Employees", len(df))
            with col2:
                st.metric("Departments", df["Department"].nunique())
            with col3:
                avg_salary = df["Salary"].replace('[\$,]', '', regex=True).astype(float).mean()
                st.metric("Average Salary", f"${avg_salary:,.2f}")
        else:
            st.info("No employees found in the database")
    
    elif choice == "Search Employees":
        st.header("Search Employees")
        
        search_term = st.text_input("Enter search term (name, email, or department)")
        
        if search_term:
            employees = search_employees(search_term)
            if employees:
                df = pd.DataFrame(employees, columns=[
                    "ID", "Name", "Email", "Department", "Position", 
                    "Salary", "Hire Date", "Created At"
                ])
                
                # Format the data
                df["Hire Date"] = pd.to_datetime(df["Hire Date"]).dt.date
                df["Created At"] = pd.to_datetime(df["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
                df["Salary"] = df["Salary"].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(df, use_container_width=True)
                st.success(f"Found {len(df)} employees matching '{search_term}'")
            else:
                st.warning(f"No employees found matching '{search_term}'")

if __name__ == "__main__":
    main()