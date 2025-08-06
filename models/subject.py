"""
Subject Model - CRUD operations for Subject entity
"""
import streamlit as st
import pandas as pd
from db.mysql_connection import execute_query, fetch_all, fetch_one

class Subject:
    def __init__(self, subject_id=None, subject_name=None):
        self.subject_id = subject_id
        self.subject_name = subject_name

    @staticmethod
    def add_subject(subject_name: str) -> bool:
        """Add new subject to database"""
        query = "INSERT INTO Subject (subject_name) VALUES (%s)"
        return execute_query(query, (subject_name,))

    @staticmethod
    def get_all_subjects() -> list:
        """Get all subjects from database"""
        query = "SELECT subject_id, subject_name, created_at FROM Subject ORDER BY subject_name"
        return fetch_all(query)

    @staticmethod
    def get_subject_by_id(subject_id: int) -> tuple:
        """Get subject by ID"""
        query = "SELECT subject_id, subject_name FROM Subject WHERE subject_id = %s"
        return fetch_one(query, (subject_id,))

    @staticmethod
    def get_subject_by_name(subject_name: str) -> tuple:
        """Get subject by name"""
        query = "SELECT subject_id, subject_name FROM Subject WHERE subject_name = %s"
        return fetch_one(query, (subject_name,))

    @staticmethod
    def update_subject(subject_id: int, subject_name: str) -> bool:
        """Update existing subject"""
        query = "UPDATE Subject SET subject_name = %s WHERE subject_id = %s"
        return execute_query(query, (subject_name, subject_id))

    @staticmethod
    def delete_subject(subject_id: int) -> bool:
        """Delete subject and all associated marks"""
        query = "DELETE FROM Subject WHERE subject_id = %s"
        return execute_query(query, (subject_id,))

    @staticmethod
    def search_subjects(search_term: str = "") -> list:
        """Search subjects by name"""
        query = """
        SELECT subject_id, subject_name, created_at 
        FROM Subject 
        WHERE subject_name LIKE %s OR %s = ''
        ORDER BY subject_name
        """
        search_pattern = f"%{search_term}%"
        return fetch_all(query, (search_pattern, search_term))

    @staticmethod
    def get_subjects_dataframe() -> pd.DataFrame:
        """Get subjects as pandas DataFrame"""
        subjects = Subject.get_all_subjects()
        if subjects:
            df = pd.DataFrame(subjects, columns=['ID', 'Subject Name', 'Created'])
            df['Created'] = pd.to_datetime(df['Created']).dt.date
            return df
        return pd.DataFrame()

    @staticmethod
    def validate_subject_data(subject_name: str) -> tuple:
        """Validate subject data before insertion/update"""
        errors = []

        # Subject name validation
        if not subject_name or len(subject_name.strip()) < 2:
            errors.append("Subject name must be at least 2 characters long")
        elif len(subject_name) > 50:
            errors.append("Subject name cannot exceed 50 characters")

        # Check for duplicate subject name (case-insensitive)
        existing_subject = Subject.get_subject_by_name(subject_name.strip())
        if existing_subject:
            errors.append("Subject already exists")

        return len(errors) == 0, errors

    @staticmethod
    def get_subject_statistics() -> dict:
        """Get statistics about subjects"""
        stats = {}

        # Total subjects
        total_query = "SELECT COUNT(*) FROM Subject"
        result = fetch_one(total_query)
        stats['total_subjects'] = result[0] if result else 0

        # Subjects with marks
        with_marks_query = """
        SELECT COUNT(DISTINCT s.subject_id) 
        FROM Subject s 
        JOIN Marks m ON s.subject_id = m.subject_id
        """
        result = fetch_one(with_marks_query)
        stats['subjects_with_marks'] = result[0] if result else 0

        # Most popular subject (by number of marks entries)
        popular_query = """
        SELECT s.subject_name, COUNT(m.mark_id) as mark_count
        FROM Subject s 
        LEFT JOIN Marks m ON s.subject_id = m.subject_id
        GROUP BY s.subject_id, s.subject_name
        ORDER BY mark_count DESC
        LIMIT 1
        """
        result = fetch_one(popular_query)
        if result and result[1] > 0:
            stats['most_popular_subject'] = result[0]
            stats['most_popular_count'] = result[1]
        else:
            stats['most_popular_subject'] = "N/A"
            stats['most_popular_count'] = 0

        return stats

def display_subjects_table(subjects_data: list, show_actions: bool = True) -> None:
    """Display subjects in a formatted table"""
    if not subjects_data:
        st.info("No subjects found")
        return

    df = pd.DataFrame(subjects_data, columns=['ID', 'Subject Name', 'Created'])

    # Format dates
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d')

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("Subject ID", width="small"),
            "Subject Name": st.column_config.TextColumn("Subject", width="medium"),
            "Created": st.column_config.DateColumn("Created On", width="medium")
        }
    )

    st.info(f"Total subjects: {len(subjects_data)}")

def subject_form(subject_data=None, form_type="Add"):
    """Reusable subject form for add/edit operations"""

    # Initialize default values
    default_name = subject_data[1] if subject_data else ""

    with st.form(f"subject_{form_type.lower()}_form"):
        subject_name = st.text_input(
            "Subject Name *", 
            value=default_name, 
            max_chars=50,
            help="Enter the name of the subject (e.g., Mathematics, Physics, etc.)"
        )

        submitted = st.form_submit_button(f"{form_type} Subject", type="primary")

        if submitted:
            # Validate input
            if form_type == "Update" and subject_data:
                # For updates, check duplicates excluding current subject
                errors = []
                if not subject_name or len(subject_name.strip()) < 2:
                    errors.append("Subject name must be at least 2 characters long")
                elif len(subject_name) > 50:
                    errors.append("Subject name cannot exceed 50 characters")
                else:
                    # Check for duplicate (excluding current subject)
                    existing_subject = Subject.get_subject_by_name(subject_name.strip())
                    if existing_subject and existing_subject[0] != subject_data[0]:
                        errors.append("Subject already exists")

                is_valid = len(errors) == 0
            else:
                is_valid, errors = Subject.validate_subject_data(subject_name)

            if is_valid:
                if form_type == "Add":
                    success = Subject.add_subject(subject_name.strip())
                    if success:
                        st.success(f"✅ Subject '{subject_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add subject")

                elif form_type == "Update" and subject_data:
                    success = Subject.update_subject(subject_data[0], subject_name.strip())
                    if success:
                        st.success(f"✅ Subject '{subject_name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update subject")
            else:
                for error in errors:
                    st.error(f"❌ {error}")

def subject_selector() -> tuple:
    """Subject selector widget for forms"""
    subjects = Subject.get_all_subjects()
    if not subjects:
        st.warning("No subjects found. Please add subjects first.")
        return None, None

    subject_options = {f"{subj[1]}": subj[0] for subj in subjects}
    selected_name = st.selectbox(
        "Select Subject *", 
        options=list(subject_options.keys()),
        help="Choose a subject from the available options"
    )

    return subject_options.get(selected_name), selected_name

def display_subject_statistics():
    """Display subject-related statistics"""
    stats = Subject.get_subject_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Subjects", stats['total_subjects'])

    with col2:
        st.metric("Subjects with Marks", stats['subjects_with_marks'])

    with col3:
        st.metric(
            "Most Popular Subject", 
            stats['most_popular_subject'],
            f"{stats['most_popular_count']} marks"
        )
