"""
Student Model - CRUD operations for Student entity (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from db.connection import execute_query, fetch_all, fetch_one

class Student:
    def __init__(self, student_id=None, name=None, class_name=None, section=None, dob=None):
        self.student_id = student_id
        self.name = name
        self.class_name = class_name
        self.section = section
        self.dob = dob

    @staticmethod
    def add_student(name: str, class_name: str, section: str, dob: date) -> bool:
        """Add new student to database"""
        query = "INSERT INTO Student (name, class, section, dob) VALUES (?, ?, ?, ?)"
        return execute_query(query, (name, class_name, section, dob))

    @staticmethod
    def get_all_students() -> list:
        """Get all students from database"""
        query = """
        SELECT student_id, name, class, section, dob, created_at 
        FROM Student 
        ORDER BY class, section, name
        """
        return fetch_all(query)

    @staticmethod
    def get_student_by_id(student_id: int) -> tuple:
        """Get student by ID"""
        query = "SELECT student_id, name, class, section, dob FROM Student WHERE student_id = ?"
        return fetch_one(query, (student_id,))

    @staticmethod
    def search_students(search_term: str = "", class_filter: str = "", section_filter: str = "") -> list:
        """Search students with filters"""
        query = """
        SELECT student_id, name, class, section, dob, created_at 
        FROM Student 
        WHERE (name LIKE ? OR ? = '')
        AND (class = ? OR ? = '')
        AND (section = ? OR ? = '')
        ORDER BY class, section, name
        """
        search_pattern = f"%{search_term}%"
        return fetch_all(query, (search_pattern, search_term, class_filter, class_filter, 
                                section_filter, section_filter))

    @staticmethod
    def update_student(student_id: int, name: str, class_name: str, section: str, dob: date) -> bool:
        """Update existing student"""
        query = """
        UPDATE Student 
        SET name = ?, class = ?, section = ?, dob = ? 
        WHERE student_id = ?
        """
        return execute_query(query, (name, class_name, section, dob, student_id))

    @staticmethod
    def delete_student(student_id: int) -> bool:
        """Delete student and all associated marks"""
        query = "DELETE FROM Student WHERE student_id = ?"
        return execute_query(query, (student_id,))

    @staticmethod
    def get_students_by_class(class_name: str, section: str = None) -> list:
        """Get students by class and optionally by section"""
        if section:
            query = "SELECT student_id, name, class, section FROM Student WHERE class = ? AND section = ?"
            return fetch_all(query, (class_name, section))
        else:
            query = "SELECT student_id, name, class, section FROM Student WHERE class = ?"
            return fetch_all(query, (class_name,))

    @staticmethod
    def get_unique_classes() -> list:
        """Get list of unique classes"""
        query = "SELECT DISTINCT class FROM Student ORDER BY class"
        result = fetch_all(query)
        return [row[0] for row in result] if result else []

    @staticmethod
    def get_unique_sections() -> list:
        """Get list of unique sections"""
        query = "SELECT DISTINCT section FROM Student ORDER BY section"
        result = fetch_all(query)
        return [row[0] for row in result] if result else []

    @staticmethod
    def get_students_dataframe() -> pd.DataFrame:
        """Get students as pandas DataFrame"""
        students = Student.get_all_students()
        if students:
            df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
            df['DOB'] = pd.to_datetime(df['DOB']).dt.date
            df['Created'] = pd.to_datetime(df['Created']).dt.date
            return df
        return pd.DataFrame()

    @staticmethod
    def validate_student_data(name: str, class_name: str, section: str, dob: date) -> tuple:
        """Validate student data before insertion/update"""
        errors = []

        # Name validation
        if not name or len(name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        elif len(name) > 100:
            errors.append("Name cannot exceed 100 characters")

        # Class validation
        if not class_name or not class_name.strip():
            errors.append("Class is required")
        elif len(class_name) > 10:
            errors.append("Class name cannot exceed 10 characters")

        # Section validation
        if not section or not section.strip():
            errors.append("Section is required")
        elif len(section) > 5:
            errors.append("Section cannot exceed 5 characters")

        # DOB validation
        if not dob:
            errors.append("Date of birth is required")
        elif dob >= date.today():
            errors.append("Date of birth must be in the past")
        elif dob < date(1900, 1, 1):
            errors.append("Invalid date of birth")

        return len(errors) == 0, errors

def display_students_table(students_data: list, show_actions: bool = True) -> None:
    """Display students in a formatted table"""
    if not students_data:
        st.info("No students found")
        return

    df = pd.DataFrame(students_data, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])

    # Format dates
    df['DOB'] = pd.to_datetime(df['DOB']).dt.strftime('%Y-%m-%d')
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d')

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("Student ID", width="small"),
            "Name": st.column_config.TextColumn("Full Name", width="medium"),
            "Class": st.column_config.TextColumn("Class", width="small"),
            "Section": st.column_config.TextColumn("Section", width="small"),
            "DOB": st.column_config.DateColumn("Date of Birth", width="medium"),
            "Created": st.column_config.DateColumn("Created On", width="medium")
        }
    )

    st.info(f"Total students: {len(students_data)}")

def student_form(student_data=None, form_type="Add"):
    """Reusable student form for add/edit operations"""

    # Initialize default values
    default_name = student_data[1] if student_data else ""
    default_class = student_data[2] if student_data else ""
    default_section = student_data[3] if student_data else ""
    default_dob = student_data[4] if student_data else date.today().replace(year=date.today().year - 10)

    with st.form(f"student_{form_type.lower()}_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *", value=default_name, max_chars=100)
            class_name = st.text_input("Class *", value=default_class, max_chars=10)

        with col2:
            section = st.text_input("Section *", value=default_section, max_chars=5)
            dob = st.date_input("Date of Birth *", value=default_dob, max_value=date.today())

        submitted = st.form_submit_button(f"{form_type} Student", type="primary")

        if submitted:
            # Validate input
            is_valid, errors = Student.validate_student_data(name, class_name, section, dob)

            if is_valid:
                if form_type == "Add":
                    success = Student.add_student(name, class_name, section, dob)
                    if success:
                        st.success(f"✅ Student '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add student")

                elif form_type == "Update" and student_data:
                    success = Student.update_student(student_data[0], name, class_name, section, dob)
                    if success:
                        st.success(f"✅ Student '{name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update student")
            else:
                for error in errors:
                    st.error(f"❌ {error}")
