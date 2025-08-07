"""
Marks Model - CRUD operations and calculations for Marks entity (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import List, Dict, Optional
from db.connection import execute_query, fetch_all, fetch_one

class Marks:
    def __init__(self, mark_id=None, student_id=None, subject_id=None,
                 marks_obtained=None, max_marks=100, assessment_date=None, assessment_type="Assignment"):
        self.mark_id = mark_id
        self.student_id = student_id
        self.subject_id = subject_id
        self.marks_obtained = marks_obtained
        self.max_marks = max_marks
        self.assessment_date = assessment_date
        self.assessment_type = assessment_type

    @staticmethod
    def add_marks(student_id: int, subject_id: int, marks_obtained: int,
                  max_marks: int = 100, assessment_date: date = None,
                  assessment_type: str = "Assignment") -> bool:
        """Add new marks entry to database"""
        if assessment_date is None:
            assessment_date = date.today()
        
        query = """
        INSERT INTO Marks (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (student_id, subject_id, marks_obtained, max_marks, assessment_date, assessment_type))

    @staticmethod
    def get_all_marks() -> list:
        """Get all marks with student and subject names"""
        query = """
        SELECT m.mark_id, s.name, sub.subject_name, m.marks_obtained, m.max_marks,
               m.assessment_date, m.assessment_type, m.created_at,
               m.student_id, m.subject_id
        FROM Marks m
        JOIN Student s ON m.student_id = s.student_id
        JOIN Subject sub ON m.subject_id = sub.subject_id
        ORDER BY m.assessment_date DESC, s.name, sub.subject_name
        """
        return fetch_all(query)

    @staticmethod
    def get_student_marks(student_id: int) -> list:
        """Get all marks for a specific student"""
        query = """
        SELECT m.mark_id, sub.subject_name, m.marks_obtained, m.max_marks,
               m.assessment_date, m.assessment_type, s.name,
               m.student_id, m.subject_id
        FROM Marks m
        JOIN Subject sub ON m.subject_id = sub.subject_id
        JOIN Student s ON m.student_id = s.student_id
        WHERE m.student_id = ?
        ORDER BY sub.subject_name, m.assessment_date DESC
        """
        return fetch_all(query, (student_id,))

    @staticmethod
    def get_subject_marks(subject_id: int) -> list:
        """Get all marks for a specific subject"""
        query = """
        SELECT m.mark_id, s.name, m.marks_obtained, m.max_marks,
               m.assessment_date, m.assessment_type, sub.subject_name,
               m.student_id, m.subject_id
        FROM Marks m
        JOIN Student s ON m.student_id = s.student_id
        JOIN Subject sub ON m.subject_id = sub.subject_id
        WHERE m.subject_id = ?
        ORDER BY s.name, m.assessment_date DESC
        """
        return fetch_all(query, (subject_id,))

    @staticmethod
    def update_marks(mark_id: int, marks_obtained: int, max_marks: int = 100,
                     assessment_date: date = None, assessment_type: str = "Assignment") -> bool:
        """Update existing marks entry"""
        if assessment_date is None:
            assessment_date = date.today()
        
        query = """
        UPDATE Marks
        SET marks_obtained = ?, max_marks = ?, assessment_date = ?, assessment_type = ?
        WHERE mark_id = ?
        """
        return execute_query(query, (marks_obtained, max_marks, assessment_date, assessment_type, mark_id))

    @staticmethod
    def delete_marks(mark_id: int) -> bool:
        """Delete marks entry"""
        query = "DELETE FROM Marks WHERE mark_id = ?"
        return execute_query(query, (mark_id,))

    @staticmethod
    def calculate_grade(percentage: float) -> str:
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C+"
        elif percentage >= 40:
            return "C"
        else:
            return "F"

    @staticmethod
    def calculate_percentage(marks_obtained: int, max_marks: int) -> float:
        """Calculate percentage from marks"""
        if max_marks == 0:
            return 0.0
        return round((marks_obtained / max_marks) * 100, 2)

    @staticmethod
    def get_student_summary(student_id: int) -> dict:
        """Get comprehensive summary for a student"""
        marks_data = Marks.get_student_marks(student_id)
        
        if not marks_data:
            return {
                'student_name': '',
                'total_subjects': 0,
                'total_marks_obtained': 0,
                'total_max_marks': 0,
                'overall_percentage': 0.0,
                'overall_grade': 'N/A',
                'subject_details': [],
                'pass_fail_status': 'No Data'
            }

        student_name = marks_data[0][6]  # Student name from query
        total_obtained = sum(mark[2] for mark in marks_data)  # marks_obtained
        total_max = sum(mark[3] for mark in marks_data)  # max_marks
        overall_percentage = Marks.calculate_percentage(total_obtained, total_max)
        overall_grade = Marks.calculate_grade(overall_percentage)

        # Subject-wise details
        subject_details = []
        for mark in marks_data:
            subject_name = mark[1]
            marks_obtained = mark[2]
            max_marks = mark[3]
            percentage = Marks.calculate_percentage(marks_obtained, max_marks)
            grade = Marks.calculate_grade(percentage)
            
            subject_details.append({
                'subject': subject_name,
                'marks_obtained': marks_obtained,
                'max_marks': max_marks,
                'percentage': percentage,
                'grade': grade,
                'assessment_date': mark[4],
                'assessment_type': mark[5]
            })

        # Determine pass/fail status (assuming 40% is pass threshold)
        pass_fail_status = "Pass" if overall_percentage >= 40 else "Fail"

        return {
            'student_name': student_name,
            'total_subjects': len(marks_data),
            'total_marks_obtained': total_obtained,
            'total_max_marks': total_max,
            'overall_percentage': overall_percentage,
            'overall_grade': overall_grade,
            'subject_details': subject_details,
            'pass_fail_status': pass_fail_status
        }

    @staticmethod
    def get_class_analytics(class_name: str, section: str = None) -> dict:
        """Get analytics for a class/section"""
        # Build query based on whether section is provided
        if section:
            student_condition = "s.class = ? AND s.section = ?"
            params = (class_name, section)
        else:
            student_condition = "s.class = ?"
            params = (class_name,)

        query = f"""
        SELECT s.student_id, s.name, s.class, s.section,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max,
               COUNT(m.mark_id) as total_subjects
        FROM Student s
        LEFT JOIN Marks m ON s.student_id = m.student_id
        WHERE {student_condition}
        GROUP BY s.student_id, s.name, s.class, s.section
        HAVING total_subjects > 0
        ORDER BY total_obtained DESC
        """

        results = fetch_all(query, params)

        if not results:
            return {
                'class_name': class_name,
                'section': section,
                'total_students': 0,
                'students_with_marks': 0,
                'class_average': 0.0,
                'pass_count': 0,
                'fail_count': 0,
                'pass_percentage': 0.0,
                'top_performers': [],
                'student_summaries': []
            }

        # Calculate statistics
        student_summaries = []
        total_percentage_sum = 0
        pass_count = 0
        
        for result in results:
            percentage = Marks.calculate_percentage(result[4], result[5])
            grade = Marks.calculate_grade(percentage)
            
            student_summaries.append({
                'student_id': result[0],
                'name': result[1],
                'total_obtained': result[4],
                'total_max': result[5],
                'percentage': percentage,
                'grade': grade,
                'subjects_count': result[6]
            })
            
            total_percentage_sum += percentage
            if percentage >= 40:  # Pass threshold
                pass_count += 1

        students_with_marks = len(student_summaries)
        class_average = total_percentage_sum / students_with_marks if students_with_marks > 0 else 0
        fail_count = students_with_marks - pass_count
        pass_percentage = (pass_count / students_with_marks * 100) if students_with_marks > 0 else 0

        # Top 3 performers
        top_performers = sorted(student_summaries, key=lambda x: x['percentage'], reverse=True)[:3]

        return {
            'class_name': class_name,
            'section': section,
            'total_students': students_with_marks,
            'students_with_marks': students_with_marks,
            'class_average': round(class_average, 2),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_percentage': round(pass_percentage, 2),
            'top_performers': top_performers,
            'student_summaries': student_summaries
        }

    @staticmethod
    def validate_marks_data(marks_obtained: int, max_marks: int, assessment_date: date = None) -> tuple:
        """Validate marks data before insertion/update"""
        errors = []

        # Marks validation
        if marks_obtained < 0:
            errors.append("Marks obtained cannot be negative")
        elif marks_obtained > max_marks:
            errors.append("Marks obtained cannot exceed maximum marks")

        # Max marks validation
        if max_marks <= 0:
            errors.append("Maximum marks must be greater than 0")
        elif max_marks > 1000:  # Reasonable upper limit
            errors.append("Maximum marks seems too high (limit: 1000)")

        # Date validation
        if assessment_date and assessment_date > date.today():
            errors.append("Assessment date cannot be in the future")

        return len(errors) == 0, errors


def display_marks_table(marks_data: list, show_calculations: bool = True) -> None:
    """Display marks in a formatted table with calculations"""
    if not marks_data:
        st.info("No marks found")
        return

    # Prepare data for display
    display_data = []
    for mark in marks_data:
        percentage = Marks.calculate_percentage(mark[3], mark[4])
        grade = Marks.calculate_grade(percentage)
        
        display_data.append([
            mark[1],  # Student/Subject name
            mark[2] if len(mark) > 8 else mark[1],  # Subject/Student name
            f"{mark[3]}/{mark[4]}",  # Marks
            f"{percentage}%",  # Percentage
            grade,  # Grade
            mark[5].strftime('%Y-%m-%d') if isinstance(mark[5], date) else mark[5],  # Date
            mark[6]  # Assessment type
        ])

    df = pd.DataFrame(display_data, columns=[
        'Student', 'Subject', 'Marks', 'Percentage', 'Grade', 'Date', 'Type'
    ])

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Student": st.column_config.TextColumn("Student", width="medium"),
            "Subject": st.column_config.TextColumn("Subject", width="medium"),
            "Marks": st.column_config.TextColumn("Marks", width="small"),
            "Percentage": st.column_config.TextColumn("Percentage", width="small"),
            "Grade": st.column_config.TextColumn("Grade", width="small"),
            "Date": st.column_config.TextColumn("Date", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="small")
        }
    )

    st.info(f"Total records: {len(marks_data)}")
