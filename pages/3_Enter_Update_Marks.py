"""
Enter/Update Marks Page - Marks entry and management
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject, subject_selector
from models.marks import Marks, display_marks_table
from utils.ui_components import paginate_data, display_pagination_controls
from utils.validations import validate_marks, validate_assessment_date

st.set_page_config(
    page_title="Enter Marks",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Enter & Update Marks")
st.markdown("Record student assessments and track academic performance")

# Sidebar for navigation
with st.sidebar:
    st.subheader("Marks Management")
    action = st.radio(
        "Choose Action:",
        ["Enter New Marks", "View All Marks", "Update Marks", "Bulk Entry", "Delete Marks"],
        key="marks_action"
    )

# Helper function to get student options
def get_student_options():
    """Get formatted student options for selectbox"""
    students = Student.get_all_students()
    if students:
        return {f"{student[1]} - {student[2]}-{student[3]} (ID: {student[0]})": student[0] 
                for student in students}
    return {}

# Helper function to get subject options
def get_subject_options():
    """Get formatted subject options for selectbox"""
    subjects = Subject.get_all_subjects()
    if subjects:
        return {f"{subject[1]} (ID: {subject[0]})": subject[0] 
                for subject in subjects}
    return {}

# Main content area
if action == "Enter New Marks":
    st.subheader("➕ Enter New Marks")

    # Check if students and subjects exist
    students = Student.get_all_students()
    subjects = Subject.get_all_subjects()

    if not students:
        st.warning("⚠️ No students found. Please add students first.")
        if st.button("Go to Manage Students"):
            st.switch_page("pages/1_Manage_Students.py")
    elif not subjects:
        st.warning("⚠️ No subjects found. Please add subjects first.")
        if st.button("Go to Manage Subjects"):
            st.switch_page("pages/2_Manage_Subjects.py")
    else:
        # Marks entry form
        with st.form("marks_entry_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Student selection
                student_options = get_student_options()
                selected_student_key = st.selectbox(
                    "Select Student *",
                    options=list(student_options.keys()),
                    help="Choose the student for marks entry"
                )
                student_id = student_options.get(selected_student_key)

                # Subject selection
                subject_options = get_subject_options()
                selected_subject_key = st.selectbox(
                    "Select Subject *",
                    options=list(subject_options.keys()),
                    help="Choose the subject for assessment"
                )
                subject_id = subject_options.get(selected_subject_key)

            with col2:
                # Marks input
                col2a, col2b = st.columns(2)
                with col2a:
                    marks_obtained = st.number_input(
                        "Marks Obtained *",
                        min_value=0,
                        max_value=1000,
                        value=0,
                        help="Enter the marks scored by student"
                    )
                with col2b:
                    max_marks = st.number_input(
                        "Maximum Marks *",
                        min_value=1,
                        max_value=1000,
                        value=100,
                        help="Enter the maximum possible marks"
                    )

                # Assessment details
                assessment_date = st.date_input(
                    "Assessment Date *",
                    value=date.today(),
                    max_value=date.today(),
                    help="Date when assessment was conducted"
                )

                assessment_type = st.selectbox(
                    "Assessment Type *",
                    options=["Assignment", "Quiz", "Midterm", "Final"],
                    help="Type of assessment"
                )

            # Submit button
            submitted = st.form_submit_button("Add Marks", type="primary")

            if submitted:
                # Validate input
                is_valid_marks, marks_errors = validate_marks(marks_obtained, max_marks)
                is_valid_date, date_errors = validate_assessment_date(assessment_date)

                if is_valid_marks and is_valid_date and student_id and subject_id:
                    # Add marks to database
                    success = Marks.add_marks(
                        student_id, subject_id, marks_obtained, max_marks, 
                        assessment_date, assessment_type
                    )

                    if success:
                        percentage = Marks.calculate_percentage(marks_obtained, max_marks)
                        grade = Marks.calculate_grade(percentage)

                        st.success(f"""
                        ✅ **Marks added successfully!**

                        - Student: {selected_student_key.split(' - ')[0]}
                        - Subject: {selected_subject_key.split(' (')[0]}
                        - Marks: {marks_obtained}/{max_marks} ({percentage}%)
                        - Grade: {grade}
                        - Assessment: {assessment_type} on {assessment_date}
                        """)
                    else:
                        st.error("❌ Failed to add marks. Please try again.")
                else:
                    # Display validation errors
                    for error in marks_errors + date_errors:
                        st.error(f"❌ {error}")

elif action == "View All Marks":
    st.subheader("📋 All Marks")

    # Load marks data
    with st.spinner("Loading marks..."):
        try:
            marks_data = Marks.get_all_marks()

            if marks_data:
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Student filter
                    student_names = ["All"] + list(set([mark[1] for mark in marks_data]))
                    selected_student = st.selectbox("Filter by Student:", student_names)

                with col2:
                    # Subject filter
                    subject_names = ["All"] + list(set([mark[2] for mark in marks_data]))
                    selected_subject = st.selectbox("Filter by Subject:", subject_names)

                with col3:
                    # Assessment type filter
                    assessment_types = ["All"] + list(set([mark[6] for mark in marks_data]))
                    selected_type = st.selectbox("Filter by Type:", assessment_types)

                # Apply filters
                filtered_data = marks_data
                if selected_student != "All":
                    filtered_data = [mark for mark in filtered_data if mark[1] == selected_student]
                if selected_subject != "All":
                    filtered_data = [mark for mark in filtered_data if mark[2] == selected_subject]
                if selected_type != "All":
                    filtered_data = [mark for mark in filtered_data if mark[6] == selected_type]

                if filtered_data:
                    # Pagination
                    page_size = st.selectbox("Records per page:", [10, 25, 50, 100], index=0)
                    paginated_data, current_page, total_pages, total_items = paginate_data(
                        filtered_data, page_size, "marks"
                    )

                    st.info(f"Showing {len(paginated_data)} of {total_items} records (Page {current_page} of {total_pages})")

                    # Display table
                    display_marks_table(paginated_data)

                    # Pagination controls
                    display_pagination_controls(current_page, total_pages, "marks")

                    # Export option
                    with st.expander("📥 Export Marks"):
                        if st.button("Export to CSV"):
                            df = pd.DataFrame(filtered_data, columns=[
                                'Mark ID', 'Student', 'Subject', 'Marks Obtained', 'Max Marks',
                                'Assessment Date', 'Assessment Type', 'Created', 'Student ID', 'Subject ID'
                            ])
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="marks_export.csv",
                                mime="text/csv"
                            )
                else:
                    st.warning("No marks found matching the selected filters")

            else:
                st.info("No marks found. Enter some marks to get started!")

        except Exception as e:
            st.error(f"Error loading marks: {str(e)}")

elif action == "Update Marks":
    st.subheader("✏️ Update Marks")

    # Load marks for selection
    try:
        all_marks = Marks.get_all_marks()

        if all_marks:
            # Create options for marks selection
            marks_options = {}
            for mark in all_marks:
                key = f"{mark[1]} - {mark[2]} ({mark[3]}/{mark[4]}) - {mark[5]}"
                marks_options[key] = mark[0]  # mark_id

            selected_mark_key = st.selectbox(
                "Select marks entry to update:",
                options=list(marks_options.keys()),
                help="Choose the marks entry you want to modify"
            )

            if selected_mark_key:
                mark_id = marks_options[selected_mark_key]

                # Find the selected mark data
                selected_mark_data = next((mark for mark in all_marks if mark[0] == mark_id), None)

                if selected_mark_data:
                    # Display current information
                    with st.expander("Current Information"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Student:** {selected_mark_data[1]}")
                            st.write(f"**Subject:** {selected_mark_data[2]}")
                            st.write(f"**Current Marks:** {selected_mark_data[3]}/{selected_mark_data[4]}")
                        with col2:
                            current_percentage = Marks.calculate_percentage(selected_mark_data[3], selected_mark_data[4])
                            current_grade = Marks.calculate_grade(current_percentage)
                            st.write(f"**Percentage:** {current_percentage}%")
                            st.write(f"**Grade:** {current_grade}")
                            st.write(f"**Assessment Type:** {selected_mark_data[6]}")

                    # Update form
                    with st.form("update_marks_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            new_marks_obtained = st.number_input(
                                "New Marks Obtained *",
                                min_value=0,
                                max_value=1000,
                                value=selected_mark_data[3],
                                help="Enter the updated marks"
                            )

                            new_max_marks = st.number_input(
                                "New Maximum Marks *",
                                min_value=1,
                                max_value=1000,
                                value=selected_mark_data[4],
                                help="Enter the updated maximum marks"
                            )

                        with col2:
                            new_assessment_date = st.date_input(
                                "Assessment Date *",
                                value=selected_mark_data[5],
                                max_value=date.today()
                            )

                            new_assessment_type = st.selectbox(
                                "Assessment Type *",
                                options=["Assignment", "Quiz", "Midterm", "Final"],
                                index=["Assignment", "Quiz", "Midterm", "Final"].index(selected_mark_data[6])
                            )

                        # Submit button
                        update_submitted = st.form_submit_button("Update Marks", type="primary")

                        if update_submitted:
                            # Validate input
                            is_valid_marks, marks_errors = validate_marks(new_marks_obtained, new_max_marks)
                            is_valid_date, date_errors = validate_assessment_date(new_assessment_date)

                            if is_valid_marks and is_valid_date:
                                # Update marks in database
                                success = Marks.update_marks(
                                    mark_id, new_marks_obtained, new_max_marks,
                                    new_assessment_date, new_assessment_type
                                )

                                if success:
                                    new_percentage = Marks.calculate_percentage(new_marks_obtained, new_max_marks)
                                    new_grade = Marks.calculate_grade(new_percentage)

                                    st.success(f"""
                                    ✅ **Marks updated successfully!**

                                    - Student: {selected_mark_data[1]}
                                    - Subject: {selected_mark_data[2]}
                                    - Updated Marks: {new_marks_obtained}/{new_max_marks} ({new_percentage}%)
                                    - New Grade: {new_grade}
                                    """)
                                else:
                                    st.error("❌ Failed to update marks. Please try again.")
                            else:
                                # Display validation errors
                                for error in marks_errors + date_errors:
                                    st.error(f"❌ {error}")
        else:
            st.info("No marks available for update")

    except Exception as e:
        st.error(f"Error loading marks for update: {str(e)}")

elif action == "Bulk Entry":
    st.subheader("📊 Bulk Marks Entry")
    st.info("Enter marks for multiple students at once for a specific subject and assessment")

    # Select subject and assessment details
    subjects = Subject.get_all_subjects()
    students = Student.get_all_students()

    if not subjects or not students:
        st.warning("⚠️ Please ensure both students and subjects are available before bulk entry")
    else:
        with st.form("bulk_entry_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Subject selection
                subject_options = get_subject_options()
                selected_subject_key = st.selectbox(
                    "Select Subject *",
                    options=list(subject_options.keys()),
                    help="Choose subject for bulk entry"
                )
                subject_id = subject_options.get(selected_subject_key)

                # Assessment details
                max_marks = st.number_input(
                    "Maximum Marks *",
                    min_value=1,
                    max_value=1000,
                    value=100
                )

            with col2:
                assessment_date = st.date_input(
                    "Assessment Date *",
                    value=date.today(),
                    max_value=date.today()
                )

                assessment_type = st.selectbox(
                    "Assessment Type *",
                    options=["Assignment", "Quiz", "Midterm", "Final"]
                )

            # Class/Section filter for students
            class_filter = st.selectbox(
                "Filter by Class (optional):",
                options=["All"] + Student.get_unique_classes()
            )

            section_filter = st.selectbox(
                "Filter by Section (optional):",
                options=["All"] + Student.get_unique_sections()
            )

            submitted = st.form_submit_button("Prepare Bulk Entry", type="primary")

        if submitted and subject_id:
            # Get filtered students
            if class_filter != "All" or section_filter != "All":
                filtered_students = Student.search_students(
                    class_filter=class_filter if class_filter != "All" else "",
                    section_filter=section_filter if section_filter != "All" else ""
                )
            else:
                filtered_students = students

            if filtered_students:
                st.subheader("Enter Marks for Each Student")

                marks_data = []

                # Create form for each student
                with st.form("bulk_marks_form"):
                    for i, student in enumerate(filtered_students):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**{student[1]}** (Class {student[2]}-{student[3]})")
                        with col2:
                            marks = st.number_input(
                                f"Marks",
                                min_value=0,
                                max_value=max_marks,
                                value=0,
                                key=f"marks_{student[0]}",
                                help=f"Enter marks for {student[1]}"
                            )
                            marks_data.append((student[0], marks))

                    bulk_submitted = st.form_submit_button("Submit All Marks", type="primary")

                if bulk_submitted:
                    success_count = 0
                    error_count = 0

                    for student_id, marks_obtained in marks_data:
                        if marks_obtained > 0:  # Only add if marks entered
                            is_valid, _ = validate_marks(marks_obtained, max_marks)
                            if is_valid:
                                if Marks.add_marks(student_id, subject_id, marks_obtained, 
                                                 max_marks, assessment_date, assessment_type):
                                    success_count += 1
                                else:
                                    error_count += 1

                    if success_count > 0:
                        st.success(f"✅ Successfully added marks for {success_count} students!")
                    if error_count > 0:
                        st.warning(f"⚠️ Failed to add marks for {error_count} students")

elif action == "Delete Marks":
    st.subheader("🗑️ Delete Marks")
    st.warning("⚠️ **Warning**: Deleting marks cannot be undone!")

    # Load marks for deletion
    try:
        all_marks = Marks.get_all_marks()

        if all_marks:
            # Create options for marks selection
            marks_options = {}
            for mark in all_marks:
                key = f"{mark[1]} - {mark[2]} ({mark[3]}/{mark[4]}) - {mark[5]} [{mark[6]}]"
                marks_options[key] = mark[0]  # mark_id

            selected_mark_key = st.selectbox(
                "Select marks entry to delete:",
                options=list(marks_options.keys()),
                help="Choose the marks entry to remove permanently"
            )

            if selected_mark_key:
                mark_id = marks_options[selected_mark_key]
                selected_mark_data = next((mark for mark in all_marks if mark[0] == mark_id), None)

                if selected_mark_data:
                    # Display mark details
                    st.error(f"""
                    **Entry to be deleted:**
                    - Student: {selected_mark_data[1]}
                    - Subject: {selected_mark_data[2]}
                    - Marks: {selected_mark_data[3]}/{selected_mark_data[4]}
                    - Date: {selected_mark_data[5]}
                    - Type: {selected_mark_data[6]}
                    """)

                    # Confirmation
                    if st.checkbox("I confirm I want to delete this marks entry"):
                        if st.button("🗑️ Delete Marks Entry", type="primary"):
                            if Marks.delete_marks(mark_id):
                                st.success("✅ Marks entry deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete marks entry")
        else:
            st.info("No marks available for deletion")

    except Exception as e:
        st.error(f"Error loading marks for deletion: {str(e)}")

# Statistics sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Marks Statistics")

    try:
        all_marks = Marks.get_all_marks()
        if all_marks:
            total_marks = len(all_marks)
            st.metric("Total Entries", total_marks)

            # Calculate some basic statistics
            total_obtained = sum(mark[3] for mark in all_marks)
            total_possible = sum(mark[4] for mark in all_marks)
            overall_percentage = (total_obtained / total_possible * 100) if total_possible > 0 else 0

            st.metric("Overall Average", f"{overall_percentage:.1f}%")

            # Grade distribution
            grades = []
            for mark in all_marks:
                percentage = Marks.calculate_percentage(mark[3], mark[4])
                grade = Marks.calculate_grade(percentage)
                grades.append(grade)

            grade_counts = {}
            for grade in grades:
                grade_counts[grade] = grade_counts.get(grade, 0) + 1

            st.write("**Grade Distribution:**")
            for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'F']:
                if grade in grade_counts:
                    st.write(f"• {grade}: {grade_counts[grade]}")
        else:
            st.info("No marks data available")

    except Exception as e:
        st.error("Could not load statistics")

# Help section
with st.expander("ℹ️ Help & Tips"):
    st.markdown("""
    ### Marks Entry Tips:

    **Single Entry:**
    - Select student and subject from dropdowns
    - Enter marks obtained and maximum marks
    - Choose appropriate assessment type
    - Marks will be automatically graded

    **Bulk Entry:**
    - Choose subject and assessment details first
    - Filter students by class/section if needed
    - Enter marks for multiple students at once
    - Only students with marks > 0 will be saved

    **Grading System:**
    - A+: 90-100%
    - A: 80-89%
    - B+: 70-79%
    - B: 60-69%
    - C+: 50-59%
    - C: 40-49%
    - F: Below 40%

    **Best Practices:**
    - Enter assessment date accurately
    - Use consistent assessment types
    - Double-check marks before submission
    - Use bulk entry for class-wide assessments
    - Regular backup of marks data
    """)
