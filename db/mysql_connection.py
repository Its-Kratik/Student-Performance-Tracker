"""
MySQL Database Connection Module
Handles database connection and initialization
"""
import mysql.connector
from mysql.connector import Error
import streamlit as st
import os
from typing import Optional, Any

class DatabaseManager:
    """Database connection manager for MySQL"""

    def __init__(self):
        self.connection = None
        self.host = st.secrets.get("mysql", {}).get("host", "localhost")
        self.database = st.secrets.get("mysql", {}).get("database", "student_tracker")
        self.user = st.secrets.get("mysql", {}).get("user", "root")
        self.password = st.secrets.get("mysql", {}).get("password", "")
        self.port = st.secrets.get("mysql", {}).get("port", 3306)

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                autocommit=True
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            st.error(f"Database connection failed: {e}")
            # Fallback to SQLite for demo purposes
            try:
                import sqlite3
                self.connection = sqlite3.connect('student_tracker.db')
                st.warning("Using SQLite as fallback database")
                return True
            except Exception as sqlite_error:
                st.error(f"SQLite fallback also failed: {sqlite_error}")
        return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cursor.close()
            return True
        except Error as e:
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
        except Error as e:
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
        except Error as e:
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
