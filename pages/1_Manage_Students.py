"""
Manage Students Page - CRUD operations for students
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student, display_students_table, student_form
from utils.ui_components import (
    paginate_data, display_pagination_controls, create_search_filters,
    display_data_summary, create_confirmation_dialog
)
from utils.validations import validate_name, validate_class_section, validate_date_of_birth

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
        ["View All Students", "Add New Student", "Search & Filter", "Edit Student", "Delete Student"],
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
                # Pagination
                page_size = st.selectbox("Students per page:", [10, 25, 50, 100], index=0)
                paginated_data, current_page, total_pages, total_items = paginate_data(
                    students_data, page_size, "students"
                )

                # Display pagination info
                st.info(f"Showing {len(paginated_data)} of {total_items} students (Page {current_page} of {total_pages})")

                # Display table
                display_students_table(paginated_data)

                # Pagination controls
                display_pagination_controls(current_page, total_pages, "students")

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
                    st.write(f"• {student[1]} (Class {student[2]}-{student[3]}) - Added: {student[5]}")
            else:
                st.info("No recent additions")
        except Exception as e:
            st.warning("Could not load recent additions")

elif action == "Search & Filter":
    st.subheader("🔍 Search & Filter Students")

    # Search filters
    filters = create_search_filters()

    # Apply filters
    with st.spinner("Searching students..."):
        try:
            search_results = Student.search_students(
                search_term=filters.get('search_term', ''),
                class_filter=filters.get('class_filter', ''),
                section_filter=filters.get('section_filter', '')
            )

            if search_results:
                st.success(f"Found {len(search_results)} students matching your criteria")

                # Pagination for search results
                page_size = st.selectbox("Results per page:", [10, 25, 50], index=0, key="search_page_size")
                paginated_results, current_page, total_pages, total_items = paginate_data(
                    search_results, page_size, "search"
                )

                # Display results
                display_students_table(paginated_results)

                # Pagination controls
                display_pagination_controls(current_page, total_pages, "search")

                # Export filtered results
                with st.expander("📥 Export Search Results"):
                    if st.button("Export to CSV"):
                        df = pd.DataFrame(search_results, columns=['ID', 'Name', 'Class', 'Section', 'DOB', 'Created'])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="filtered_students.csv",
                            mime="text/csv"
                        )

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
                    if create_confirmation_dialog(
                        f"Are you sure you want to delete {student_data[1]}? This action cannot be undone.",
                        f"delete_student_{selected_student_id}"
                    ):
                        if Student.delete_student(selected_student_id):
                            st.success(f"✅ Student {student_data[1]} deleted successfully!")
                            # Clear session state to refresh the page
                            if f"delete_student_{selected_student_id}" in st.session_state:
                                del st.session_state[f"delete_student_{selected_student_id}"]
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

# Help section
with st.expander("ℹ️ Help & Tips"):
    st.markdown("""
    ### Student Management Tips:

    **Adding Students:**
    - Name: Enter full name (at least 2 characters)
    - Class: Enter class/grade (e.g., 10, 11, 12)
    - Section: Enter section (e.g., A, B, C)
    - DOB: Select date of birth (must be in the past)

    **Search & Filter:**
    - Use partial names to search (e.g., "John" will find "John Doe")
    - Filter by class and section for targeted views
    - Export filtered results for external use

    **Editing Students:**
    - Select student from dropdown to modify information
    - All fields are required and will be validated

    **Deleting Students:**
    - ⚠️ This will permanently remove all student marks
    - Double confirmation required for safety

    **Data Import:**
    - Use CSV export/import for bulk operations
    - Ensure data follows the required format
    """)
