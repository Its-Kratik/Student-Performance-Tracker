"""
Class Analytics Page - Class and section-wise performance analysis
"""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.marks import Marks
from utils.analytics import PerformanceAnalytics, display_analytics_metrics
from utils.export import export_class_summary
from utils.ui_components import create_grade_badge, create_status_badge

st.set_page_config(
    page_title="Class Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Class Analytics & Performance")
st.markdown("Comprehensive analysis of class and section performance")

# Get available classes and sections
students = Student.get_all_students()

if not students:
    st.warning("⚠️ No students found. Please add students first.")
    if st.button("Go to Manage Students"):
        st.switch_page("pages/1_Manage_Students.py")
    st.stop()

# Get unique classes and sections
unique_classes = Student.get_unique_classes()
unique_sections = Student.get_unique_sections()

# Sidebar for class/section selection
with st.sidebar:
    st.subheader("Class Selection")

    # Class filter
    selected_class = st.selectbox(
        "Select Class:",
        options=["All"] + unique_classes,
        help="Choose a specific class or view all classes"
    )

    # Section filter
    if selected_class != "All":
        available_sections = []
        for student in students:
            if student[2] == selected_class:
                if student[3] not in available_sections:
                    available_sections.append(student[3])
        available_sections.sort()

        selected_section = st.selectbox(
            "Select Section:",
            options=["All"] + available_sections,
            help="Choose a specific section within the class"
        )
    else:
        selected_section = "All"

    if selected_class != "All":
        st.info(f"**Analyzing:** Class {selected_class}" + 
               (f"-{selected_section}" if selected_section != "All" else ""))

# Main analytics content
col1, col2 = st.columns([2, 1])

with col1:
    if selected_class != "All":
        # Specific class analysis
        st.subheader(f"📈 Class {selected_class}" + 
                    (f" Section {selected_section}" if selected_section != "All" else "") + 
                    " Performance")

        # Get class analytics
        with st.spinner("Analyzing class performance..."):
            try:
                class_analytics = Marks.get_class_analytics(
                    selected_class, 
                    selected_section if selected_section != "All" else None
                )

                if class_analytics['total_students'] == 0:
                    st.warning("⚠️ No marks data found for this class. Please enter marks first.")
                    if st.button("Go to Enter Marks"):
                        st.switch_page("pages/3_Enter_Update_Marks.py")
                else:
                    # Performance metrics
                    col1_1, col1_2, col1_3, col1_4 = st.columns(4)

                    with col1_1:
                        st.metric("Total Students", class_analytics['total_students'])

                    with col1_2:
                        st.metric("Class Average", f"{class_analytics['class_average']}%")

                    with col1_3:
                        st.metric("Pass Rate", f"{class_analytics['pass_percentage']}%")

                    with col1_4:
                        pass_fail_ratio = f"{class_analytics['pass_count']}/{class_analytics['fail_count']}"
                        st.metric("Pass/Fail", pass_fail_ratio)

                    # Top performers section
                    st.markdown("### 🏆 Top Performers")

                    if class_analytics['top_performers']:
                        top_performers_data = []
                        for i, student in enumerate(class_analytics['top_performers'], 1):
                            top_performers_data.append({
                                'Rank': i,
                                'Name': student['name'],
                                'Percentage': f"{student['percentage']}%",
                                'Grade': student['grade'],
                                'Subjects': student['subjects_count']
                            })

                        df_top = pd.DataFrame(top_performers_data)
                        st.dataframe(
                            df_top,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Rank": st.column_config.NumberColumn("Rank", width="small"),
                                "Name": st.column_config.TextColumn("Student Name", width="medium"),
                                "Percentage": st.column_config.TextColumn("Percentage", width="small"),
                                "Grade": st.column_config.TextColumn("Grade", width="small"),
                                "Subjects": st.column_config.NumberColumn("Subjects", width="small")
                            }
                        )

                    # All students performance table
                    st.markdown("### 📋 All Students Performance")

                    all_students_data = []
                    for student in class_analytics['student_summaries']:
                        status = "Pass" if student['percentage'] >= 40 else "Fail"
                        all_students_data.append({
                            'Name': student['name'],
                            'Total Marks': f"{student['total_obtained']}/{student['total_max']}",
                            'Percentage': f"{student['percentage']:.1f}%",
                            'Grade': student['grade'],
                            'Status': status,
                            'Subjects': student['subjects_count']
                        })

                    df_all = pd.DataFrame(all_students_data)
                    st.dataframe(
                        df_all,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Name": st.column_config.TextColumn("Student Name", width="medium"),
                            "Total Marks": st.column_config.TextColumn("Marks", width="medium"),
                            "Percentage": st.column_config.TextColumn("Percentage", width="small"),
                            "Grade": st.column_config.TextColumn("Grade", width="small"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                            "Subjects": st.column_config.NumberColumn("Subjects", width="small")
                        }
                    )

                    # Grade distribution
                    st.markdown("### 📊 Grade Distribution")

                    grade_counts = {}
                    for student in class_analytics['student_summaries']:
                        grade = student['grade']
                        grade_counts[grade] = grade_counts.get(grade, 0) + 1

                    col1_1, col1_2, col1_3, col1_4 = st.columns(4)

                    with col1_1:
                        a_count = grade_counts.get('A+', 0) + grade_counts.get('A', 0)
                        st.metric("A Grades", a_count, f"{(a_count/class_analytics['total_students']*100):.1f}%")

                    with col1_2:
                        b_count = grade_counts.get('B+', 0) + grade_counts.get('B', 0)
                        st.metric("B Grades", b_count, f"{(b_count/class_analytics['total_students']*100):.1f}%")

                    with col1_3:
                        c_count = grade_counts.get('C+', 0) + grade_counts.get('C', 0)
                        st.metric("C Grades", c_count, f"{(c_count/class_analytics['total_students']*100):.1f}%")

                    with col1_4:
                        f_count = grade_counts.get('F', 0)
                        st.metric("F Grades", f_count, f"{(f_count/class_analytics['total_students']*100):.1f}%")

                    # Performance insights
                    st.markdown("### 💡 Performance Insights")

                    insights = []

                    # Class average insight
                    if class_analytics['class_average'] >= 80:
                        insights.append("🌟 **Excellent class performance** - Average above 80%")
                    elif class_analytics['class_average'] >= 60:
                        insights.append("👍 **Good class performance** - Average above 60%")
                    elif class_analytics['class_average'] >= 40:
                        insights.append("⚠️ **Average class performance** - Needs improvement")
                    else:
                        insights.append("❌ **Below average class performance** - Requires immediate attention")

                    # Pass rate insight
                    if class_analytics['pass_percentage'] >= 90:
                        insights.append("✅ **Excellent pass rate** - 90%+ students passing")
                    elif class_analytics['pass_percentage'] >= 75:
                        insights.append("📈 **Good pass rate** - Most students performing well")
                    elif class_analytics['pass_percentage'] >= 50:
                        insights.append("⚠️ **Moderate pass rate** - Some students need support")
                    else:
                        insights.append("🚨 **Low pass rate** - Many students failing, intervention needed")

                    # Grade distribution insight
                    if (grade_counts.get('A+', 0) + grade_counts.get('A', 0)) >= class_analytics['total_students'] * 0.3:
                        insights.append("🎯 **High achievers present** - 30%+ students with A grades")

                    if grade_counts.get('F', 0) == 0:
                        insights.append("🎉 **No failing students** - Everyone is passing!")
                    elif grade_counts.get('F', 0) >= class_analytics['total_students'] * 0.2:
                        insights.append("⚠️ **High failure rate** - 20%+ students failing")

                    for insight in insights:
                        st.write(insight)

                    # Export section
                    st.markdown("---")
                    st.markdown("### 📥 Export Class Report")

                    col1_1, col1_2 = st.columns(2)

                    with col1_1:
                        try:
                            export_class_summary(class_analytics, class_analytics['student_summaries'], "pdf")
                        except Exception as e:
                            st.error(f"PDF export error: {str(e)}")

                    with col1_2:
                        try:
                            export_class_summary(class_analytics, class_analytics['student_summaries'], "csv")
                        except Exception as e:
                            st.error(f"CSV export error: {str(e)}")

            except Exception as e:
                st.error(f"Error analyzing class performance: {str(e)}")

    else:
        # Overall system analytics
        st.subheader("🌐 Overall System Analytics")

        with st.spinner("Loading system analytics..."):
            try:
                # Get overall statistics
                overall_stats = PerformanceAnalytics.get_overall_statistics()
                display_analytics_metrics(overall_stats)

                # Class-wise performance comparison
                st.markdown("### 📊 Class-wise Performance Comparison")

                class_performance = PerformanceAnalytics.get_class_wise_performance()

                if class_performance:
                    class_df_data = []
                    for class_data in class_performance:
                        class_df_data.append({
                            'Class': f"{class_data['class']}-{class_data['section']}",
                            'Students': class_data['total_students'],
                            'With Marks': class_data['students_with_marks'],
                            'Assessments': class_data['total_assessments'],
                            'Average %': f"{class_data['avg_percentage']:.1f}%",
                            'Pass Count': class_data['pass_count'],
                            'Pass %': f"{class_data['pass_percentage']:.1f}%"
                        })

                    class_df = pd.DataFrame(class_df_data)
                    st.dataframe(
                        class_df,
                        use_container_width=True,
                        hide_index=True
                    )

                # Subject performance comparison
                st.markdown("### 📚 Subject Performance Comparison")

                subject_performance = PerformanceAnalytics.get_subject_performance_comparison()

                if subject_performance:
                    subject_df_data = []
                    for subject_data in subject_performance:
                        subject_df_data.append({
                            'Subject': subject_data['subject'],
                            'Assessments': subject_data['total_assessments'],
                            'Avg Marks': f"{subject_data['avg_marks']:.1f}",
                            'Avg %': f"{subject_data['avg_percentage']:.1f}%",
                            'Grade': subject_data['grade'],
                            'Highest': subject_data['highest_marks'],
                            'Lowest': subject_data['lowest_marks']
                        })

                    subject_df = pd.DataFrame(subject_df_data)
                    st.dataframe(
                        subject_df,
                        use_container_width=True,
                        hide_index=True
                    )

                # Top performers across all classes
                st.markdown("### 🏆 Top Performers (All Classes)")

                top_performers = PerformanceAnalytics.get_top_performers(limit=10)

                if top_performers:
                    top_df_data = []
                    for performer in top_performers:
                        top_df_data.append({
                            'Rank': performer['rank'],
                            'Name': performer['name'],
                            'Class': f"{performer['class']}-{performer['section']}",
                            'Percentage': f"{performer['percentage']:.1f}%",
                            'Grade': performer['grade'],
                            'Subjects': performer['total_subjects']
                        })

                    top_df = pd.DataFrame(top_df_data)
                    st.dataframe(
                        top_df,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:
                st.error(f"Error loading system analytics: {str(e)}")

with col2:
    # Right sidebar with additional insights
    st.subheader("📋 Quick Insights")

    try:
        if selected_class != "All":
            # Class-specific insights
            class_students = [s for s in students if s[2] == selected_class]
            if selected_section != "All":
                class_students = [s for s in class_students if s[3] == selected_section]

            st.metric("Total Students in Class", len(class_students))

            # Get marks for this class
            all_marks = Marks.get_all_marks()
            class_marks = []
            for mark in all_marks:
                # Find student info
                student_info = next((s for s in students if s[0] == mark[8]), None)
                if student_info and student_info[2] == selected_class:
                    if selected_section == "All" or student_info[3] == selected_section:
                        class_marks.append(mark)

            if class_marks:
                total_assessments = len(class_marks)
                st.metric("Total Assessments", total_assessments)

                # Recent activity
                recent_marks = sorted(class_marks, key=lambda x: x[7], reverse=True)[:5]

                st.markdown("**Recent Assessments:**")
                for mark in recent_marks:
                    percentage = Marks.calculate_percentage(mark[3], mark[4])
                    st.write(f"• {mark[1]}: {mark[2]} ({percentage:.1f}%)")
        else:
            # Overall system insights
            total_students = len(students)
            all_marks = Marks.get_all_marks()

            st.metric("Total Students", total_students)
            st.metric("Total Assessments", len(all_marks))

            if all_marks:
                # Calculate overall pass rate
                passing_assessments = sum(1 for mark in all_marks 
                                        if Marks.calculate_percentage(mark[3], mark[4]) >= 40)
                overall_pass_rate = (passing_assessments / len(all_marks)) * 100

                st.metric("Overall Pass Rate", f"{overall_pass_rate:.1f}%")

    except Exception as e:
        st.error("Could not load insights")

    # Navigation shortcuts
    st.markdown("---")
    st.subheader("🚀 Quick Actions")

    if st.button("📝 Enter Marks", use_container_width=True):
        st.switch_page("pages/3_Enter_Update_Marks.py")

    if st.button("📋 View Report Cards", use_container_width=True):
        st.switch_page("pages/4_Student_Report_Card.py")

    if st.button("📈 Visual Reports", use_container_width=True):
        st.switch_page("pages/6_Visual_Reports.py")

# Help section
with st.expander("ℹ️ Help & Analysis Guide"):
    st.markdown("""
    ### Class Analytics Features:

    **Class Selection:**
    - Choose specific class or view all classes
    - Filter by section within selected class
    - Compare performance across different groups

    **Performance Metrics:**
    - **Class Average**: Overall percentage of the class
    - **Pass Rate**: Percentage of students passing (≥40%)
    - **Grade Distribution**: Breakdown of grades achieved
    - **Top Performers**: Highest achieving students

    **Insights & Analysis:**
    - Automated performance insights
    - Comparison with overall system averages
    - Identification of areas needing attention
    - Recent activity tracking

    **Export Options:**
    - PDF: Professional class summary report
    - CSV: Data for further analysis and records
    - Custom reports for different stakeholders

    **Using Analytics:**
    - Regular monitoring of class performance
    - Identifying students needing extra support
    - Recognizing top performers for awards
    - Planning intervention strategies
    - Parent-teacher conference preparation

    **Performance Thresholds:**
    - Excellent: 80%+ average
    - Good: 60-79% average  
    - Average: 40-59% average
    - Below Average: <40% average
    """)
