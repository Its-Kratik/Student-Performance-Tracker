"""
Student Performance Tracker - Main Application
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
from db.db_init import initialize_database
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from utils.analytics import PerformanceAnalytics, display_analytics_metrics
from utils.ui_components import SessionStateManager, display_loading_spinner

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
    SessionStateManager.initialize_session_state()

    # Initialize database if needed
    if 'db_initialized' not in st.session_state:
        with st.spinner("Initializing database..."):
            try:
                if initialize_database():
                    st.session_state.db_initialized = True
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

    # Quick stats
    with st.spinner("Loading dashboard data..."):
        try:
            stats = PerformanceAnalytics.get_overall_statistics()
            display_analytics_metrics(stats)
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            # Fallback stats
            stats = {
                'total_students': 0,
                'total_subjects': 0,
                'total_assessments': 0,
                'overall_average': 0,
                'pass_rate': 0
            }

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
        st.markdown("#### Latest Students Added")
        try:
            recent_students = Student.get_all_students()[:5]  # Last 5 students
            if recent_students:
                for student in recent_students:
                    st.write(f"• {student[1]} - {student[2]}-{student[3]}")
            else:
                st.info("No students found")
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
                st.info("No subjects found")
        except Exception as e:
            st.warning("Could not load subjects")

    # Grade distribution preview
    st.markdown("---")
    st.subheader("📊 Grade Distribution Preview")

    try:
        grade_data = PerformanceAnalytics.get_grade_distribution()
        if grade_data['total_students'] > 0:
            # Create a simple grade distribution display
            grade_counts = grade_data['grade_counts']

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("A+ Students", grade_counts.get('A+', 0))
            with col2:
                st.metric("A Students", grade_counts.get('A', 0))
            with col3:
                st.metric("B+ Students", grade_counts.get('B+', 0))
            with col4:
                st.metric("Failing Students", grade_counts.get('F', 0))
        else:
            st.info("No grade data available yet")

    except Exception as e:
        st.info("Grade distribution will appear when marks are entered")

def display_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.title("🎓 Navigation")

        # Navigation menu
        pages = [
            {"name": "🏠 Dashboard", "file": "app.py"},
            {"name": "👥 Manage Students", "file": "pages/1_Manage_Students.py"},
            {"name": "📚 Manage Subjects", "file": "pages/2_Manage_Subjects.py"},
            {"name": "📝 Enter Marks", "file": "pages/3_Enter_Update_Marks.py"},
            {"name": "📋 Report Cards", "file": "pages/4_Student_Report_Card.py"},
            {"name": "📊 Class Analytics", "file": "pages/5_Class_Analytics.py"},
            {"name": "📈 Visual Reports", "file": "pages/6_Visual_Reports.py"},
            {"name": "⚙️ Settings", "file": "pages/7_Settings.py"}
        ]

        for page in pages:
            if st.button(page["name"], use_container_width=True):
                if page["file"] != "app.py":
                    st.switch_page(page["file"])

        st.markdown("---")

        # System status
        st.subheader("📊 System Status")

        try:
            # Check database connection
            students = Student.get_all_students()
            st.success("✅ Database Connected")

            # Display basic stats
            student_count = len(students) if students else 0
            subjects = Subject.get_all_subjects()
            subject_count = len(subjects) if subjects else 0

            st.metric("Students", student_count)
            st.metric("Subjects", subject_count)

        except Exception as e:
            st.error("❌ Database Connection Error")
            st.warning("Please check your database configuration")

        st.markdown("---")

        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Student Performance Tracker v1.0**

            A comprehensive academic performance management system built with:
            - Python 3.x
            - Streamlit
            - MySQL/SQLite
            - Pandas
            - Altair/Plotly

            Features:
            - Student & Subject Management
            - Marks Entry & Tracking
            - Performance Analytics
            - Report Generation
            - Data Export (PDF/CSV)
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
        <p>Student Performance Tracker | Built with ❤️ using Streamlit</p>
        <p>📧 Support: admin@studenttracker.com | 📞 Help: +1-234-567-8900</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
