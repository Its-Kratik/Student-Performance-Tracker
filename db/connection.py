"""
SQLite Database Connection Module
Handles database connection and initialization for SQLite
"""
import sqlite3
import streamlit as st
import os
from typing import Optional, Any
from pathlib import Path

class DatabaseManager:
    """Database connection manager for SQLite"""

    def __init__(self):
        self.connection = None
        # Use a database file in the project directory
        self.db_path = Path(__file__).parent.parent / "student_tracker.db"

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path), 
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign key support
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.commit()
            return True
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
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
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
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
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            st.error(f"Query fetch failed: {e}")
            return None

# Global database instance
@st.cache_resource
def get_db_connection():
    """Get cached database connection"""
    db = DatabaseManager()
    if db.connect():
        return db
    return None

# Helper functions
def execute_query(query: str, params: tuple = None) -> bool:
    """Execute query using global connection"""
    db = get_db_connection()
    if db:
        return db.execute_query(query, params)
    return False

def fetch_all(query: str, params: tuple = None) -> list:
    """Fetch all results using global connection"""
    db = get_db_connection()
    if db:
        return db.fetch_all(query, params)
    return []

def fetch_one(query: str, params: tuple = None) -> Optional[tuple]:
    """Fetch one result using global connection"""
    db = get_db_connection()
    if db:
        return db.fetch_one(query, params)
    return None

def init_database():
    """Initialize database with tables if they don't exist"""
    db = get_db_connection()
    if not db:
        return False

    try:
        # Create Student table
        student_table_sql = """
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            section TEXT NOT NULL,
            dob DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Create Subject table
        subject_table_sql = """
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Create Marks table
        marks_table_sql = """
        CREATE TABLE IF NOT EXISTS Marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            marks_obtained INTEGER,
            max_marks INTEGER DEFAULT 100,
            assessment_date DATE,
            assessment_type TEXT DEFAULT 'Assignment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
            CHECK (marks_obtained >= 0 AND marks_obtained <= max_marks)
        )
        """

        # Create indexes for better performance
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_student_class_section ON Student(class, section)",
            "CREATE INDEX IF NOT EXISTS idx_marks_student_subject ON Marks(student_id, subject_id)",
            "CREATE INDEX IF NOT EXISTS idx_marks_assessment_date ON Marks(assessment_date)"
        ]

        # Execute table creation
        for table_sql in [student_table_sql, subject_table_sql, marks_table_sql]:
            db.execute_query(table_sql)

        # Create indexes
        for index_sql in indexes_sql:
            db.execute_query(index_sql)

        return True

    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def get_database_info():
    """Get database information and statistics"""
    db = get_db_connection()
    if not db:
        return {}

    try:
        info = {
            "database_path": str(db.db_path),
            "database_exists": db.db_path.exists(),
            "database_size": 0
        }

        if db.db_path.exists():
            info["database_size"] = db.db_path.stat().st_size

        # Get table counts
        tables = ["Student", "Subject", "Marks"]
        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table}"
            result = db.fetch_one(count_query)
            info[f"{table.lower()}_count"] = result[0] if result else 0

        return info

    except Exception as e:
        st.error(f"Error getting database info: {e}")
        return {}
