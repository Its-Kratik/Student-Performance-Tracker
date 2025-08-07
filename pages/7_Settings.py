"""
Settings Page - Application configuration and preferences (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ Correct SQLite imports
from db.connection import get_db_connection, init_database, get_database_info, initialize_sample_data
from models.student import Student
from models.subject import Subject
from models.marks import Marks

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Application Settings")
st.markdown("Configure application preferences and manage system data")

# Sidebar for settings categories
with st.sidebar:
    st.subheader("Settings Categories")

    settings_category = st.radio(
        "Choose Category:",
        [
            "Database Management",
            "Data Import/Export", 
            "System Information",
            "Application Preferences",
            "Backup & Restore"
        ]
    )

# Main content area
if settings_category == "Database Management":
    st.subheader("🗄️ Database Management")

    # Database status
    st.markdown("### Database Status")

    try:
        # Test database connection
        db_info = get_database_info()
        test_students = Student.get_all_students()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Database connection is working")
            st.info(f"**Database:** SQLite")
            st.info(f"**Location:** {db_info.get('database_path', 'Unknown')}")
            
        with col2:
            db_size_mb = db_info.get('database_size', 0) / (1024 * 1024) if db_info.get('database_size', 0) > 0 else 0
            st.metric("Database Size", f"{db_size_mb:.2f} MB")

        # Display basic statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            student_count = db_info.get('student_count', 0)
            st.metric("Total Students", student_count)

        with col2:
            subject_count = db_info.get('subject_count', 0)
            st.metric("Total Subjects", subject_count)

        with col3:
            marks_count = db_info.get('marks_count', 0)
            st.metric("Total Marks", marks_count)

    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")

    st.markdown("---")

    # Database operations
    st.markdown("### Database Operations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Reinitialize Database")
        st.warning("⚠️ This will recreate all tables and add sample data")

        if st.button("🔄 Reinitialize Database"):
            with st.spinner("Reinitializing database..."):
                try:
                    if init_database():
                        st.success("✅ Database reinitialized successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to reinitialize database")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col2:
        st.markdown("#### Add Sample Data")
        st.info("Add sample students, subjects, and marks if database is empty")

        if st.button("📝 Add Sample Data"):
            with st.spinner("Adding sample data..."):
                try:
                    if initialize_sample_data():
                        st.success("✅ Sample data added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add sample data")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    # Data cleanup
    st.markdown("### Data Cleanup")

    with st.expander("⚠️ Danger Zone - Data Deletion"):
        st.error("**WARNING**: These operations cannot be undone!")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear All Marks", type="secondary"):
                if st.checkbox("I confirm deletion of all marks", key="clear_marks"):
                    try:
                        from db.connection import execute_query
                        if execute_query("DELETE FROM Marks"):
                            st.success("✅ All marks deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete marks")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col2:
            if st.button("🗑️ Clear All Students", type="secondary"):
                if st.checkbox("I confirm deletion of all students", key="clear_students"):
                    try:
                        from db.connection import execute_query
                        # Delete in order due to foreign key constraints
                        execute_query("DELETE FROM Marks")
                        if execute_query("DELETE FROM Student"):
                            st.success("✅ All students deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete students")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col3:
            if st.button("🗑️ Clear All Subjects", type="secondary"):
                if st.checkbox("I confirm deletion of all subjects", key="clear_subjects"):
                    try:
                        from db.connection import execute_query
                        # Delete in order due to foreign key constraints
                        execute_query("DELETE FROM Marks")
                        if execute_query("DELETE FROM Subject"):
                            st.success("✅ All subjects deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete subjects")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

elif settings_category == "Data Import/Export":
    st.subheader("📤📥 Data Import/Export")

    # Export section
    st.markdown("### 📤 Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Export Students")
        if st.button("📊 Export Students CSV", use_container_width=True):
            try:
                students = Student.get_all_students()
                if students:
                    df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Students CSV",
                        data=csv,
                        file_name=f"students_export_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No students to export")
            except Exception as e:
                st.error(f"Export error: {str(e)}")

    with col2:
        st.markdown("#### Export Subjects")
        if st.button("📚 Export Subjects CSV", use_container_width=True):
            try:
                subjects = Subject.get_all_subjects()
                if subjects:
                    df = pd.DataFrame(subjects, columns=['ID', 'Subject Name', 'Created'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Subjects CSV",
                        data=csv,
                        file_name=f"subjects_export_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No subjects to export")
            except Exception as e:
                st.error(f"Export error: {str(e)}")

    with col3:
        st.markdown("#### Export Marks")
        if st.button("📝 Export Marks CSV", use_container_width=True):
            try:
                marks = Marks.get_all_marks()
                if marks:
                    df = pd.DataFrame(marks, columns=[
                        'Mark ID', 'Student', 'Subject', 'Marks Obtained', 
                        'Max Marks', 'Assessment Date', 'Assessment Type', 
                        'Created', 'Student ID', 'Subject ID'
                    ])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Marks CSV",
                        data=csv,
                        file_name=f"marks_export_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No marks to export")
            except Exception as e:
                st.error(f"Export error: {str(e)}")

    st.markdown("---")

    # Import section
    st.markdown("### 📥 Import Data")

    st.info("📋 Import data from CSV files. Ensure your files match the expected format.")

    tab1, tab2, tab3 = st.tabs(["Import Students", "Import Subjects", "Import Marks"])

    with tab1:
        st.markdown("#### Import Students from CSV")
        st.markdown("**Expected format:** Name, Class, Section, DOB (YYYY-MM-DD)")

        uploaded_students = st.file_uploader(
            "Choose students CSV file",
            type=['csv'],
            key="students_upload"
        )

        if uploaded_students:
            try:
                df = pd.read_csv(uploaded_students)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Students"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab2:
        st.markdown("#### Import Subjects from CSV")
        st.markdown("**Expected format:** Subject Name")

        uploaded_subjects = st.file_uploader(
            "Choose subjects CSV file",
            type=['csv'],
            key="subjects_upload"
        )

        if uploaded_subjects:
            try:
                df = pd.read_csv(uploaded_subjects)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Subjects"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab3:
        st.markdown("#### Import Marks from CSV")
        st.markdown("**Expected format:** Student ID, Subject ID, Marks Obtained, Max Marks, Assessment Date, Assessment Type")

        uploaded_marks = st.file_uploader(
            "Choose marks CSV file",
            type=['csv'],
            key="marks_upload"
        )

        if uploaded_marks:
            try:
                df = pd.read_csv(uploaded_marks)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                if st.button("Import Marks"):
                    st.info("Import functionality coming soon!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

elif settings_category == "System Information":
    st.subheader("ℹ️ System Information")

    # Application information
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📱 Application Info")

        app_info = {
            "Application": "Student Performance Tracker",
            "Version": "2.0.0 (SQLite)",
            "Framework": "Streamlit",
            "Database": "SQLite",
            "Python Version": "3.x",
            "Last Updated": "2024"
        }

        for key, value in app_info.items():
            st.write(f"**{key}:** {value}")

    with col2:
        st.markdown("### 📊 Database Statistics")

        try:
            db_info = get_database_info()

            db_stats = {
                "Total Students": db_info.get('student_count', 0),
                "Total Subjects": db_info.get('subject_count', 0),
                "Total Assessments": db_info.get('marks_count', 0),
                "Database Size": f"{db_info.get('database_size', 0) / 1024:.1f} KB",
                "Database Exists": "Yes" if db_info.get('database_exists', False) else "No"
            }

            for key, value in db_stats.items():
                st.write(f"**{key}:** {value}")

        except Exception as e:
            st.error(f"Could not load database statistics: {str(e)}")

    st.markdown("---")

    # System requirements
    st.markdown("### 💻 System Requirements")

    requirements = {
        "Python": "3.8 or higher",
        "RAM": "512MB minimum, 1GB recommended",
        "Storage": "100MB for application, additional for data",
        "Database": "SQLite 3.x (built-in)",
        "Browser": "Modern web browser (Chrome, Firefox, Safari, Edge)"
    }

    for requirement, details in requirements.items():
        st.write(f"**{requirement}:** {details}")

    st.markdown("---")

    # Feature list
    st.markdown("### ✨ Features")

    features = [
        "✅ Student Management (CRUD operations)",
        "✅ Subject Management with quick add",
        "✅ Marks Entry with validation and grading",
        "✅ Individual Student Report Cards",
        "✅ Class Performance Analytics",
        "✅ Interactive Visual Reports",
        "✅ CSV Export capabilities",
        "✅ Search and Filter functionality",
        "✅ SQLite Database Management",
        "✅ Responsive design",
        "✅ Sample Data Generation",
        "🔄 Data Import (Coming Soon)",
        "🔄 Advanced Analytics (Coming Soon)",
        "🔄 PDF Export (Coming Soon)"
    ]

    for feature in features:
        st.write(feature)

elif settings_category == "Application Preferences":
    st.subheader("🎛️ Application Preferences")

    st.info("👤 Preferences are stored in browser session and will reset when you close the app")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎨 Display Settings")

        # Theme selection (placeholder)
        theme = st.selectbox(
            "Theme",
            options=["Light", "Dark", "Auto"],
            help="Select application theme (feature coming soon)"
        )

        # Page size preferences
        default_page_size = st.selectbox(
            "Default Page Size",
            options=[10, 25, 50, 100],
            index=0,
            help="Default number of items per page in tables"
        )

        # Auto-refresh
        auto_refresh = st.checkbox(
            "Auto-refresh data",
            help="Automatically refresh data every 30 seconds"
        )

        # Compact view
        compact_view = st.checkbox(
            "Compact table view",
            help="Use smaller fonts and spacing in tables"
        )

    with col2:
        st.markdown("### 📊 Default Settings")

        # Default class/section for new entries
        default_class = st.selectbox(
            "Default Class",
            options=["", "10", "11", "12"],
            help="Default class for new student entries"
        )

        default_section = st.selectbox(
            "Default Section", 
            options=["", "A", "B", "C"],
            help="Default section for new student entries"
        )

        # Default assessment type
        default_assessment = st.selectbox(
            "Default Assessment Type",
            options=["Assignment", "Quiz", "Midterm", "Final"],
            help="Default type for new marks entries"
        )

        # Grade threshold
        pass_threshold = st.slider(
            "Pass Threshold (%)",
            min_value=30,
            max_value=50,
            value=40,
            help="Percentage required to pass"
        )

    # Save preferences
    if st.button("💾 Save Preferences"):
        # Store in session state
        st.session_state.update({
            'theme': theme,
            'default_page_size': default_page_size,
            'auto_refresh': auto_refresh,
            'compact_view': compact_view,
            'default_class': default_class,
            'default_section': default_section,
            'default_assessment': default_assessment,
            'pass_threshold': pass_threshold
        })
        st.success("✅ Preferences saved for this session!")

    st.markdown("---")

    # Reset preferences
    if st.button("🔄 Reset to Defaults"):
        # Clear relevant session state
        keys_to_clear = [
            'theme', 'default_page_size', 'auto_refresh', 'compact_view',
            'default_class', 'default_section', 'default_assessment', 'pass_threshold'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Preferences reset to defaults!")
        st.rerun()

elif settings_category == "Backup & Restore":
    st.subheader("💾 Backup & Restore")

    st.warning("⚠️ Regular backups are recommended to prevent data loss")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Create Backup")

        st.info("Create a complete backup of all system data")

        backup_format = st.radio(
            "Backup Format:",
            options=["CSV Archive", "Database Copy"],
            help="Choose the format for your backup"
        )

        include_settings = st.checkbox(
            "Include Settings",
            value=True,
            help="Include application settings in backup"
        )

        if st.button("🗂️ Create Full Backup", use_container_width=True):
            with st.spinner("Creating backup..."):
                try:
                    # Get all data
                    students = Student.get_all_students()
                    subjects = Subject.get_all_subjects()
                    marks = Marks.get_all_marks()

                    if backup_format == "CSV Archive":
                        # Create combined CSV export
                        import zipfile
                        import io
                        
                        # Create in-memory ZIP file
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            # Add students CSV
                            if students:
                                students_df = pd.DataFrame(students, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                                zip_file.writestr("students.csv", students_df.to_csv(index=False))
                            
                            # Add subjects CSV
                            if subjects:
                                subjects_df = pd.DataFrame(subjects, columns=['ID', 'Subject Name', 'Created'])
                                zip_file.writestr("subjects.csv", subjects_df.to_csv(index=False))
                            
                            # Add marks CSV
                            if marks:
                                marks_df = pd.DataFrame(marks, columns=[
                                    'Mark ID', 'Student', 'Subject', 'Marks Obtained', 
                                    'Max Marks', 'Assessment Date', 'Assessment Type', 
                                    'Created', 'Student ID', 'Subject ID'
                                ])
                                zip_file.writestr("marks.csv", marks_df.to_csv(index=False))

                        zip_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Download Backup Archive",
                            data=zip_buffer.read(),
                            file_name=f"student_tracker_backup_{date.today().strftime('%Y%m%d')}.zip",
                            mime="application/zip"
                        )

                    else:  # Database Copy
                        st.info("Database copy backup coming soon!")

                except Exception as e:
                    st.error(f"Backup creation failed: {str(e)}")

    with col2:
        st.markdown("### 📥 Restore from Backup")

        st.info("Restore system data from a previous backup")

        uploaded_backup = st.file_uploader(
            "Choose backup file",
            type=['zip', 'db'],
            help="Select your backup file"
        )

        if uploaded_backup:
            st.success(f"Backup file '{uploaded_backup.name}' uploaded successfully")

            restore_options = st.multiselect(
                "What to restore:",
                options=["Students", "Subjects", "Marks", "Settings"],
                default=["Students", "Subjects", "Marks"]
            )

            overwrite_existing = st.checkbox(
                "Overwrite existing data",
                help="⚠️ This will replace current data"
            )

            if st.button("🔄 Restore Data", use_container_width=True):
                if overwrite_existing:
                    st.warning("Restore functionality coming soon!")
                else:
                    st.info("Please confirm overwrite to proceed")

# Footer with support information
st.markdown("---")
st.markdown("### 📞 Support & Help")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📧 Email Support**")
    st.write("kratikjain121@gmail.com")

with col2:
    st.markdown("**📖 Documentation**")  
    st.write("Available in Help sections")

with col3:
    st.markdown("**🐛 Report Issues**")
    st.write("Use the help sections in each page")

# Quick actions sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🚀 Quick Actions")

    if st.button("🏠 Go to Dashboard", use_container_width=True):
        st.switch_page("app.py")

    if st.button("👥 Manage Students", use_container_width=True):
        st.switch_page("pages/1_Manage_Students.py")

    if st.button("📝 Enter Marks", use_container_width=True):
        st.switch_page("pages/3_Enter_Update_Marks.py")

    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/5_Class_Analytics.py")
