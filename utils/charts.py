"""
Chart generation utilities using Altair and Matplotlib
"""
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List

class ChartGenerator:
    """Class for generating various charts and visualizations"""

    @staticmethod
    def create_grade_distribution_pie_chart(grade_data: Dict) -> alt.Chart:
        """Create a pie chart for grade distribution using Altair"""
        # Prepare data
        grades = []
        counts = []
        for grade, count in grade_data['grade_counts'].items():
            if count > 0:  # Only include grades with students
                grades.append(grade)
                counts.append(count)

        if not grades:
            return None

        df = pd.DataFrame({
            'Grade': grades,
            'Count': counts
        })

        # Create pie chart using Altair (donut chart)
        chart = alt.Chart(df).mark_arc(innerRadius=50, outerRadius=100).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Grade", type="nominal", 
                          scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'])),
            tooltip=['Grade', 'Count']
        ).properties(
            title="Grade Distribution",
            width=300,
            height=300
        )

        return chart

    @staticmethod
    def create_subject_performance_bar_chart(subjects_data: List[Dict]) -> alt.Chart:
        """Create bar chart for subject performance comparison"""
        if not subjects_data:
            return None

        df = pd.DataFrame(subjects_data)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('avg_percentage:Q', title='Average Percentage'),
            y=alt.Y('subject:N', sort='-x', title='Subject'),
            color=alt.Color('avg_percentage:Q', 
                          scale=alt.Scale(range=['#d62728', '#ff7f0e', '#2ca02c']),
                          legend=None),
            tooltip=['subject', 'avg_percentage', 'total_assessments']
        ).properties(
            title="Subject Performance Comparison",
            width=500,
            height=300
        )

        return chart

    @staticmethod
    def create_top_performers_chart(performers_data: List[Dict]) -> alt.Chart:
        """Create bar chart for top performers"""
        if not performers_data:
            return None

        df = pd.DataFrame(performers_data)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('percentage:Q', title='Percentage'),
            y=alt.Y('name:N', sort='-x', title='Student Name'),
            color=alt.Color('percentage:Q',
                          scale=alt.Scale(range=['#2ca02c', '#1f77b4', '#ff7f0e']),
                          legend=None),
            tooltip=['name', 'class', 'section', 'percentage', 'grade']
        ).properties(
            title="Top Performers",
            width=500,
            height=300
        )

        return chart

    @staticmethod
    def create_class_performance_chart(class_data: List[Dict]) -> alt.Chart:
        """Create chart for class-wise performance"""
        if not class_data:
            return None

        df = pd.DataFrame(class_data)
        df['class_section'] = df['class'] + '-' + df['section']

        chart = alt.Chart(df).mark_circle(size=200).encode(
            x=alt.X('avg_percentage:Q', title='Average Percentage'),
            y=alt.Y('pass_percentage:Q', title='Pass Percentage'),
            color=alt.Color('class:N', title='Class'),
            size=alt.Size('total_students:Q', title='Total Students'),
            tooltip=['class_section', 'avg_percentage', 'pass_percentage', 'total_students']
        ).properties(
            title="Class Performance Overview",
            width=500,
            height=400
        )

        return chart

    @staticmethod
    def create_trend_line_chart(trend_data: Dict, subject_name: str) -> alt.Chart:
        """Create line chart for student performance trends"""
        if not trend_data['has_data'] or subject_name not in trend_data['subject_trends']:
            return None

        subject_data = trend_data['subject_trends'][subject_name]
        df = pd.DataFrame(subject_data)

        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('date:T', title='Assessment Date'),
            y=alt.Y('percentage:Q', title='Percentage'),
            tooltip=['date', 'percentage', 'marks_obtained', 'max_marks']
        ).properties(
            title=f"Performance Trend: {subject_name}",
            width=500,
            height=300
        )

        return chart

    @staticmethod
    def create_plotly_grade_pie_chart(grade_data: Dict) -> go.Figure:
        """Create interactive pie chart using Plotly"""
        grades = []
        counts = []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

        for grade, count in grade_data['grade_counts'].items():
            if count > 0:
                grades.append(grade)
                counts.append(count)

        if not grades:
            return None

        fig = go.Figure(data=[go.Pie(
            labels=grades,
            values=counts,
            hole=0.4,
            marker=dict(colors=colors[:len(grades)])
        )])

        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )

        fig.update_layout(
            title="Grade Distribution",
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )

        return fig

    @staticmethod
    def create_matplotlib_performance_heatmap(class_data: List[Dict]) -> plt.Figure:
        """Create heatmap for class performance using matplotlib"""
        if not class_data:
            return None

        # Prepare data for heatmap
        df = pd.DataFrame(class_data)

        if df.empty:
            return None

        # Create pivot table
        pivot_data = df.pivot_table(
            index='class',
            columns='section', 
            values='avg_percentage',
            fill_value=0
        )

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(pivot_data.values, cmap='RdYlGn', aspect='auto')

        # Set ticks and labels
        ax.set_xticks(range(len(pivot_data.columns)))
        ax.set_yticks(range(len(pivot_data.index)))
        ax.set_xticklabels(pivot_data.columns)
        ax.set_yticklabels(pivot_data.index)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Average Percentage', rotation=270, labelpad=15)

        # Add text annotations
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                value = pivot_data.iloc[i, j]
                if value > 0:
                    text = ax.text(j, i, f'{value:.1f}%', 
                                 ha='center', va='center', 
                                 color='white' if value < 50 else 'black')

        ax.set_title('Class-wise Performance Heatmap')
        ax.set_xlabel('Section')
        ax.set_ylabel('Class')

        plt.tight_layout()
        return fig

def display_grade_distribution_chart(grade_data: Dict, chart_type: str = "plotly") -> None:
    """Display grade distribution chart"""
    if not grade_data or grade_data.get('total_students', 0) == 0:
        st.info("No data available for grade distribution")
        return

    st.subheader("📊 Grade Distribution")

    if chart_type == "altair":
        chart = ChartGenerator.create_grade_distribution_pie_chart(grade_data)
        if chart:
            st.altair_chart(chart, use_container_width=True)
    elif chart_type == "plotly":
        fig = ChartGenerator.create_plotly_grade_pie_chart(grade_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Display summary table
    with st.expander("View Grade Summary"):
        grade_df = pd.DataFrame([
            {'Grade': grade, 'Count': count, 'Percentage': f"{(count/grade_data['total_students']*100):.1f}%"}
            for grade, count in grade_data['grade_counts'].items()
            if count > 0
        ])
        st.dataframe(grade_df, use_container_width=True, hide_index=True)

def display_subject_performance_chart(subjects_data: List[Dict]) -> None:
    """Display subject performance comparison chart"""
    if not subjects_data:
        st.info("No data available for subject performance")
        return

    st.subheader("📈 Subject Performance Comparison")

    chart = ChartGenerator.create_subject_performance_bar_chart(subjects_data)
    if chart:
        st.altair_chart(chart, use_container_width=True)

    # Display detailed table
    with st.expander("View Subject Details"):
        df = pd.DataFrame(subjects_data)
        st.dataframe(
            df[['subject', 'avg_percentage', 'total_assessments', 'grade']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "subject": "Subject",
                "avg_percentage": "Average %",
                "total_assessments": "Assessments",
                "grade": "Grade"
            }
        )

def display_top_performers_chart(performers_data: List[Dict]) -> None:
    """Display top performers chart"""
    if not performers_data:
        st.info("No data available for top performers")
        return

    st.subheader("🏆 Top Performers")

    chart = ChartGenerator.create_top_performers_chart(performers_data)
    if chart:
        st.altair_chart(chart, use_container_width=True)

    # Display leaderboard table
    with st.expander("View Leaderboard"):
        df = pd.DataFrame(performers_data)
        st.dataframe(
            df[['rank', 'name', 'class', 'section', 'percentage', 'grade']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "rank": "Rank",
                "name": "Student Name",
                "class": "Class",
                "section": "Section",
                "percentage": "Percentage",
                "grade": "Grade"
            }
        )
