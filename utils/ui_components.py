"""
UI Components and helper utilities for Streamlit
"""
import streamlit as st
import time
from typing import List, Dict, Any
import pandas as pd

def display_loading_spinner(message: str = "Loading..."):
    """Display loading spinner with message"""
    return st.spinner(message)

def paginate_data(data: List[Any], page_size: int = 10, page_key: str = "page") -> tuple:
    """Paginate data for display"""
    if not data:
        return [], 0, 0, 0

    total_items = len(data)
    total_pages = (total_items + page_size - 1) // page_size

    # Get current page from session state
    if f"{page_key}_current" not in st.session_state:
        st.session_state[f"{page_key}_current"] = 1

    current_page = st.session_state[f"{page_key}_current"]

    # Ensure current page is within bounds
    current_page = max(1, min(current_page, total_pages))
    st.session_state[f"{page_key}_current"] = current_page

    # Calculate start and end indices
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    # Get paginated data
    paginated_data = data[start_idx:end_idx]

    return paginated_data, current_page, total_pages, total_items

def display_pagination_controls(current_page: int, total_pages: int, page_key: str = "page") -> None:
    """Display pagination controls"""
    if total_pages <= 1:
        return

    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("⏮️ First", disabled=(current_page == 1), key=f"{page_key}_first"):
            st.session_state[f"{page_key}_current"] = 1
            st.rerun()

    with col2:
        if st.button("◀️ Prev", disabled=(current_page == 1), key=f"{page_key}_prev"):
            st.session_state[f"{page_key}_current"] = max(1, current_page - 1)
            st.rerun()

    with col3:
        st.write(f"Page {current_page} of {total_pages}")

    with col4:
        if st.button("Next ▶️", disabled=(current_page == total_pages), key=f"{page_key}_next"):
            st.session_state[f"{page_key}_current"] = min(total_pages, current_page + 1)
            st.rerun()

    with col5:
        if st.button("Last ⏭️", disabled=(current_page == total_pages), key=f"{page_key}_last"):
            st.session_state[f"{page_key}_current"] = total_pages
            st.rerun()

def create_search_filters() -> Dict[str, Any]:
    """Create search and filter components"""
    filters = {}

    with st.expander("🔍 Search & Filters"):
        col1, col2, col3 = st.columns(3)

        with col1:
            filters['search_term'] = st.text_input(
                "Search by name", 
                placeholder="Enter student/subject name..."
            )

        with col2:
            filters['class_filter'] = st.selectbox(
                "Filter by Class", 
                options=["All", "10", "11", "12"],
                index=0
            )

        with col3:
            filters['section_filter'] = st.selectbox(
                "Filter by Section",
                options=["All", "A", "B", "C"],
                index=0
            )

    # Convert "All" to empty string for database queries
    for key in ['class_filter', 'section_filter']:
        if filters[key] == "All":
            filters[key] = ""

    return filters

def display_success_message(message: str, duration: int = 3) -> None:
    """Display success message with auto-hide"""
    success_placeholder = st.success(message)
    time.sleep(duration)
    success_placeholder.empty()

def display_error_message(message: str) -> None:
    """Display error message"""
    st.error(message)

def create_confirmation_dialog(message: str, key: str) -> bool:
    """Create a confirmation dialog"""
    if f"confirm_{key}" not in st.session_state:
        st.session_state[f"confirm_{key}"] = False

    if not st.session_state[f"confirm_{key}"]:
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes", key=f"yes_{key}"):
                st.session_state[f"confirm_{key}"] = True
                st.rerun()
        with col2:
            if st.button("❌ No", key=f"no_{key}"):
                return False
        return False
    else:
        return True

def create_data_table(data: List[Dict], columns: List[str], title: str = "") -> None:
    """Create a formatted data table"""
    if not data:
        st.info(f"No {title.lower()} found")
        return

    df = pd.DataFrame(data)

    if title:
        st.subheader(title)

    st.dataframe(
        df[columns] if columns else df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(f"Total records: {len(data)}")

def create_metric_cards(metrics: Dict[str, Any]) -> None:
    """Create metric cards display"""
    if not metrics:
        return

    num_metrics = len(metrics)
    cols = st.columns(min(4, num_metrics))

    for i, (label, value) in enumerate(metrics.items()):
        with cols[i % len(cols)]:
            if isinstance(value, dict) and 'value' in value:
                st.metric(label, value['value'], value.get('delta'))
            else:
                st.metric(label, value)

def create_status_badge(status: str, percentage: float = None) -> str:
    """Create colored status badge"""
    if status.lower() == "pass" or (percentage is not None and percentage >= 40):
        return "🟢 Pass"
    elif status.lower() == "fail" or (percentage is not None and percentage < 40):
        return "🔴 Fail"
    else:
        return f"⚪ {status}"

def create_grade_badge(grade: str) -> str:
    """Create colored grade badge"""
    grade_colors = {
        "A+": "🟢",
        "A": "🟢", 
        "B+": "🔵",
        "B": "🔵",
        "C+": "🟡",
        "C": "🟡",
        "F": "🔴"
    }
    return f"{grade_colors.get(grade, '⚪')} {grade}"

def display_data_summary(data: List[Any], entity_name: str) -> None:
    """Display summary information about data"""
    if not data:
        st.info(f"No {entity_name} available")
        return

    total_count = len(data)
    st.info(f"📊 Total {entity_name}: **{total_count}**")

def create_export_section() -> Dict[str, str]:
    """Create export options section"""
    export_options = {}

    with st.expander("📥 Export Options"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Export to PDF", use_container_width=True):
                export_options['format'] = 'pdf'

        with col2:
            if st.button("📊 Export to CSV", use_container_width=True):
                export_options['format'] = 'csv'

    return export_options

def display_app_info() -> None:
    """Display application information"""
    with st.expander("ℹ️ About This Application"):
        st.markdown("""
        ### Student Performance Tracker

        This application helps manage and analyze student academic performance with features including:

        - **Student Management**: Add, edit, and manage student records
        - **Subject Management**: Organize subjects and curriculum
        - **Marks Entry**: Record and track assessment results
        - **Analytics**: Generate performance insights and reports
        - **Visualizations**: Interactive charts and graphs
        - **Export**: PDF reports and CSV data export

        **Technology Stack**: Python, Streamlit, MySQL, Pandas, Altair

        **Version**: 1.0.0
        """)

def create_sidebar_navigation() -> str:
    """Create sidebar navigation"""
    with st.sidebar:
        st.title("🎓 Student Tracker")

        nav_options = [
            "🏠 Dashboard",
            "👥 Manage Students", 
            "📚 Manage Subjects",
            "📝 Enter Marks",
            "📋 Report Cards",
            "📊 Analytics",
            "📈 Visual Reports",
            "⚙️ Settings"
        ]

        selected = st.radio("Navigation", nav_options)

        st.markdown("---")
        display_app_info()

        return selected

def create_theme_toggle():
    """Create theme toggle (placeholder for future implementation)"""
    with st.sidebar:
        st.markdown("---")
        theme = st.selectbox("🎨 Theme", ["Light", "Dark", "Auto"])
        return theme

class SessionStateManager:
    """Manage Streamlit session state"""

    @staticmethod
    def initialize_session_state():
        """Initialize required session state variables"""
        default_states = {
            'current_page': 1,
            'search_term': '',
            'selected_class': '',
            'selected_section': '',
            'show_success': False,
            'last_operation': None
        }

        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def clear_session_state():
        """Clear all session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    @staticmethod
    def get_state(key: str, default=None):
        """Get session state value"""
        return st.session_state.get(key, default)

    @staticmethod
    def set_state(key: str, value):
        """Set session state value"""
        st.session_state[key] = value

# Initialize session state when module is imported
SessionStateManager.initialize_session_state()
