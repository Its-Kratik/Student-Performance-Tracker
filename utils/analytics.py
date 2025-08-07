"""
Analytics utilities for performance calculations and insights (SQLite version)
"""
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple
from db.connection import fetch_all, fetch_one  # ✅ Correct SQLite import
from models.marks import Marks

class PerformanceAnalytics:
    """Class for advanced performance analytics"""

    @staticmethod
    def get_grade_distribution(class_name: str = None, section: str = None) -> Dict:
        """Get distribution of grades across students"""
        # Build query based on filters
        conditions = []
        params = []

        if class_name:
            conditions.append("s.class = ?")  # ✅ SQLite placeholder
            params.append(class_name)

        if section:
            conditions.append("s.section = ?")  # ✅ SQLite placeholder
            params.append(section)

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = f"WHERE {where_clause}"

        query = f"""
        SELECT s.student_id, s.name, s.class, s.section,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max
        FROM Student s
        JOIN Marks m ON s.student_id = m.student_id
        {where_clause}
        GROUP BY s.student_id, s.name, s.class, s.section
        HAVING total_max > 0
        """

        results = fetch_all(query, tuple(params))

        grade_counts = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'F': 0}
        student_grades = []

        for result in results:
            percentage = Marks.calculate_percentage(result[4], result[5])
            grade = Marks.calculate_grade(percentage)
            grade_counts[grade] += 1
            student_grades.append({
                'student_id': result[0],
                'name': result[1],
                'class': result[2],
                'section': result[3],
                'percentage': percentage,
                'grade': grade
            })

        return {
            'grade_counts': grade_counts,
            'student_grades': student_grades,
            'total_students': len(student_grades)
        }

    @staticmethod
    def get_subject_performance_comparison() -> Dict:
        """Compare performance across all subjects"""
        query = """
        SELECT sub.subject_name,
               COUNT(m.mark_id) as total_assessments,
               AVG(m.marks_obtained) as avg_marks,
               AVG((m.marks_obtained * 100.0) / m.max_marks) as avg_percentage,
               MAX(m.marks_obtained) as highest_marks,
               MIN(m.marks_obtained) as lowest_marks
        FROM Subject sub
        LEFT JOIN Marks m ON sub.subject_id = m.subject_id
        GROUP BY sub.subject_id, sub.subject_name
        HAVING total_assessments > 0
        ORDER BY avg_percentage DESC
        """

        results = fetch_all(query)

        subjects_data = []
        for result in results:
            subjects_data.append({
                'subject': result[0],
                'total_assessments': result[1],
                'avg_marks': round(result[2], 2),
                'avg_percentage': round(result[3], 2),
                'highest_marks': result[4],
                'lowest_marks': result[5],
                'grade': Marks.calculate_grade(result[3])
            })

        return subjects_data

    @staticmethod
    def get_class_wise_performance() -> List[Dict]:
        """Get performance summary for each class-section combination"""
        query = """
        SELECT s.class, s.section,
               COUNT(DISTINCT s.student_id) as total_students,
               COUNT(m.mark_id) as total_assessments,
               AVG((m.marks_obtained * 100.0) / m.max_marks) as avg_percentage,
               SUM(CASE WHEN (m.marks_obtained * 100.0) / m.max_marks >= 40 THEN 1 ELSE 0 END) as pass_count,
               COUNT(DISTINCT m.student_id) as students_with_marks
        FROM Student s
        LEFT JOIN Marks m ON s.student_id = m.student_id
        GROUP BY s.class, s.section
        ORDER BY s.class, s.section
        """

        results = fetch_all(query)

        class_data = []
        for result in results:
            students_with_marks = result[6] if result[6] else 0
            pass_percentage = 0

            if students_with_marks > 0:
                pass_percentage = (result[5] / students_with_marks) * 100

            class_data.append({
                'class': result[0],
                'section': result[1],
                'total_students': result[2],
                'students_with_marks': students_with_marks,
                'total_assessments': result[3] if result[3] else 0,
                'avg_percentage': round(result[4], 2) if result[4] else 0,
                'pass_count': result[5] if result[5] else 0,
                'pass_percentage': round(pass_percentage, 2)
            })

        return class_data

    @staticmethod
    def get_top_performers(limit: int = 10, class_name: str = None) -> List[Dict]:
        """Get top performing students"""
        conditions = []
        params = []

        if class_name:
            conditions.append("s.class = ?")  # ✅ SQLite placeholder
            params.append(class_name)

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = f"AND {where_clause}"

        query = f"""
        SELECT s.student_id, s.name, s.class, s.section,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max,
               COUNT(m.mark_id) as total_subjects,
               (SUM(m.marks_obtained) * 100.0) / SUM(m.max_marks) as percentage
        FROM Student s
        JOIN Marks m ON s.student_id = m.student_id
        WHERE 1=1 {where_clause}
        GROUP BY s.student_id, s.name, s.class, s.section
        HAVING total_max > 0
        ORDER BY percentage DESC
        LIMIT ?
        """

        params.append(limit)
        results = fetch_all(query, tuple(params))

        top_performers = []
        for i, result in enumerate(results):
            percentage = result[7]
            top_performers.append({
                'rank': i + 1,
                'student_id': result[0],
                'name': result[1],
                'class': result[2],
                'section': result[3],
                'total_obtained': result[4],
                'total_max': result[5],
                'total_subjects': result[6],
                'percentage': round(percentage, 2),
                'grade': Marks.calculate_grade(percentage)
            })

        return top_performers

    @staticmethod
    def get_failing_students(threshold: float = 40.0) -> List[Dict]:
        """Get students who are failing (below threshold)"""
        query = """
        SELECT s.student_id, s.name, s.class, s.section,
               SUM(m.marks_obtained) as total_obtained,
               SUM(m.max_marks) as total_max,
               COUNT(m.mark_id) as total_subjects,
               (SUM(m.marks_obtained) * 100.0) / SUM(m.max_marks) as percentage
        FROM Student s
        JOIN Marks m ON s.student_id = m.student_id
        GROUP BY s.student_id, s.name, s.class, s.section
        HAVING percentage < ?
        ORDER BY percentage ASC
        """

        results = fetch_all(query, (threshold,))

        failing_students = []
        for result in results:
            percentage = result[7]
            failing_students.append({
                'student_id': result[0],
                'name': result[1],
                'class': result[2],
                'section': result[3],
                'total_obtained': result[4],
                'total_max': result[5],
                'total_subjects': result[6],
                'percentage': round(percentage, 2),
                'grade': Marks.calculate_grade(percentage)
            })

        return failing_students

    @staticmethod
    def get_improvement_trends(student_id: int) -> Dict:
        """Analyze improvement trends for a student over time"""
        query = """
        SELECT sub.subject_name, m.marks_obtained, m.max_marks, m.assessment_date,
               (m.marks_obtained * 100.0) / m.max_marks as percentage
        FROM Marks m
        JOIN Subject sub ON m.subject_id = sub.subject_id
        WHERE m.student_id = ?
        ORDER BY m.assessment_date DESC
        """

        results = fetch_all(query, (student_id,))

        if not results:
            return {'has_data': False}

        # Group by subject
        subject_trends = {}
        for result in results:
            subject = result[0]
            if subject not in subject_trends:
                subject_trends[subject] = []

            subject_trends[subject].append({
                'marks_obtained': result[1],
                'max_marks': result[2],
                'date': result[3],
                'percentage': round(result[4], 2)
            })

        return {
            'has_data': True,
            'subject_trends': subject_trends,
            'total_assessments': len(results)
        }

    @staticmethod
    def get_overall_statistics() -> Dict:
        """Get overall system statistics"""
        # Total students
        total_students_query = "SELECT COUNT(*) FROM Student"
        total_students = fetch_one(total_students_query)[0]

        # Total subjects
        total_subjects_query = "SELECT COUNT(*) FROM Subject"
        total_subjects = fetch_one(total_subjects_query)[0]

        # Total assessments
        total_assessments_query = "SELECT COUNT(*) FROM Marks"
        total_assessments = fetch_one(total_assessments_query)[0]

        # Students with marks
        students_with_marks_query = "SELECT COUNT(DISTINCT student_id) FROM Marks"
        students_with_marks = fetch_one(students_with_marks_query)[0]

        # Overall average
        overall_avg_query = "SELECT AVG((marks_obtained * 100.0) / max_marks) FROM Marks"
        overall_avg = fetch_one(overall_avg_query)[0]
        overall_avg = round(overall_avg, 2) if overall_avg else 0

        # Pass rate
        pass_rate_query = """
        SELECT 
            (SUM(CASE WHEN (marks_obtained * 100.0) / max_marks >= 40 THEN 1 ELSE 0 END) * 100.0) / COUNT(*)
        FROM Marks
        """
        pass_rate = fetch_one(pass_rate_query)[0]
        pass_rate = round(pass_rate, 2) if pass_rate else 0

        return {
            'total_students': total_students,
            'total_subjects': total_subjects,
            'total_assessments': total_assessments,
            'students_with_marks': students_with_marks,
            'overall_average': overall_avg,
            'pass_rate': pass_rate
        }

def display_analytics_metrics(analytics_data: Dict) -> None:
    """Display analytics in metric format"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Students",
            analytics_data.get('total_students', 0)
        )

    with col2:
        st.metric(
            "Average Performance",
            f"{analytics_data.get('overall_average', 0)}%"
        )

    with col3:
        st.metric(
            "Pass Rate",
            f"{analytics_data.get('pass_rate', 0)}%"
        )

    with col4:
        st.metric(
            "Total Assessments",
            analytics_data.get('total_assessments', 0)
        )
