"""
Database Initialization Module
Creates tables and sample data
"""
import streamlit as st
from db.mysql_connection import execute_query, fetch_one

def create_tables():
    """Create all necessary database tables"""

    # Create Student table
    student_table_query = """
    CREATE TABLE IF NOT EXISTS Student (
        student_id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        class VARCHAR(10) NOT NULL,
        section VARCHAR(5) NOT NULL,
        dob DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_class_section (class, section)
    )
    """

    # Create Subject table
    subject_table_query = """
    CREATE TABLE IF NOT EXISTS Subject (
        subject_id INT PRIMARY KEY AUTO_INCREMENT,
        subject_name VARCHAR(50) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    # Create Marks table
    marks_table_query = """
    CREATE TABLE IF NOT EXISTS Marks (
        mark_id INT PRIMARY KEY AUTO_INCREMENT,
        student_id INT,
        subject_id INT,
        marks_obtained INT,
        max_marks INT DEFAULT 100,
        assessment_date DATE,
        assessment_type ENUM('Quiz', 'Assignment', 'Midterm', 'Final') DEFAULT 'Assignment',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
        CHECK (marks_obtained >= 0 AND max_marks > 0 AND marks_obtained <= max_marks),
        INDEX idx_student_subject (student_id, subject_id),
        INDEX idx_assessment_date (assessment_date)
    )
    """

    tables = [
        ("Student", student_table_query),
        ("Subject", subject_table_query), 
        ("Marks", marks_table_query)
    ]

    success_count = 0
    for table_name, query in tables:
        if execute_query(query):
            st.success(f"✅ {table_name} table created successfully")
            success_count += 1
        else:
            st.error(f"❌ Failed to create {table_name} table")

    return success_count == len(tables)

def insert_sample_data():
    """Insert sample data for demonstration"""

    # Check if data already exists
    existing_students = fetch_one("SELECT COUNT(*) FROM Student")
    if existing_students and existing_students[0] > 0:
        st.info("Sample data already exists")
        return True

    # Sample students
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
    student_query = "INSERT INTO Student (name, class, section, dob) VALUES (%s, %s, %s, %s)"
    students_inserted = 0
    for student in sample_students:
        if execute_query(student_query, student):
            students_inserted += 1

    # Insert subjects  
    subject_query = "INSERT INTO Subject (subject_name) VALUES (%s)"
    subjects_inserted = 0
    for subject in sample_subjects:
        if execute_query(subject_query, subject):
            subjects_inserted += 1

    # Insert sample marks
    import random
    from datetime import date, timedelta

    marks_inserted = 0
    for student_id in range(1, students_inserted + 1):
        for subject_id in range(1, min(6, subjects_inserted + 1)):  # First 5 subjects
            marks_obtained = random.randint(45, 95)  # Random marks between 45-95
            assessment_date = date.today() - timedelta(days=random.randint(1, 30))
            assessment_type = random.choice(['Quiz', 'Assignment', 'Midterm', 'Final'])

            marks_query = """
            INSERT INTO Marks (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            if execute_query(marks_query, (student_id, subject_id, marks_obtained, 100, assessment_date, assessment_type)):
                marks_inserted += 1

    st.success(f"✅ Sample data inserted: {students_inserted} students, {subjects_inserted} subjects, {marks_inserted} marks")
    return True

def initialize_database():
    """Initialize complete database with tables and sample data"""
    st.info("🔄 Initializing database...")

    # Create tables
    if create_tables():
        st.success("📋 All tables created successfully")

        # Insert sample data
        if insert_sample_data():
            st.success("🎯 Database initialization completed!")
            return True

    st.error("❌ Database initialization failed")
    return False

# SQLite fallback table creation (simplified)
def create_sqlite_tables():
    """Create tables for SQLite fallback"""
    import sqlite3

    try:
        conn = sqlite3.connect('student_tracker.db')
        cursor = conn.cursor()

        # Student table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            section TEXT NOT NULL,
            dob DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Subject table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Marks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            marks_obtained INTEGER,
            max_marks INTEGER DEFAULT 100,
            assessment_date DATE,
            assessment_type TEXT DEFAULT 'Assignment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
        )
        """)

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        st.error(f"SQLite table creation failed: {e}")
        return False
