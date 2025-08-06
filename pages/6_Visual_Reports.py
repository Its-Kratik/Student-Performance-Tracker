"""
Visual Reports Page - Interactive charts and visualizations
"""
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject
from models.marks import Marks
from utils.analytics import PerformanceAnalytics

st.set_page_config(
    page_title="Visual Reports",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Visual Reports & Analytics")
st.markdown("Interactive charts and visualizations for performance analysis")

# Check if data exists
students = Student.get_all_students()
marks = Marks.get_all_marks()

if not students or not marks:
    st.warning("⚠️ Insufficient data for visualization. Please add students and marks first.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Manage Students"):
            st.switch_page("pages/1_Manage_Students.py")
    with col2:
        if st.button("Go to Enter Marks"):
            st.switch_page("pages/3_Enter_Update_Marks.py")
    st.stop()

# Sidebar for chart selection
with st.sidebar:
    st.subheader("Chart Selection")

    chart_type = st.radio(
        "Select Chart Type:",
        [
            "Grade Distribution",
            "Class Performance",
            "Subject Performance", 
            "Top Performers",
            "Performance Trends",
            "Pass/Fail Analysis"
        ]
    )

    # Filters
    st.markdown("---")
    st.subheader("Filters")

    # Class filter
    unique_classes = Student.get_unique_classes()
    selected_class = st.selectbox(
        "Class Filter:",
        options=["All"] + unique_classes
    )

    # Section filter
    if selected_class != "All":
        class_sections = []
        for student in students:
            if student[2] == selected_class and student[3] not in class_sections:
                class_sections.append(student[3])
        class_sections.sort()

        selected_section = st.selectbox(
            "Section Filter:",
            options=["All"] + class_sections
        )
    else:
        selected_section = "All"

# Main content area
if chart_type == "Grade Distribution":
    st.subheader("📊 Grade Distribution Analysis")

    try:
        # Get grade distribution data
        if selected_class != "All":
            grade_data = PerformanceAnalytics.get_grade_distribution(
                selected_class, 
                selected_section if selected_section != "All" else None
            )
        else:
            grade_data = PerformanceAnalytics.get_grade_distribution()

        if grade_data['total_students'] > 0:
            # Prepare data for visualization
            grade_counts = grade_data['grade_counts']

            # Remove grades with 0 count
            filtered_grades = {k: v for k, v in grade_counts.items() if v > 0}

            if filtered_grades:
                # Create DataFrame for plotting
                df_grades = pd.DataFrame([
                    {'Grade': grade, 'Count': count, 'Percentage': (count/grade_data['total_students'])*100}
                    for grade, count in filtered_grades.items()
                ])

                col1, col2 = st.columns(2)

                with col1:
                    # Pie chart using Plotly
                    fig_pie = px.pie(
                        df_grades, 
                        values='Count', 
                        names='Grade',
                        title=f"Grade Distribution - Total Students: {grade_data['total_students']}",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col2:
                    # Bar chart using Plotly
                    fig_bar = px.bar(
                        df_grades,
                        x='Grade',
                        y='Count',
                        title="Grade Distribution (Count)",
                        color='Count',
                        color_continuous_scale='Viridis'
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)

                # Summary statistics
                st.markdown("### 📋 Grade Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    a_grades = grade_counts.get('A+', 0) + grade_counts.get('A', 0)
                    st.metric("A Grades", a_grades, f"{(a_grades/grade_data['total_students']*100):.1f}%")

                with col2:
                    b_grades = grade_counts.get('B+', 0) + grade_counts.get('B', 0)
                    st.metric("B Grades", b_grades, f"{(b_grades/grade_data['total_students']*100):.1f}%")

                with col3:
                    c_grades = grade_counts.get('C+', 0) + grade_counts.get('C', 0)
                    st.metric("C Grades", c_grades, f"{(c_grades/grade_data['total_students']*100):.1f}%")

                with col4:
                    f_grades = grade_counts.get('F', 0)
                    st.metric("F Grades", f_grades, f"{(f_grades/grade_data['total_students']*100):.1f}%")

        else:
            st.info("No grade data available for the selected filters")

    except Exception as e:
        st.error(f"Error creating grade distribution chart: {str(e)}")

elif chart_type == "Class Performance":
    st.subheader("🏫 Class Performance Comparison")

    try:
        class_performance = PerformanceAnalytics.get_class_wise_performance()

        if class_performance:
            # Create DataFrame
            df_class = pd.DataFrame(class_performance)
            df_class['Class-Section'] = df_class['class'] + '-' + df_class['section']

            col1, col2 = st.columns(2)

            with col1:
                # Average percentage comparison
                fig_avg = px.bar(
                    df_class,
                    x='Class-Section',
                    y='avg_percentage',
                    title="Average Percentage by Class-Section",
                    color='avg_percentage',
                    color_continuous_scale='RdYlGn'
                )
                fig_avg.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_avg, use_container_width=True)

            with col2:
                # Pass percentage comparison
                fig_pass = px.bar(
                    df_class,
                    x='Class-Section',
                    y='pass_percentage',
                    title="Pass Percentage by Class-Section",
                    color='pass_percentage',
                    color_continuous_scale='Blues'
                )
                fig_pass.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_pass, use_container_width=True)

            # Scatter plot: Average vs Pass percentage
            fig_scatter = px.scatter(
                df_class,
                x='avg_percentage',
                y='pass_percentage',
                size='total_students',
                color='class',
                hover_name='Class-Section',
                title="Class Performance Overview: Average % vs Pass %",
                labels={'avg_percentage': 'Average Percentage', 'pass_percentage': 'Pass Percentage'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Performance table
            st.markdown("### 📊 Detailed Class Performance")

            display_df = df_class[['Class-Section', 'total_students', 'avg_percentage', 'pass_percentage', 'total_assessments']]
            display_df.columns = ['Class-Section', 'Students', 'Avg %', 'Pass %', 'Assessments']

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No class performance data available")

    except Exception as e:
        st.error(f"Error creating class performance charts: {str(e)}")

elif chart_type == "Subject Performance":
    st.subheader("📚 Subject Performance Analysis")

    try:
        subject_performance = PerformanceAnalytics.get_subject_performance_comparison()

        if subject_performance:
            # Create DataFrame
            df_subjects = pd.DataFrame(subject_performance)

            col1, col2 = st.columns(2)

            with col1:
                # Average percentage by subject
                fig_subj_avg = px.bar(
                    df_subjects,
                    y='subject',
                    x='avg_percentage',
                    orientation='h',
                    title="Average Percentage by Subject",
                    color='avg_percentage',
                    color_continuous_scale='Viridis'
                )
                fig_subj_avg.update_layout(height=500)
                st.plotly_chart(fig_subj_avg, use_container_width=True)

            with col2:
                # Number of assessments by subject
                fig_subj_count = px.bar(
                    df_subjects,
                    y='subject',
                    x='total_assessments',
                    orientation='h',
                    title="Total Assessments by Subject",
                    color='total_assessments',
                    color_continuous_scale='Blues'
                )
                fig_subj_count.update_layout(height=500)
                st.plotly_chart(fig_subj_count, use_container_width=True)

            # Subject performance range (min to max)
            fig_range = go.Figure()

            for _, subject in df_subjects.iterrows():
                fig_range.add_trace(go.Scatter(
                    x=[subject['lowest_marks'], subject['highest_marks']],
                    y=[subject['subject'], subject['subject']],
                    mode='lines+markers',
                    name=subject['subject'],
                    line=dict(width=4),
                    marker=dict(size=8)
                ))

            fig_range.update_layout(
                title="Subject Performance Range (Min to Max Marks)",
                xaxis_title="Marks",
                yaxis_title="Subject",
                showlegend=False,
                height=500
            )

            st.plotly_chart(fig_range, use_container_width=True)

            # Subject performance table
            st.markdown("### 📊 Subject Performance Details")

            display_df = df_subjects[['subject', 'total_assessments', 'avg_percentage', 'highest_marks', 'lowest_marks', 'grade']]
            display_df.columns = ['Subject', 'Assessments', 'Avg %', 'Highest', 'Lowest', 'Grade']

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No subject performance data available")

    except Exception as e:
        st.error(f"Error creating subject performance charts: {str(e)}")

elif chart_type == "Top Performers":
    st.subheader("🏆 Top Performers Analysis")

    try:
        # Get top performers data
        if selected_class != "All":
            top_performers = PerformanceAnalytics.get_top_performers(
                limit=15, 
                class_name=selected_class
            )
        else:
            top_performers = PerformanceAnalytics.get_top_performers(limit=15)

        if top_performers:
            # Create DataFrame
            df_top = pd.DataFrame(top_performers)

            col1, col2 = st.columns(2)

            with col1:
                # Top performers bar chart
                fig_top = px.bar(
                    df_top.head(10),
                    y='name',
                    x='percentage',
                    orientation='h',
                    title="Top 10 Performers",
                    color='percentage',
                    color_continuous_scale='RdYlGn'
                )
                fig_top.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top, use_container_width=True)

            with col2:
                # Performance by class
                if selected_class == "All":
                    df_top['Class-Section'] = df_top['class'] + '-' + df_top['section']

                    fig_class_perf = px.box(
                        df_top,
                        x='Class-Section',
                        y='percentage',
                        title="Performance Distribution by Class",
                        points="all"
                    )
                    fig_class_perf.update_layout(xaxis_tickangle=-45, height=500)
                    st.plotly_chart(fig_class_perf, use_container_width=True)
                else:
                    # Grade distribution for top performers
                    grade_counts = df_top['grade'].value_counts()

                    fig_grade_top = px.pie(
                        values=grade_counts.values,
                        names=grade_counts.index,
                        title="Grade Distribution - Top Performers"
                    )
                    st.plotly_chart(fig_grade_top, use_container_width=True)

            # Leaderboard table
            st.markdown("### 🥇 Leaderboard")

            display_df = df_top[['rank', 'name', 'class', 'section', 'percentage', 'grade', 'total_subjects']]
            display_df.columns = ['Rank', 'Name', 'Class', 'Section', 'Percentage', 'Grade', 'Subjects']

            # Color code the rows based on rank
            def highlight_rank(row):
                if row['Rank'] == 1:
                    return ['background-color: gold'] * len(row)
                elif row['Rank'] == 2:
                    return ['background-color: silver'] * len(row)
                elif row['Rank'] == 3:
                    return ['background-color: #CD7F32'] * len(row)  # Bronze
                else:
                    return [''] * len(row)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No top performers data available")

    except Exception as e:
        st.error(f"Error creating top performers charts: {str(e)}")

elif chart_type == "Performance Trends":
    st.subheader("📈 Performance Trends")

    try:
        # Get all marks with dates
        all_marks = Marks.get_all_marks()

        if all_marks:
            # Create DataFrame for trend analysis
            trend_data = []
            for mark in all_marks:
                percentage = Marks.calculate_percentage(mark[3], mark[4])
                trend_data.append({
                    'Date': mark[5],
                    'Student': mark[1],
                    'Subject': mark[2],
                    'Percentage': percentage,
                    'Assessment_Type': mark[6]
                })

            df_trends = pd.DataFrame(trend_data)
            df_trends['Date'] = pd.to_datetime(df_trends['Date'])

            # Apply filters
            if selected_class != "All":
                # Filter by class
                class_students = [s[1] for s in students if s[2] == selected_class]
                if selected_section != "All":
                    class_students = [s[1] for s in students if s[2] == selected_class and s[3] == selected_section]

                df_trends = df_trends[df_trends['Student'].isin(class_students)]

            if not df_trends.empty:
                col1, col2 = st.columns(2)

                with col1:
                    # Performance trend over time
                    df_daily_avg = df_trends.groupby('Date')['Percentage'].mean().reset_index()

                    fig_trend = px.line(
                        df_daily_avg,
                        x='Date',
                        y='Percentage',
                        title="Average Performance Trend Over Time",
                        markers=True
                    )
                    fig_trend.add_hline(y=40, line_dash="dash", line_color="red", 
                                      annotation_text="Pass Threshold (40%)")
                    st.plotly_chart(fig_trend, use_container_width=True)

                with col2:
                    # Performance by assessment type
                    df_assessment = df_trends.groupby('Assessment_Type')['Percentage'].mean().reset_index()

                    fig_assessment = px.bar(
                        df_assessment,
                        x='Assessment_Type',
                        y='Percentage',
                        title="Average Performance by Assessment Type",
                        color='Percentage',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig_assessment, use_container_width=True)

                # Subject performance trend
                df_subject_trend = df_trends.groupby(['Date', 'Subject'])['Percentage'].mean().reset_index()

                fig_subject_trend = px.line(
                    df_subject_trend,
                    x='Date',
                    y='Percentage',
                    color='Subject',
                    title="Subject-wise Performance Trends"
                )
                st.plotly_chart(fig_subject_trend, use_container_width=True)

            else:
                st.info("No trend data available for selected filters")

        else:
            st.info("No marks data available for trend analysis")

    except Exception as e:
        st.error(f"Error creating performance trend charts: {str(e)}")

elif chart_type == "Pass/Fail Analysis":
    st.subheader("✅❌ Pass/Fail Analysis")

    try:
        # Get pass/fail data
        all_marks = Marks.get_all_marks()

        if all_marks:
            pass_fail_data = []

            for mark in all_marks:
                percentage = Marks.calculate_percentage(mark[3], mark[4])
                status = "Pass" if percentage >= 40 else "Fail"

                # Get student info
                student_info = next((s for s in students if s[0] == mark[8]), None)

                pass_fail_data.append({
                    'Student': mark[1],
                    'Subject': mark[2],
                    'Percentage': percentage,
                    'Status': status,
                    'Class': student_info[2] if student_info else 'Unknown',
                    'Section': student_info[3] if student_info else 'Unknown',
                    'Assessment_Type': mark[6]
                })

            df_pass_fail = pd.DataFrame(pass_fail_data)

            # Apply filters
            if selected_class != "All":
                df_pass_fail = df_pass_fail[df_pass_fail['Class'] == selected_class]
                if selected_section != "All":
                    df_pass_fail = df_pass_fail[df_pass_fail['Section'] == selected_section]

            if not df_pass_fail.empty:
                col1, col2 = st.columns(2)

                with col1:
                    # Overall pass/fail ratio
                    status_counts = df_pass_fail['Status'].value_counts()

                    fig_pass_fail = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Overall Pass/Fail Ratio",
                        color_discrete_map={'Pass': 'green', 'Fail': 'red'}
                    )
                    st.plotly_chart(fig_pass_fail, use_container_width=True)

                with col2:
                    # Pass rate by subject
                    subject_pass_rate = df_pass_fail.groupby(['Subject', 'Status']).size().unstack(fill_value=0)
                    subject_pass_rate['Pass_Rate'] = (subject_pass_rate.get('Pass', 0) / 
                                                    (subject_pass_rate.get('Pass', 0) + subject_pass_rate.get('Fail', 0))) * 100

                    subject_pass_rate = subject_pass_rate.reset_index()

                    fig_subject_pass = px.bar(
                        subject_pass_rate,
                        x='Subject',
                        y='Pass_Rate',
                        title="Pass Rate by Subject",
                        color='Pass_Rate',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_subject_pass.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_subject_pass, use_container_width=True)

                # Class-wise pass/fail analysis (if showing all classes)
                if selected_class == "All":
                    class_pass_fail = df_pass_fail.groupby(['Class', 'Section', 'Status']).size().unstack(fill_value=0)
                    class_pass_fail['Pass_Rate'] = (class_pass_fail.get('Pass', 0) / 
                                                   (class_pass_fail.get('Pass', 0) + class_pass_fail.get('Fail', 0))) * 100

                    class_pass_fail = class_pass_fail.reset_index()
                    class_pass_fail['Class-Section'] = class_pass_fail['Class'] + '-' + class_pass_fail['Section']

                    fig_class_pass = px.bar(
                        class_pass_fail,
                        x='Class-Section',
                        y='Pass_Rate',
                        title="Pass Rate by Class-Section",
                        color='Pass_Rate',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_class_pass.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_class_pass, use_container_width=True)

                # Students at risk (consistently failing)
                student_fail_count = df_pass_fail[df_pass_fail['Status'] == 'Fail']['Student'].value_counts()

                if not student_fail_count.empty:
                    st.markdown("### ⚠️ Students at Risk (Multiple Failures)")

                    at_risk_students = student_fail_count.head(10).reset_index()
                    at_risk_students.columns = ['Student', 'Failed_Assessments']

                    fig_at_risk = px.bar(
                        at_risk_students,
                        x='Student',
                        y='Failed_Assessments',
                        title="Students with Most Failed Assessments",
                        color='Failed_Assessments',
                        color_continuous_scale='Reds'
                    )
                    fig_at_risk.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_at_risk, use_container_width=True)

                    # Display table
                    st.dataframe(at_risk_students, use_container_width=True, hide_index=True)

            else:
                st.info("No pass/fail data available for selected filters")

        else:
            st.info("No marks data available for pass/fail analysis")

    except Exception as e:
        st.error(f"Error creating pass/fail analysis: {str(e)}")

# Export section
st.markdown("---")
st.markdown("### 📥 Export Charts")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Current Chart Data (CSV)", use_container_width=True):
        st.info("Chart data export feature coming soon!")

with col2:
    if st.button("🖼️ Export Charts as Images", use_container_width=True):
        st.info("Chart image export feature coming soon!")

# Help section
with st.expander("ℹ️ Chart Guide & Tips"):
    st.markdown("""
    ### Chart Types Explained:

    **📊 Grade Distribution:**
    - Shows percentage of students in each grade category
    - Pie chart for overall view, bar chart for counts
    - Helps identify grade concentration patterns

    **🏫 Class Performance:**
    - Compares average performance across classes
    - Shows pass rates and total assessments
    - Scatter plot reveals performance vs pass rate correlation

    **📚 Subject Performance:**
    - Analyzes difficulty and performance by subject
    - Shows assessment frequency and score ranges
    - Identifies subjects needing attention

    **🏆 Top Performers:**
    - Highlights best performing students
    - Shows grade distribution among top performers
    - Useful for recognition and awards

    **📈 Performance Trends:**
    - Shows performance changes over time
    - Compares different assessment types
    - Helps track improvement or decline

    **✅❌ Pass/Fail Analysis:**
    - Overall system pass rates
    - Subject-wise failure patterns
    - Identifies at-risk students

    ### Tips for Better Analysis:
    - Use filters to focus on specific classes or sections
    - Compare trends across different time periods
    - Look for patterns in subject performance
    - Identify students needing intervention
    - Use data for parent-teacher conferences
    - Regular monitoring helps catch issues early
    """)
