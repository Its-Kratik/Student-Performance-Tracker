"""
SQLite Database Connection Module
Handles database connection and initialization for SQLite
"""

import sqlite3
import streamlit as st
import os
import random
from typing import Optional, Any
from pathlib import Path
from datetime import date, timedelta

class DatabaseManager:
    """Database connection manager for SQLite"""

    def __init__(self):
        self.connection = None
        self.db_path = Path(__file__).parent.parent / "student_tracker.db"

    def get_connection(self):
        """Get database connection with optimizations"""
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0,
                isolation_level=None  # Autocommit mode
            )
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 1000")
            conn.execute("PRAGMA temp_store = MEMORY")
            return conn
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def connect(self) -> bool:
        """Establish database connection"""
        self.connection = self.get_connection()
        return self.connection is not None

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return False

    def fetch_all(self, query: str, params: tuple = None) -> list:
        """Fetch all results from SELECT query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            st.error(f"Query fetch failed: {e}")
            return []

    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        """Fetch single result from SELECT query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            st.error(f"Query fetch failed: {e}")
            return None

# Global database instance
@st.cache_resource
def get_db_connection():
    db = DatabaseManager()
    if db.connect():
        return db
    return None

# Query helper functions
def execute_query(query: str, params: tuple = None) -> bool:
    db = get_db_connection()
    return db.execute_query(query, params) if db else False

def fetch_all(query: str, params: tuple = None) -> list:
    db = get_db_connection()
    return db.fetch_all(query, params) if db else []

def fetch_one(query: str, params: tuple = None) -> Optional[tuple]:
    db = get_db_connection()
    return db.fetch_one(query, params) if db else None

# Initialization logic
def initialize_sample_data():
    try:
        existing_students = fetch_one("SELECT COUNT(*) FROM Student")
        if existing_students and existing_students[0] > 0:
            print("Sample data already exists")
            return True

        print("Inserting sample data...")

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

        sample_subjects = [
            ("Mathematics",), ("Physics",), ("Chemistry",),
            ("Biology",), ("English",), ("History",),
            ("Geography",), ("Computer Science",)
        ]

        for student in sample_students:
            execute_query("INSERT INTO Student (name, class, section, dob) VALUES (?, ?, ?, ?)", student)

        for subject in sample_subjects:
            execute_query("INSERT OR IGNORE INTO Subject (subject_name) VALUES (?)", subject)

        for student_id in range(1, len(sample_students) + 1):
            for subject_id in range(1, 6):  # 5 subjects per student
                marks_obtained = random.randint(45, 95)
                assessment_date = date.today() - timedelta(days=random.randint(1, 30))
                assessment_type = random.choice(['Quiz', 'Assignment', 'Midterm', 'Final'])
                execute_query(
                    """INSERT INTO Marks 
                    (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (student_id, subject_id, marks_obtained, 100, assessment_date, assessment_type)
                )

        print("Sample data inserted.")
        return True

    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

def init_database():
    db = get_db_connection()
    if not db:
        return False

    try:
        student_table_sql = """
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL 
                CHECK(length(trim(name)) >= 2),
            class TEXT NOT NULL 
                CHECK(class IN ('10', '11', '12')),
            section TEXT NOT NULL 
                CHECK(section IN ('A', 'B', 'C')),
            dob DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        subject_table_sql = """
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE
                CHECK(length(trim(subject_name)) >= 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        marks_table_sql = """
        CREATE TABLE IF NOT EXISTS Marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks_obtained INTEGER NOT NULL
                CHECK(marks_obtained >= 0),
            max_marks INTEGER DEFAULT 100
                CHECK(max_marks > 0),
            assessment_date DATE DEFAULT (date('now')),
            assessment_type TEXT DEFAULT 'Assignment'
                CHECK(assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final', 'Project')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
            CHECK(marks_obtained <= max_marks)
        )
        """

        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_student_class_section ON Student(class, section)",
            "CREATE INDEX IF NOT EXISTS idx_student_name ON Student(name)",
            "CREATE INDEX IF NOT EXISTS idx_marks_student_id ON Marks(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_marks_subject_id ON Marks(subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_marks_assessment_date ON Marks(assessment_date)",
            "CREATE INDEX IF NOT EXISTS idx_marks_student_subject ON Marks(student_id, subject_id)"
        ]

        for table_sql in [student_table_sql, subject_table_sql, marks_table_sql]:
            db.execute_query(table_sql)

        for index_sql in indexes_sql:
            db.execute_query(index_sql)

        initialize_sample_data()
        return True

    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def get_database_info():
    db = get_db_connection()
    if not db:
        return {}

    try:
        info = {
            "database_path": str(db.db_path),
            "database_exists": db.db_path.exists(),
            "database_size": db.db_path.stat().st_size if db.db_path.exists() else 0
        }

        for table in ["Student", "Subject", "Marks"]:
            result = db.fetch_one(f"SELECT COUNT(*) FROM {table}")
            info[f"{table.lower()}_count"] = result[0] if result else 0

        return info

    except Exception as e:
        st.error(f"Error getting database info: {e}")
        return {}

def debug_database():
    try:
        students = fetch_all("SELECT COUNT(*) FROM Student")
        subjects = fetch_all("SELECT COUNT(*) FROM Subject")
        marks = fetch_all("SELECT COUNT(*) FROM Marks")

        print(f"Students: {students[0][0] if students else 0}")
        print(f"Subjects: {subjects[0][0] if subjects else 0}")
        print(f"Marks: {marks[0][0] if marks else 0}")

        all_students = fetch_all("SELECT * FROM Student LIMIT 5")
        print("Sample students:" if all_students else "No students found", all_students)

    except Exception as e:
        print(f"Debug error: {e}")
