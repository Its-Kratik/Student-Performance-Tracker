"""
Database Initialization Module
Creates tables and sample data for SQLite
"""
import streamlit as st
import sqlite3
import random
from datetime import date, timedelta
from db.connection import get_db_connection, execute_query, fetch_one

def insert_sample_data():
    """Insert sample data for demonstration"""
    # Check if data already exists
    existing_students = fetch_one("SELECT COUNT(*) FROM Student")
    if existing_students and existing_students[0] > 0:
        st.info("Sample data already exists")
        return True

    # Sample students (SQLite compatible)
    sample_students = [
        ("Aarav Sharma", "10", "A", "2008-05-20"),
        ("Priya Patel", "10", "A", "2008-03-15"),
        ("Rohit Kumar", "10", "B", "2008-07-10"),
        ("Sneha Singh", "10", "B", "2008-01-25"),
        ("Vikram Rao", "11", "A", "2007-11-05"),
        ("Anita Desai", "11", "A", "2007-09-30"),
        ("Kiran Reddy", "11", "B", "2007-12-18"),
        ("Meera Joshi", "12", "A", "2006-08-22"),
        ("Arjun Nair", "12", "A", "2006-04-14"),
        ("Deepika Gupta", "12", "B", "2006-06-08")
    ]

    # Sample subjects
    sample_subjects = [
        ("Mathematics",),
        ("Physics",),
        ("Chemistry",),
        ("Biology",),
        ("English",),
        ("History",),
        ("Geography",),
        ("Computer Science",)
    ]

    # Insert students
    student_query = "INSERT INTO Student (name, class, section, dob) VALUES (?, ?, ?, ?)"
    students_inserted = 0
    for student in sample_students:
        if execute_query(student_query, student):
            students_inserted += 1

    # Insert subjects
    subject_query = "INSERT INTO Subject (subject_name) VALUES (?)"
    subjects_inserted = 0
    for subject in sample_subjects:
        if execute_query(subject_query, subject):
            subjects_inserted += 1

    # Insert sample marks
    marks_inserted = 0
    for student_id in range(1, students_inserted + 1):
        for subject_id in range(1, min(6, subjects_inserted + 1)):
            marks_obtained = random.randint(45, 95)
            assessment_date = date.today() - timedelta(days=random.randint(1, 30))
            assessment_type = random.choice(['Quiz', 'Assignment', 'Midterm', 'Final'])
            
            marks_query = """
            INSERT INTO Marks (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            if execute_query(marks_query, (student_id, subject_id, marks_obtained, 100, assessment_date, assessment_type)):
                marks_inserted += 1

    st.success(f"✅ Sample data inserted: {students_inserted} students, {subjects_inserted} subjects, {marks_inserted} marks")
    return True

def initialize_database():
    """Initialize complete database with tables and sample data"""
    from db.connection import init_database
    
    st.info("🔄 Initializing database...")
    
    # Create tables using connection.py
    if init_database():
        st.success("📋 All tables created successfully")
        
        # Insert sample data
        if insert_sample_data():
            st.success("🎯 Database initialization completed!")
            return True
    
    st.error("❌ Database initialization failed")
    return False
