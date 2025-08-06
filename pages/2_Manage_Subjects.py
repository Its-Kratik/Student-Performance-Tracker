"""
Manage Subjects Page - CRUD operations for subjects
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.subject import Subject, display_subjects_table, subject_form, display_subject_statistics
from utils.ui_components import (
    paginate_data, display_pagination_controls, create_confirmation_dialog
)

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
                # Pagination
                page_size = st.selectbox("Subjects per page:", [10, 25, 50], index=0)
                paginated_data, current_page, total_pages, total_items = paginate_data(
                    subjects_data, page_size, "subjects"
                )

                # Display pagination info
                st.info(f"Showing {len(paginated_data)} of {total_items} subjects (Page {current_page} of {total_pages})")

                # Display table
                display_subjects_table(paginated_data)

                # Pagination controls
                display_pagination_controls(current_page, total_pages, "subjects")

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

    # Display recent additions
    with st.expander("Recent Subject Additions"):
        try:
            recent_subjects = Subject.get_all_subjects()[-5:]  # Last 5 subjects
            if recent_subjects:
                for subject in recent_subjects:
                    st.write(f"• {subject[1]} - Added: {subject[2]}")
            else:
                st.info("No recent additions")
        except Exception as e:
            st.warning("Could not load recent additions")

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

                    # Show impact warning
                    st.warning("This will delete:")
                    st.write("• The subject from the system")
                    st.write("• All marks/assessments for this subject")
                    st.write("• All related performance data")

                    # Confirmation
                    if create_confirmation_dialog(
                        f"Are you sure you want to delete '{subject_data[1]}'? This action cannot be undone.",
                        f"delete_subject_{selected_subject_id}"
                    ):
                        if Subject.delete_subject(selected_subject_id):
                            st.success(f"✅ Subject '{subject_data[1]}' deleted successfully!")
                            # Clear session state to refresh the page
                            if f"delete_subject_{selected_subject_id}" in st.session_state:
                                del st.session_state[f"delete_subject_{selected_subject_id}"]
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

        # Additional stats
        all_subjects = Subject.get_all_subjects()
        if all_subjects:
            st.markdown("**Subject Categories:**")

            # Simple categorization based on subject names
            science_subjects = [s for s in all_subjects if any(word in s[1].lower() 
                              for word in ['physics', 'chemistry', 'biology', 'science'])]
            math_subjects = [s for s in all_subjects if 'math' in s[1].lower()]
            language_subjects = [s for s in all_subjects if any(word in s[1].lower() 
                               for word in ['english', 'language', 'literature'])]
            social_subjects = [s for s in all_subjects if any(word in s[1].lower() 
                             for word in ['history', 'geography', 'social', 'economics'])]

            if science_subjects:
                st.write(f"🔬 Science: {len(science_subjects)}")
            if math_subjects:
                st.write(f"🔢 Mathematics: {len(math_subjects)}")
            if language_subjects:
                st.write(f"📖 Languages: {len(language_subjects)}")
            if social_subjects:
                st.write(f"🏛️ Social Studies: {len(social_subjects)}")

            other_count = len(all_subjects) - len(science_subjects) - len(math_subjects) - len(language_subjects) - len(social_subjects)
            if other_count > 0:
                st.write(f"📚 Others: {other_count}")

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

# Help section
with st.expander("ℹ️ Help & Tips"):
    st.markdown("""
    ### Subject Management Tips:

    **Adding Subjects:**
    - Subject names must be unique
    - Use proper capitalization (e.g., "Mathematics" not "mathematics")
    - Keep names concise but descriptive
    - Minimum 2 characters, maximum 50 characters

    **Quick Add:**
    - Use the quick add buttons for common subjects
    - Prevents typing errors and ensures consistency

    **Subject Organization:**
    - Group related subjects (e.g., Physics, Chemistry under Science)
    - Use consistent naming conventions
    - Consider adding subject codes if needed

    **Editing Subjects:**
    - You can modify subject names but not IDs
    - Changes will reflect in all existing marks

    **Deleting Subjects:**
    - ⚠️ This permanently removes all associated marks
    - Consider archiving instead of deleting if historical data is important
    - Double confirmation required for safety

    **Best Practices:**
    - Plan your subject structure before adding marks
    - Use standard academic subject names
    - Keep subject list manageable (typically 8-15 subjects)
    - Regular cleanup of unused subjects
    """)
