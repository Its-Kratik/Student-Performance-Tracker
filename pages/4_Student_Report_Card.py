"""
Student Report Card Page - Individual student performance reports (SQLite version)
"""
import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.marks import Marks

st.set_page_config(
    page_title="Student Report Cards",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Student Report Cards")
st.markdown("Generate detailed performance reports for individual students")

# Student selection
students = Student.get_all_students()

if not students:
    st.warning("⚠️ No students found. Please add students first.")
    if st.button("Go to Manage Students"):
        st.switch_page("pages/1_Manage_Students.py")
    st.stop()

# Create student options
student_options = {f"{student[1]} - Class {student[2]}-{student[3]} (ID: {student[0]})": student[0] 
                  for student in students}

# Sidebar for student selection
with st.sidebar:
    st.subheader("Select Student")

    selected_student_key = st.selectbox(
        "Choose student:",
        options=list(student_options.keys()),
        help="Select a student to view their report card"
    )

    student_id = student_options.get(selected_student_key)

    if student_id:
        # Get student data
        student_data = Student.get_student_by_id(student_id)

        if student_data:
            st.info(f"**Selected:** {student_data[1]}")
            st.write(f"**Class:** {student_data[2]}-{student_data[3]}")
            st.write(f"**DOB:** {student_data[4]}")

# Main content
if student_id:
    # Get comprehensive student data
    with st.spinner("Generating report card..."):
        try:
            student_summary = Marks.get_student_summary(student_id)

            if student_summary['total_subjects'] == 0:
                st.warning("⚠️ No marks found for this student. Please enter marks first.")
                if st.button("Go to Enter Marks"):
                    st.switch_page("pages/3_Enter_Update_Marks.py")
                st.stop()

            # Header section
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"## 🎓 {student_summary['student_name']}")
                st.markdown(f"**Class:** {student_data[2]}-{student_data[3]} | **Student ID:** {student_id}")

            with col2:
                st.metric("Overall Grade", student_summary['overall_grade'])
                status_color = "🟢" if student_summary['pass_fail_status'] == "Pass" else "🔴"
                st.markdown(f"**Status:** {status_color} {student_summary['pass_fail_status']}")

            with col3:
                st.metric("Overall Percentage", f"{student_summary['overall_percentage']}%")
                st.metric("Total Subjects", student_summary['total_subjects'])

            # Performance Summary Cards
            st.markdown("### 📊 Performance Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Marks Obtained",
                    student_summary['total_marks_obtained']
                )

            with col2:
                st.metric(
                    "Total Possible Marks",
                    student_summary['total_max_marks']
                )

            with col3:
                # Calculate pass/fail per subject
                passing_subjects = sum(1 for subject in student_summary['subject_details'] 
                                     if subject['percentage'] >= 40)
                st.metric(
                    "Passing Subjects",
                    f"{passing_subjects}/{student_summary['total_subjects']}"
                )

            with col4:
                # Calculate average percentage
                avg_percentage = student_summary['overall_percentage']
                st.metric(
                    "Average Percentage",
                    f"{avg_percentage:.1f}%"
                )

            # Subject-wise Performance Table
            st.markdown("### 📚 Subject-wise Performance")

            # Prepare data for display
            subject_data = []
            for subject in student_summary['subject_details']:
                status = "Pass" if subject['percentage'] >= 40 else "Fail"

                subject_data.append({
                    'Subject': subject['subject'],
                    'Marks': f"{subject['marks_obtained']}/{subject['max_marks']}",
                    'Percentage': f"{subject['percentage']:.1f}%",
                    'Grade': subject['grade'],
                    'Status': status,
                    'Date': subject['assessment_date'],
                    'Type': subject['assessment_type']
                })

            # Display table
            df = pd.DataFrame(subject_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Subject": st.column_config.TextColumn("Subject", width="medium"),
                    "Marks": st.column_config.TextColumn("Marks", width="small"),
                    "Percentage": st.column_config.TextColumn("%", width="small"),
                    "Grade": st.column_config.TextColumn("Grade", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Date": st.column_config.DateColumn("Date", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="small")
                }
            )

            # Performance Analysis
            st.markdown("### 📈 Performance Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🎯 Strengths")

                # Find best performing subjects
                best_subjects = sorted(student_summary['subject_details'], 
                                     key=lambda x: x['percentage'], reverse=True)[:3]

                for i, subject in enumerate(best_subjects, 1):
                    st.write(f"{i}. **{subject['subject']}**: {subject['percentage']:.1f}% ({subject['grade']})")

                # Performance insights
                if student_summary['overall_percentage'] >= 80:
                    st.success("🌟 Excellent overall performance!")
                elif student_summary['overall_percentage'] >= 60:
                    st.info("👍 Good performance with room for improvement")
                elif student_summary['overall_percentage'] >= 40:
                    st.warning("⚠️ Average performance, needs focused attention")
                else:
                    st.error("❌ Below average performance, requires immediate attention")

            with col2:
                st.markdown("#### 🎯 Areas for Improvement")

                # Find subjects needing improvement
                weak_subjects = [subject for subject in student_summary['subject_details'] 
                               if subject['percentage'] < 60]

                if weak_subjects:
                    weak_subjects_sorted = sorted(weak_subjects, key=lambda x: x['percentage'])

                    for i, subject in enumerate(weak_subjects_sorted[:3], 1):
                        st.write(f"{i}. **{subject['subject']}**: {subject['percentage']:.1f}% ({subject['grade']})")

                    # Recommendations
                    st.markdown("**Recommendations:**")
                    for subject in weak_subjects_sorted[:2]:
                        if subject['percentage'] < 40:
                            st.write(f"• Focus on {subject['subject']} - currently failing")
                        else:
                            st.write(f"• Strengthen {subject['subject']} concepts")
                else:
                    st.success("🎉 No subjects need immediate attention!")

            # Grade Analysis
            st.markdown("### 📊 Grade Distribution")

            grade_counts = {}
            for subject in student_summary['subject_details']:
                grade = subject['grade']
                grade_counts[grade] = grade_counts.get(grade, 0) + 1

            # Display grade distribution
            col1, col2, col3, col4 = st.columns(4)

            grade_cols = [col1, col2, col3, col4]
            grade_names = ['A+/A', 'B+/B', 'C+/C', 'F']
            grade_groups = [
                ['A+', 'A'],
                ['B+', 'B'], 
                ['C+', 'C'],
                ['F']
            ]

            for i, (col, name, grades) in enumerate(zip(grade_cols, grade_names, grade_groups)):
                count = sum(grade_counts.get(grade, 0) for grade in grades)
                with col:
                    st.metric(name, count)

            # Export Section
            st.markdown("---")
            st.markdown("### 📥 Export Report Card")

            col1, col2 = st.columns(2)

            with col1:
                # CSV Export
                if st.button("📊 Export to CSV", use_container_width=True):
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"report_card_{student_summary['student_name'].replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col2:
                st.info("PDF export feature coming soon!")

        except Exception as e:
            st.error(f"Error generating report card: {str(e)}")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Dashboard"):
        st.switch_page("app.py")

with col2:
    if st.button("📝 Enter Marks"):
        st.switch_page("pages/3_Enter_Update_Marks.py")

with col3:
    if st.button("📊 Class Analytics"):
        st.switch_page("pages/5_Class_Analytics.py")
