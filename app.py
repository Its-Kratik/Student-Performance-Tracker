import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io
import json

# Page configuration
st.set_page_config(
    page_title="Student Performance Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
@st.cache_resource
def init_database():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect('student_tracker.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            grade_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Marks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            marks REAL,
            max_marks REAL DEFAULT 100,
            exam_type TEXT,
            exam_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        # Sample students
        students = [
            ('Alice Johnson', 'alice@email.com', '123-456-7890', '10th Grade'),
            ('Bob Smith', 'bob@email.com', '123-456-7891', '10th Grade'),
            ('Carol Davis', 'carol@email.com', '123-456-7892', '11th Grade'),
            ('David Wilson', 'david@email.com', '123-456-7893', '11th Grade'),
            ('Eva Brown', 'eva@email.com', '123-456-7894', '12th Grade')
        ]
        cursor.executemany("INSERT INTO students (name, email, phone, grade_level) VALUES (?, ?, ?, ?)", students)
        
        # Sample subjects
        subjects = [
            ('Mathematics', 'MATH101', 'Advanced Mathematics'),
            ('Physics', 'PHY101', 'Physics Fundamentals'),
            ('Chemistry', 'CHEM101', 'General Chemistry'),
            ('English', 'ENG101', 'English Literature'),
            ('History', 'HIST101', 'World History'),
            ('Biology', 'BIO101', 'General Biology')
        ]
        cursor.executemany("INSERT INTO subjects (name, code, description) VALUES (?, ?, ?)", subjects)
        
        # Sample marks
        import random
        marks_data = []
        for student_id in range(1, 6):
            for subject_id in range(1, 7):
                for exam_type in ['Midterm', 'Final', 'Quiz']:
                    marks = round(random.uniform(60, 95), 1)
                    exam_date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    marks_data.append((student_id, subject_id, marks, 100, exam_type, exam_date))
        
        cursor.executemany(
            "INSERT INTO marks (student_id, subject_id, marks, max_marks, exam_type, exam_date) VALUES (?, ?, ?, ?, ?, ?)", 
            marks_data
        )
    
    conn.commit()
    return conn

def get_database_connection():
    """Get database connection"""
    return sqlite3.connect('student_tracker.db', check_same_thread=False)

def calculate_grade(percentage):
    """Calculate letter grade from percentage"""
    if percentage >= 90: return 'A+'
    elif percentage >= 85: return 'A'
    elif percentage >= 80: return 'B+'
    elif percentage >= 75: return 'B'
    elif percentage >= 70: return 'C+'
    elif percentage >= 65: return 'C'
    elif percentage >= 60: return 'D'
    else: return 'F'

def main():
    # Initialize database
    conn = init_database()
    
    # Sidebar navigation
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.selectbox("Select Page", [
        "🏠 Dashboard",
        "👥 Students",
        "📖 Subjects", 
        "📝 Marks Entry",
        "📊 Performance Reports",
        "📈 Analytics"
    ])
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Students":
        manage_students()
    elif page == "📖 Subjects":
        manage_subjects()
    elif page == "📝 Marks Entry":
        manage_marks()
    elif page == "📊 Performance Reports":
        show_reports()
    elif page == "📈 Analytics":
        show_analytics()

def show_dashboard():
    """Dashboard with overview statistics"""
    st.title("📚 Student Performance Tracker")
    st.markdown("---")
    
    conn = get_database_connection()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        student_count = pd.read_sql("SELECT COUNT(*) as count FROM students", conn)['count'].iloc[0]
        st.metric("Total Students", student_count, delta="Active")
    
    with col2:
        subject_count = pd.read_sql("SELECT COUNT(*) as count FROM subjects", conn)['count'].iloc[0]
        st.metric("Total Subjects", subject_count, delta="Available")
    
    with col3:
        marks_count = pd.read_sql("SELECT COUNT(*) as count FROM marks", conn)['count'].iloc[0]
        st.metric("Total Assessments", marks_count, delta="Recorded")
    
    with col4:
        avg_performance = pd.read_sql("SELECT AVG(marks/max_marks*100) as avg FROM marks", conn)['avg'].iloc[0]
        st.metric("Average Performance", f"{avg_performance:.1f}%", delta="Overall")
    
    st.markdown("---")
    
    # Recent performance chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Recent Performance Trends")
        query = """
            SELECT s.name as student, AVG(m.marks/m.max_marks*100) as avg_score
            FROM students s
            JOIN marks m ON s.id = m.student_id
            GROUP BY s.id, s.name
            ORDER BY avg_score DESC
            LIMIT 10
        """
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            fig = px.bar(df, x='avg_score', y='student', orientation='h',
                        title="Average Student Performance", color='avg_score',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Subject Performance Distribution")
        query = """
            SELECT sub.name as subject, AVG(m.marks/m.max_marks*100) as avg_score
            FROM subjects sub
            JOIN marks m ON sub.id = m.subject_id
            GROUP BY sub.id, sub.name
            ORDER BY avg_score DESC
        """
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            fig = px.pie(df, values='avg_score', names='subject', 
                        title="Subject Performance Share")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

def manage_students():
    """Student management interface"""
    st.title("👥 Student Management")
    
    tab1, tab2, tab3 = st.tabs(["View Students", "Add Student", "Edit Student"])
    
    conn = get_database_connection()
    
    with tab1:
        st.subheader("📋 All Students")
        students_df = pd.read_sql("SELECT * FROM students ORDER BY name", conn)
        
        if not students_df.empty:
            # Add performance data
            for idx, row in students_df.iterrows():
                query = f"SELECT AVG(marks/max_marks*100) as avg FROM marks WHERE student_id = {row['id']}"
                avg_result = pd.read_sql(query, conn)
                avg_performance = avg_result['avg'].iloc[0] if not avg_result.empty and avg_result['avg'].iloc[0] else 0
                students_df.at[idx, 'avg_performance'] = f"{avg_performance:.1f}%"
                students_df.at[idx, 'grade'] = calculate_grade(avg_performance)
            
            st.dataframe(students_df[['name', 'email', 'grade_level', 'avg_performance', 'grade']], 
                        use_container_width=True)
        else:
            st.info("No students found.")
    
    with tab2:
        st.subheader("➕ Add New Student")
        with st.form("add_student_form"):
            name = st.text_input("Student Name*", placeholder="Enter full name")
            email = st.text_input("Email", placeholder="student@email.com")
            phone = st.text_input("Phone", placeholder="123-456-7890")
            grade_level = st.selectbox("Grade Level", 
                                     ["9th Grade", "10th Grade", "11th Grade", "12th Grade"])
            
            submitted = st.form_submit_button("Add Student")
            
            if submitted and name:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO students (name, email, phone, grade_level) VALUES (?, ?, ?, ?)",
                        (name, email, phone, grade_level)
                    )
                    conn.commit()
                    st.success(f"✅ Student '{name}' added successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ Email already exists!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("✏️ Edit Student")
        students_df = pd.read_sql("SELECT id, name FROM students ORDER BY name", conn)
        
        if not students_df.empty:
            student_options = {f"{row['name']} (ID: {row['id']})": row['id'] 
                             for _, row in students_df.iterrows()}
            selected_student = st.selectbox("Select Student", options=list(student_options.keys()))
            
            if selected_student:
                student_id = student_options[selected_student]
                student_data = pd.read_sql(f"SELECT * FROM students WHERE id = {student_id}", conn).iloc[0]
                
                with st.form("edit_student_form"):
                    name = st.text_input("Student Name*", value=student_data['name'])
                    email = st.text_input("Email", value=student_data['email'] or '')
                    phone = st.text_input("Phone", value=student_data['phone'] or '')
                    grade_level = st.selectbox("Grade Level", 
                                             ["9th Grade", "10th Grade", "11th Grade", "12th Grade"],
                                             index=["9th Grade", "10th Grade", "11th Grade", "12th Grade"].index(student_data['grade_level']))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("Update Student")
                    with col2:
                        delete_submitted = st.form_submit_button("Delete Student", type="secondary")
                    
                    if update_submitted and name:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE students SET name=?, email=?, phone=?, grade_level=? WHERE id=?",
                            (name, email, phone, grade_level, student_id)
                        )
                        conn.commit()
                        st.success("✅ Student updated successfully!")
                        st.rerun()
                    
                    if delete_submitted:
                        if st.session_state.get('confirm_delete') != student_id:
                            st.session_state.confirm_delete = student_id
                            st.warning("⚠️ Click Delete again to confirm")
                        else:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM marks WHERE student_id=?", (student_id,))
                            cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
                            conn.commit()
                            st.success("✅ Student deleted successfully!")
                            del st.session_state.confirm_delete
                            st.rerun()
    
    conn.close()

def manage_subjects():
    """Subject management interface"""
    st.title("📖 Subject Management")
    
    tab1, tab2 = st.tabs(["View Subjects", "Add Subject"])
    
    conn = get_database_connection()
    
    with tab1:
        st.subheader("📚 All Subjects")
        subjects_df = pd.read_sql("SELECT * FROM subjects ORDER BY name", conn)
        
        if not subjects_df.empty:
            # Add student count for each subject
            for idx, row in subjects_df.iterrows():
                query = f"""
                    SELECT COUNT(DISTINCT student_id) as count 
                    FROM marks WHERE subject_id = {row['id']}
                """
                count_result = pd.read_sql(query, conn)
                subjects_df.at[idx, 'enrolled_students'] = count_result['count'].iloc[0]
            
            st.dataframe(subjects_df[['name', 'code', 'description', 'enrolled_students']], 
                        use_container_width=True)
        else:
            st.info("No subjects found.")
    
    with tab2:
        st.subheader("➕ Add New Subject")
        with st.form("add_subject_form"):
            name = st.text_input("Subject Name*", placeholder="e.g., Advanced Mathematics")
            code = st.text_input("Subject Code*", placeholder="e.g., MATH201")
            description = st.text_area("Description", placeholder="Brief description of the subject")
            
            submitted = st.form_submit_button("Add Subject")
            
            if submitted and name and code:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO subjects (name, code, description) VALUES (?, ?, ?)",
                        (name, code.upper(), description)
                    )
                    conn.commit()
                    st.success(f"✅ Subject '{name}' added successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ Subject name or code already exists!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    conn.close()

def manage_marks():
    """Marks entry and management"""
    st.title("📝 Marks Management")
    
    tab1, tab2 = st.tabs(["Add Marks", "View/Edit Marks"])
    
    conn = get_database_connection()
    
    with tab1:
        st.subheader("➕ Record New Marks")
        
        # Get students and subjects
        students_df = pd.read_sql("SELECT id, name FROM students ORDER BY name", conn)
        subjects_df = pd.read_sql("SELECT id, name FROM subjects ORDER BY name", conn)
        
        if students_df.empty or subjects_df.empty:
            st.warning("⚠️ Please add students and subjects first.")
        else:
            with st.form("add_marks_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    student_options = {f"{row['name']}": row['id'] for _, row in students_df.iterrows()}
                    selected_student = st.selectbox("Select Student*", options=list(student_options.keys()))
                    
                    subject_options = {f"{row['name']}": row['id'] for _, row in subjects_df.iterrows()}
                    selected_subject = st.selectbox("Select Subject*", options=list(subject_options.keys()))
                
                with col2:
                    marks = st.number_input("Marks Obtained*", min_value=0.0, max_value=100.0, step=0.1)
                    max_marks = st.number_input("Maximum Marks", min_value=1.0, value=100.0, step=0.1)
                
                exam_type = st.selectbox("Exam Type", ["Quiz", "Midterm", "Final", "Assignment", "Project"])
                exam_date = st.date_input("Exam Date", value=date.today())
                
                submitted = st.form_submit_button("Record Marks")
                
                if submitted and selected_student and selected_subject:
                    student_id = student_options[selected_student]
                    subject_id = subject_options[selected_subject]
                    
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO marks (student_id, subject_id, marks, max_marks, exam_type, exam_date) VALUES (?, ?, ?, ?, ?, ?)",
                        (student_id, subject_id, marks, max_marks, exam_type, str(exam_date))
                    )
                    conn.commit()
                    
                    percentage = (marks / max_marks) * 100
                    grade = calculate_grade(percentage)
                    st.success(f"✅ Marks recorded! Score: {marks}/{max_marks} ({percentage:.1f}%) - Grade: {grade}")
                    st.rerun()
    
    with tab2:
        st.subheader("📊 All Marks Records")
        query = """
            SELECT m.id, s.name as student, sub.name as subject, m.marks, m.max_marks,
                   ROUND(m.marks/m.max_marks*100, 1) as percentage, m.exam_type, m.exam_date
            FROM marks m
            JOIN students s ON m.student_id = s.id
            JOIN subjects sub ON m.subject_id = sub.id
            ORDER BY m.exam_date DESC, s.name
        """
        marks_df = pd.read_sql(query, conn)
        
        if not marks_df.empty:
            # Add grade column
            marks_df['grade'] = marks_df['percentage'].apply(calculate_grade)
            
            # Display with filters
            col1, col2, col3 = st.columns(3)
            with col1:
                student_filter = st.selectbox("Filter by Student", ["All"] + marks_df['student'].unique().tolist())
            with col2:
                subject_filter = st.selectbox("Filter by Subject", ["All"] + marks_df['subject'].unique().tolist())
            with col3:
                exam_filter = st.selectbox("Filter by Exam Type", ["All"] + marks_df['exam_type'].unique().tolist())
            
            # Apply filters
            filtered_df = marks_df.copy()
            if student_filter != "All":
                filtered_df = filtered_df[filtered_df['student'] == student_filter]
            if subject_filter != "All":
                filtered_df = filtered_df[filtered_df['subject'] == subject_filter]
            if exam_filter != "All":
                filtered_df = filtered_df[filtered_df['exam_type'] == exam_filter]
            
            st.dataframe(filtered_df[['student', 'subject', 'marks', 'max_marks', 'percentage', 'grade', 'exam_type', 'exam_date']], 
                        use_container_width=True)
        else:
            st.info("No marks records found.")
    
    conn.close()

def show_reports():
    """Performance reports and analytics"""
    st.title("📊 Performance Reports")
    
    conn = get_database_connection()
    
    tab1, tab2, tab3 = st.tabs(["Student Reports", "Subject Reports", "Comparative Analysis"])
    
    with tab1:
        st.subheader("👤 Individual Student Performance")
        students_df = pd.read_sql("SELECT id, name FROM students ORDER BY name", conn)
        
        if not students_df.empty:
            student_options = {f"{row['name']}": row['id'] for _, row in students_df.iterrows()}
            selected_student = st.selectbox("Select Student", options=list(student_options.keys()))
            
            if selected_student:
                student_id = student_options[selected_student]
                
                # Student performance query
                query = f"""
                    SELECT sub.name as subject, m.marks, m.max_marks, 
                           ROUND(m.marks/m.max_marks*100, 1) as percentage, 
                           m.exam_type, m.exam_date
                    FROM marks m
                    JOIN subjects sub ON m.subject_id = sub.id
                    WHERE m.student_id = {student_id}
                    ORDER BY m.exam_date DESC
                """
                student_marks = pd.read_sql(query, conn)
                
                if not student_marks.empty:
                    # Overall statistics
                    avg_performance = student_marks['percentage'].mean()
                    best_subject = student_marks.groupby('subject')['percentage'].mean().idxmax()
                    total_assessments = len(student_marks)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Performance", f"{avg_performance:.1f}%", delta=calculate_grade(avg_performance))
                    with col2:
                        st.metric("Best Subject", best_subject, delta="⭐")
                    with col3:
                        st.metric("Total Assessments", total_assessments, delta="📝")
                    
                    # Performance by subject chart
                    subject_avg = student_marks.groupby('subject')['percentage'].mean().reset_index()
                    fig = px.bar(subject_avg, x='subject', y='percentage', 
                               title=f"{selected_student} - Subject Performance", 
                               color='percentage', color_continuous_scale='RdYlGn')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Recent marks table
                    st.subheader("📋 Recent Assessment Results")
                    student_marks['grade'] = student_marks['percentage'].apply(calculate_grade)
                    st.dataframe(student_marks[['subject', 'marks', 'max_marks', 'percentage', 'grade', 'exam_type', 'exam_date']], 
                                use_container_width=True)
                else:
                    st.info("No marks recorded for this student.")
    
    with tab2:
        st.subheader("📚 Subject Performance Analysis")
        
        query = """
            SELECT sub.name as subject, AVG(m.marks/m.max_marks*100) as avg_percentage,
                   COUNT(*) as total_assessments, COUNT(DISTINCT m.student_id) as students_count
            FROM subjects sub
            JOIN marks m ON sub.id = m.subject_id
            GROUP BY sub.id, sub.name
            ORDER BY avg_percentage DESC
        """
        subject_stats = pd.read_sql(query, conn)
        
        if not subject_stats.empty:
            # Subject comparison chart
            fig = px.bar(subject_stats, x='subject', y='avg_percentage', 
                        title="Average Performance by Subject", 
                        color='avg_percentage', color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Subject statistics table
            st.subheader("📊 Subject Statistics")
            subject_stats['avg_grade'] = subject_stats['avg_percentage'].apply(calculate_grade)
            subject_stats['avg_percentage'] = subject_stats['avg_percentage'].round(1)
            st.dataframe(subject_stats[['subject', 'avg_percentage', 'avg_grade', 'students_count', 'total_assessments']], 
                        use_container_width=True)
    
    with tab3:
        st.subheader("⚖️ Comparative Analysis")
        
        # Grade distribution
        query = """
            SELECT ROUND(marks/max_marks*100, 0) as percentage
            FROM marks
        """
        all_marks = pd.read_sql(query, conn)
        
        if not all_marks.empty:
            all_marks['grade'] = all_marks['percentage'].apply(calculate_grade)
            grade_dist = all_marks['grade'].value_counts().sort_index()
            
            fig = px.pie(values=grade_dist.values, names=grade_dist.index, 
                        title="Overall Grade Distribution")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance trends
            st.subheader("📈 Class Performance Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top performers
                query = """
                    SELECT s.name, AVG(m.marks/m.max_marks*100) as avg_score
                    FROM students s
                    JOIN marks m ON s.id = m.student_id
                    GROUP BY s.id, s.name
                    ORDER BY avg_score DESC
                    LIMIT 5
                """
                top_students = pd.read_sql(query, conn)
                st.write("🏆 **Top 5 Students**")
                for idx, row in top_students.iterrows():
                    st.write(f"{idx+1}. {row['name']}: {row['avg_score']:.1f}%")
            
            with col2:
                # Subject difficulty ranking
                query = """
                    SELECT sub.name, AVG(m.marks/m.max_marks*100) as avg_score
                    FROM subjects sub
                    JOIN marks m ON sub.id = m.subject_id
                    GROUP BY sub.id, sub.name
                    ORDER BY avg_score ASC
                    LIMIT 5
                """
                difficult_subjects = pd.read_sql(query, conn)
                st.write("📚 **Most Challenging Subjects**")
                for idx, row in difficult_subjects.iterrows():
                    st.write(f"{idx+1}. {row['name']}: {row['avg_score']:.1f}%")
    
    conn.close()

def show_analytics():
    """Advanced analytics and insights"""
    st.title("📈 Advanced Analytics")
    
    conn = get_database_connection()
    
    # Time-based performance trends
    st.subheader("📅 Performance Trends Over Time")
    
    query = """
        SELECT exam_date, AVG(marks/max_marks*100) as avg_performance
        FROM marks
        WHERE exam_date IS NOT NULL
        GROUP BY exam_date
        ORDER BY exam_date
    """
    time_trends = pd.read_sql(query, conn)
    
    if not time_trends.empty:
        time_trends['exam_date'] = pd.to_datetime(time_trends['exam_date'])
        fig = px.line(time_trends, x='exam_date', y='avg_performance',
                     title="Average Class Performance Over Time",
                     markers=True)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Score Distribution")
        query = "SELECT marks/max_marks*100 as percentage FROM marks"
        all_scores = pd.read_sql(query, conn)
        
        if not all_scores.empty:
            fig = px.histogram(all_scores, x='percentage', nbins=20,
                             title="Score Distribution", 
                             color_discrete_sequence=['lightblue'])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Exam Type Performance")
        query = """
            SELECT exam_type, AVG(marks/max_marks*100) as avg_score
            FROM marks
            GROUP BY exam_type
            ORDER BY avg_score DESC
        """
        exam_performance = pd.read_sql(query, conn)
        
        if not exam_performance.empty:
            fig = px.bar(exam_performance, x='exam_type', y='avg_score',
                        title="Performance by Exam Type",
                        color='avg_score', color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Export functionality
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export All Data (CSV)"):
            query = """
                SELECT s.name as student_name, sub.name as subject_name, 
                       m.marks, m.max_marks, m.marks/m.max_marks*100 as percentage,
                       m.exam_type, m.exam_date
                FROM marks m
                JOIN students s ON m.student_id = s.id
                JOIN subjects sub ON m.subject_id = sub.id
                ORDER BY s.name, sub.name, m.exam_date
            """
            export_data = pd.read_sql(query, conn)
            export_data['grade'] = export_data['percentage'].apply(calculate_grade)
            
            csv = export_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"student_performance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Export Summary Report"):
            # Create summary report
            summary_data = {}
            
            # Overall statistics
            total_students = pd.read_sql("SELECT COUNT(*) as count FROM students", conn)['count'].iloc[0]
            total_subjects = pd.read_sql("SELECT COUNT(*) as count FROM subjects", conn)['count'].iloc[0]
            total_assessments = pd.read_sql("SELECT COUNT(*) as count FROM marks", conn)['count'].iloc[0]
            avg_performance = pd.read_sql("SELECT AVG(marks/max_marks*100) as avg FROM marks", conn)['avg'].iloc[0]
            
            summary_data['overall'] = {
                'total_students': total_students,
                'total_subjects': total_subjects,
                'total_assessments': total_assessments,
                'average_performance': round(avg_performance, 2)
            }
            
            # Top students
            query = """
                SELECT s.name, AVG(m.marks/m.max_marks*100) as avg_score
                FROM students s
                JOIN marks m ON s.id = m.student_id
                GROUP BY s.id, s.name
                ORDER BY avg_score DESC
                LIMIT 10
            """
            top_students = pd.read_sql(query, conn)
            summary_data['top_students'] = top_students.to_dict('records')
            
            # Subject performance
            query = """
                SELECT sub.name, AVG(m.marks/m.max_marks*100) as avg_score
                FROM subjects sub
                JOIN marks m ON sub.id = m.subject_id
                GROUP BY sub.id, sub.name
                ORDER BY avg_score DESC
            """
            subject_performance = pd.read_sql(query, conn)
            summary_data['subject_performance'] = subject_performance.to_dict('records')
            
            summary_json = json.dumps(summary_data, indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=summary_json,
                file_name=f"performance_summary_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    conn.close()

if __name__ == "__main__":
    main()
