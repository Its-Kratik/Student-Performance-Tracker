"""
Manage Subjects Page - CRUD operations for subjects (SQLite version)
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.subject import Subject, display_subjects_table, subject_form, display_subject_statistics

st.set_page_config(
    page_title="Manage Subjects",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Manage Subjects")
st.markdown("Add, edit, view, and manage academic subjects")

# Sidebar for navigation
with st.sidebar:
    st.subheader("Subject Management")
    action = st.radio(
        "Choose Action:",
        ["View All Subjects", "Add New Subject", "Edit Subject", "Delete Subject"],
        key="subject_action"
    )

# Main content area
if action == "View All Subjects":
    st.subheader("📋 All Subjects")

    # Load subjects data
    with st.spinner("Loading subjects..."):
        try:
            subjects_data = Subject.get_all_subjects()

            if subjects_data:
                st.success(f"Found {len(subjects_data)} subjects")
                display_subjects_table(subjects_data)

                # Export option
                with st.expander("📥 Export Subjects"):
                    if st.button("Export to CSV"):
                        df = pd.DataFrame(subjects_data, columns=['ID', 'Subject Name', 'Created'])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="subjects_list.csv",
                            mime="text/csv"
                        )

            else:
                st.info("No subjects found. Add some subjects to get started!")

        except Exception as e:
            st.error(f"Error loading subjects: {str(e)}")

elif action == "Add New Subject":
    st.subheader("➕ Add New Subject")

    # Subject form for adding
    subject_form(form_type="Add")

    # Quick add common subjects
    st.markdown("---")
    st.subheader("🚀 Quick Add Common Subjects")

    common_subjects = [
        "Mathematics", "Physics", "Chemistry", "Biology", "English",
        "History", "Geography", "Computer Science", "Economics", "Psychology"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Core Subjects:**")
        for subject in common_subjects[:5]:
            if st.button(f"Add {subject}", key=f"add_{subject}"):
                if Subject.add_subject(subject):
                    st.success(f"✅ {subject} added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to add {subject} (may already exist)")

    with col2:
        st.write("**Additional Subjects:**")
        for subject in common_subjects[5:]:
            if st.button(f"Add {subject}", key=f"add_{subject}"):
                if Subject.add_subject(subject):
                    st.success(f"✅ {subject} added successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to add {subject} (may already exist)")

elif action == "Edit Subject":
    st.subheader("✏️ Edit Subject")

    # Select subject to edit
    try:
        subjects = Subject.get_all_subjects()
        if subjects:
            # Create selectbox with subject options
            subject_options = {f"{subject[1]} (ID: {subject[0]})": subject[0] 
                             for subject in subjects}

            selected_subject_key = st.selectbox(
                "Select subject to edit:",
                options=list(subject_options.keys()),
                key="edit_subject_select"
            )

            if selected_subject_key:
                selected_subject_id = subject_options[selected_subject_key]

                # Get subject data
                subject_data = Subject.get_subject_by_id(selected_subject_id)

                if subject_data:
                    st.info(f"Editing: {subject_data[1]}")

                    # Display current information
                    with st.expander("Current Information"):
                        st.write(f"**Subject ID:** {subject_data[0]}")
                        st.write(f"**Subject Name:** {subject_data[1]}")

                    # Edit form
                    subject_form(subject_data=subject_data, form_type="Update")

                else:
                    st.error("Could not load subject data")
        else:
            st.info("No subjects available for editing")

    except Exception as e:
        st.error(f"Error loading subjects for editing: {str(e)}")

elif action == "Delete Subject":
    st.subheader("🗑️ Delete Subject")

    st.warning("⚠️ **Warning**: Deleting a subject will also remove all marks for that subject and cannot be undone!")

    try:
        subjects = Subject.get_all_subjects()
        if subjects:
            # Create selectbox with subject options
            subject_options = {f"{subject[1]} (ID: {subject[0]})": subject[0] 
                             for subject in subjects}

            selected_subject_key = st.selectbox(
                "Select subject to delete:",
                options=list(subject_options.keys()),
                key="delete_subject_select"
            )

            if selected_subject_key:
                selected_subject_id = subject_options[selected_subject_key]
                subject_data = Subject.get_subject_by_id(selected_subject_id)

                if subject_data:
                    # Display subject info
                    st.error(f"**Subject to be deleted:** {subject_data[1]}")

                    # Confirmation
                    if st.checkbox(f"I confirm I want to delete '{subject_data[1]}'"):
                        if st.button("🗑️ Delete Subject", type="primary"):
                            if Subject.delete_subject(selected_subject_id):
                                st.success(f"✅ Subject '{subject_data[1]}' deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete subject")
        else:
            st.info("No subjects available for deletion")

    except Exception as e:
        st.error(f"Error loading subjects for deletion: {str(e)}")

# Statistics sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Subject Statistics")

    try:
        # Display subject statistics
        display_subject_statistics()

    except Exception as e:
        st.error("Could not load statistics")

# Search functionality
st.markdown("---")
st.subheader("🔍 Search Subjects")

search_term = st.text_input("Search by subject name:", placeholder="Enter subject name...")

if search_term:
    with st.spinner("Searching..."):
        try:
            search_results = Subject.search_subjects(search_term)

            if search_results:
                st.success(f"Found {len(search_results)} subjects matching '{search_term}'")
                display_subjects_table(search_results)
            else:
                st.warning(f"No subjects found matching '{search_term}'")

        except Exception as e:
            st.error(f"Search error: {str(e)}")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("👥 Manage Students"):
        st.switch_page("pages/1_Manage_Students.py")

with col3:
    if st.button("📝 Enter Marks"):
        st.switch_page("pages/3_Enter_Update_Marks.py")
