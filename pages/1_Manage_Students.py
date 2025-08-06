"""
Manage Students Page - CRUD operations for students (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student, display_students_table, student_form

st.set_page_config(
    page_title="Manage Students",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Manage Students")
st.markdown("Add, edit, view, and manage student records")

# Sidebar for navigation
with st.sidebar:
    st.subheader("Student Management")
    action = st.radio(
        "Choose Action:",
        ["View All Students", "Add New Student", "Search Students", "Edit Student", "Delete Student"],
        key="student_action"
    )

# Main content area
if action == "View All Students":
    st.subheader("📋 All Students")

    # Load students data
    with st.spinner("Loading students..."):
        try:
            students_data = Student.get_all_students()

            if students_data:
                st.success(f"Found {len(students_data)} students")
                display_students_table(students_data)

                # Export option
                with st.expander("📥 Export Students"):
                    if st.button("Export to CSV"):
                        df = pd.DataFrame(students_data, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"students_export_{date.today().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )

            else:
                st.info("No students found. Add some students to get started!")

        except Exception as e:
            st.error(f"Error loading students: {str(e)}")

elif action == "Add New Student":
    st.subheader("➕ Add New Student")

    # Student form for adding
    student_form(form_type="Add")

    # Display recent additions
    with st.expander("Recent Student Additions"):
        try:
            recent_students = Student.get_all_students()[-5:]  # Last 5 students
            if recent_students:
                for student in recent_students:
                    st.write(f"• {student[1]} (Class {student[2]}-{student[3]})")
            else:
                st.info("No recent additions")
        except Exception as e:
            st.warning("Could not load recent additions")

elif action == "Search Students":
    st.subheader("🔍 Search Students")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("Search by name:", placeholder="Enter student name...")

    with col2:
        class_filter = st.selectbox("Filter by Class:", options=["All", "10", "11", "12"])

    with col3:
        section_filter = st.selectbox("Filter by Section:", options=["All", "A", "B", "C"])

    if st.button("🔍 Search") or search_term:
        with st.spinner("Searching students..."):
            try:
                search_results = Student.search_students(
                    search_term=search_term,
                    class_filter=class_filter if class_filter != "All" else "",
                    section_filter=section_filter if section_filter != "All" else ""
                )

                if search_results:
                    st.success(f"Found {len(search_results)} students matching your criteria")
                    display_students_table(search_results)
                else:
                    st.warning("No students found matching your search criteria")

            except Exception as e:
                st.error(f"Search error: {str(e)}")

elif action == "Edit Student":
    st.subheader("✏️ Edit Student")

    # Select student to edit
    try:
        students = Student.get_all_students()
        if students:
            # Create selectbox with student options
            student_options = {f"{student[1]} (ID: {student[0]} - {student[2]}-{student[3]})": student[0] 
                             for student in students}

            selected_student_key = st.selectbox(
                "Select student to edit:",
                options=list(student_options.keys()),
                key="edit_student_select"
            )

            if selected_student_key:
                selected_student_id = student_options[selected_student_key]

                # Get student data
                student_data = Student.get_student_by_id(selected_student_id)

                if student_data:
                    st.info(f"Editing: {student_data[1]}")

                    # Display current information
                    with st.expander("Current Information"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {student_data[1]}")
                            st.write(f"**Class:** {student_data[2]}")
                        with col2:
                            st.write(f"**Section:** {student_data[3]}")
                            st.write(f"**DOB:** {student_data[4]}")

                    # Edit form
                    student_form(student_data=student_data, form_type="Update")

                else:
                    st.error("Could not load student data")
        else:
            st.info("No students available for editing")

    except Exception as e:
        st.error(f"Error loading students for editing: {str(e)}")

elif action == "Delete Student":
    st.subheader("🗑️ Delete Student")

    st.warning("⚠️ **Warning**: Deleting a student will also remove all their marks and cannot be undone!")

    try:
        students = Student.get_all_students()
        if students:
            # Create selectbox with student options
            student_options = {f"{student[1]} (ID: {student[0]} - {student[2]}-{student[3]})": student[0] 
                             for student in students}

            selected_student_key = st.selectbox(
                "Select student to delete:",
                options=list(student_options.keys()),
                key="delete_student_select"
            )

            if selected_student_key:
                selected_student_id = student_options[selected_student_key]
                student_data = Student.get_student_by_id(selected_student_id)

                if student_data:
                    # Display student info
                    st.error(f"**Student to be deleted:** {student_data[1]} (Class {student_data[2]}-{student_data[3]})")

                    # Confirmation
                    if st.checkbox(f"I confirm I want to delete {student_data[1]}"):
                        if st.button("🗑️ Delete Student", type="primary"):
                            if Student.delete_student(selected_student_id):
                                st.success(f"✅ Student {student_data[1]} deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete student")
        else:
            st.info("No students available for deletion")

    except Exception as e:
        st.error(f"Error loading students for deletion: {str(e)}")

# Statistics sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Student Statistics")

    try:
        all_students = Student.get_all_students()
        student_count = len(all_students) if all_students else 0

        # Basic stats
        st.metric("Total Students", student_count)

        if all_students:
            # Class distribution
            class_counts = {}
            for student in all_students:
                class_name = student[2]
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

            st.write("**Students by Class:**")
            for class_name, count in sorted(class_counts.items()):
                st.write(f"• Class {class_name}: {count}")

            # Section distribution
            section_counts = {}
            for student in all_students:
                section_name = student[3]
                section_counts[section_name] = section_counts.get(section_name, 0) + 1

            st.write("**Students by Section:**")
            for section_name, count in sorted(section_counts.items()):
                st.write(f"• Section {section_name}: {count}")

    except Exception as e:
        st.error("Could not load statistics")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📚 Manage Subjects"):
        st.switch_page("pages/2_Manage_Subjects.py")

with col3:
    if st.button("📝 Enter Marks"):
        st.switch_page("pages/3_Enter_Update_Marks.py")
