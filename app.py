"""
Student Performance Tracker - Main Application (SQLite Version)
Streamlit-based academic performance management system
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
# In app.py - Use this import
from db.connection import get_db_connection, init_database

# Initialize database
try:
    if get_db_connection():
        if init_database():
            st.success("✅ Database ready!")
        else:
            st.error("❌ Database initialization failed")
except Exception as e:
    st.error(f"Database error: {e}")
from db.connection import get_database_info
from models.student import Student
from models.subject import Subject
from models.marks import Marks

# Page configuration
st.set_page_config(
    page_title="Student Performance Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        color: #155724;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize the application"""

    # Initialize database if needed
    if 'db_initialized' not in st.session_state:
        with st.spinner("Initializing SQLite database..."):
            try:
                if initialize_database():
                    st.session_state.db_initialized = True
                    st.success("✅ Database initialized successfully!")
                else:
                    st.error("Failed to initialize database")
                    return False
            except Exception as e:
                st.error(f"Database initialization error: {str(e)}")
                return False

    return True

def display_dashboard():
    """Display the main dashboard"""
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Performance Tracker</h1>', unsafe_allow_html=True)
    st.markdown("### Welcome to your comprehensive academic performance management system")
    st.info("📋 **SQLite Version** - Ready to use without external database setup!")

    # Quick stats
    with st.spinner("Loading dashboard data..."):
        try:
            # Get basic statistics
            students = Student.get_all_students()
            subjects = Subject.get_all_subjects()
            marks = Marks.get_all_marks()

            # Calculate overall statistics
            student_count = len(students) if students else 0
            subject_count = len(subjects) if subjects else 0
            marks_count = len(marks) if marks else 0

            # Calculate overall pass rate
            if marks:
                passing_marks = sum(1 for mark in marks 
                                  if Marks.calculate_percentage(mark[3], mark[4]) >= 40)
                pass_rate = (passing_marks / marks_count * 100) if marks_count > 0 else 0
            else:
                pass_rate = 0

            # Calculate overall average
            if marks:
                total_obtained = sum(mark[3] for mark in marks)
                total_possible = sum(mark[4] for mark in marks)
                overall_avg = (total_obtained / total_possible * 100) if total_possible > 0 else 0
            else:
                overall_avg = 0

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Students", student_count)

            with col2:
                st.metric("Total Subjects", subject_count)

            with col3:
                st.metric("Total Assessments", marks_count)

            with col4:
                st.metric("Overall Average", f"{overall_avg:.1f}%")

        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            # Fallback stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", 0)
            with col2:
                st.metric("Total Subjects", 0)
            with col3:
                st.metric("Total Assessments", 0)
            with col4:
                st.metric("Overall Average", "0%")

    st.markdown("---")

    # Quick actions
    st.subheader("🚀 Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("👥 Manage Students", use_container_width=True):
            st.switch_page("pages/1_Manage_Students.py")

    with col2:
        if st.button("📚 Manage Subjects", use_container_width=True):
            st.switch_page("pages/2_Manage_Subjects.py")

    with col3:
        if st.button("📝 Enter Marks", use_container_width=True):
            st.switch_page("pages/3_Enter_Update_Marks.py")

    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/5_Class_Analytics.py")

    st.markdown("---")

    # Recent activity section
    st.subheader("📈 Recent Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Latest Students")
        try:
            recent_students = Student.get_all_students()[:5]  # First 5 students
            if recent_students:
                for student in recent_students:
                    st.write(f"• {student[1]} - Class {student[2]}-{student[3]}")
            else:
                st.info("No students found - start by adding some students!")
        except Exception as e:
            st.warning("Could not load recent students")

    with col2:
        st.markdown("#### Available Subjects")
        try:
            subjects = Subject.get_all_subjects()[:5]  # First 5 subjects
            if subjects:
                for subject in subjects:
                    st.write(f"• {subject[1]}")
            else:
                st.info("No subjects found - add subjects to get started!")
        except Exception as e:
            st.warning("Could not load subjects")

    # Grade distribution preview
    st.markdown("---")
    st.subheader("📊 System Overview")

    try:
        marks = Marks.get_all_marks()
        if marks:
            # Calculate grade distribution
            grade_counts = {}
            for mark in marks:
                percentage = Marks.calculate_percentage(mark[3], mark[4])
                grade = Marks.calculate_grade(percentage)
                grade_counts[grade] = grade_counts.get(grade, 0) + 1

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                a_count = grade_counts.get('A+', 0) + grade_counts.get('A', 0)
                st.metric("A Grades", a_count)
            with col2:
                b_count = grade_counts.get('B+', 0) + grade_counts.get('B', 0)
                st.metric("B Grades", b_count)
            with col3:
                c_count = grade_counts.get('C+', 0) + grade_counts.get('C', 0)
                st.metric("C Grades", c_count)
            with col4:
                f_count = grade_counts.get('F', 0)
                st.metric("Failing Grades", f_count)
        else:
            st.info("📝 No marks data available yet. Enter some assessments to see grade distribution!")

    except Exception as e:
        st.info("Grade distribution will appear when marks are entered")

def display_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.title("🎓 Student Tracker")
        st.caption("SQLite Edition")

        # Navigation menu
        st.subheader("📋 Navigation")

        if st.button("🏠 Dashboard", use_container_width=True):
            st.rerun()

        if st.button("👥 Students", use_container_width=True):
            st.switch_page("pages/1_Manage_Students.py")

        if st.button("📚 Subjects", use_container_width=True):
            st.switch_page("pages/2_Manage_Subjects.py")

        if st.button("📝 Enter Marks", use_container_width=True):
            st.switch_page("pages/3_Enter_Update_Marks.py")

        if st.button("📋 Report Cards", use_container_width=True):
            st.switch_page("pages/4_Student_Report_Card.py")

        if st.button("📊 Analytics", use_container_width=True):
            st.switch_page("pages/5_Class_Analytics.py")

        st.markdown("---")

        # Database status
        st.subheader("📊 Database Status")

        try:
            # Get database info
            db_info = get_database_info()

            if db_info.get('database_exists'):
                st.success("✅ SQLite Database Connected")

                # Display basic stats
                st.metric("Students", db_info.get('student_count', 0))
                st.metric("Subjects", db_info.get('subject_count', 0))
                st.metric("Assessments", db_info.get('marks_count', 0))

                # Database file size
                db_size = db_info.get('database_size', 0)
                if db_size > 0:
                    size_mb = db_size / (1024 * 1024)
                    st.caption(f"Database size: {size_mb:.2f} MB")
            else:
                st.warning("⚠️ Database file not found")

        except Exception as e:
            st.error("❌ Database Connection Error")
            st.caption("Database will be created automatically")

        st.markdown("---")

        # Quick help
        with st.expander("ℹ️ Quick Help"):
            st.markdown("""
            **Getting Started:**
            1. Add students in "Students" section
            2. Add subjects in "Subjects" section  
            3. Enter marks in "Enter Marks"
            4. View reports and analytics

            **Features:**
            - No external database required
            - Automatic grade calculation
            - Performance analytics
            - Export capabilities

            **SQLite Benefits:**
            - Zero configuration
            - Portable database file
            - Fast and reliable
            - Perfect for single-user scenarios
            """)

def main():
    """Main application function"""
    # Initialize the application
    if not initialize_app():
        st.stop()

    # Display sidebar
    display_sidebar()

    # Display main dashboard
    display_dashboard()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🎓 <strong>Student Performance Tracker</strong> | SQLite Edition</p>
        <p>Built with ❤️ using Streamlit & SQLite</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
