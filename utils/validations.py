"""
Validation utilities for the application
"""
import streamlit as st
from datetime import date
import re

def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> tuple:
    """Validate person/entity names"""
    errors = []

    if not name or not name.strip():
        errors.append("Name is required")
    else:
        name = name.strip()
        if len(name) < min_length:
            errors.append(f"Name must be at least {min_length} characters long")
        elif len(name) > max_length:
            errors.append(f"Name cannot exceed {max_length} characters")
        elif not re.match("^[a-zA-Z\s]+$", name):
            errors.append("Name can only contain letters and spaces")

    return len(errors) == 0, errors

def validate_class_section(class_name: str, section: str) -> tuple:
    """Validate class and section"""
    errors = []

    # Class validation
    if not class_name or not class_name.strip():
        errors.append("Class is required")
    elif len(class_name.strip()) > 10:
        errors.append("Class name too long")
    elif not re.match("^[a-zA-Z0-9\s]+$", class_name.strip()):
        errors.append("Class name contains invalid characters")

    # Section validation
    if not section or not section.strip():
        errors.append("Section is required")
    elif len(section.strip()) > 5:
        errors.append("Section name too long")
    elif not re.match("^[a-zA-Z0-9]+$", section.strip()):
        errors.append("Section can only contain letters and numbers")

    return len(errors) == 0, errors

def validate_date_of_birth(dob: date) -> tuple:
    """Validate date of birth"""
    errors = []

    if not dob:
        errors.append("Date of birth is required")
    elif dob >= date.today():
        errors.append("Date of birth must be in the past")
    elif dob < date(1900, 1, 1):
        errors.append("Date of birth is too old")
    elif (date.today() - dob).days < 365 * 3:  # Less than 3 years old
        errors.append("Student must be at least 3 years old")
    elif (date.today() - dob).days > 365 * 25:  # More than 25 years old
        errors.append("Student age seems too high for school")

    return len(errors) == 0, errors

def validate_marks(marks_obtained: int, max_marks: int) -> tuple:
    """Validate marks data"""
    errors = []

    # Marks obtained validation
    try:
        marks_obtained = int(marks_obtained)
        if marks_obtained < 0:
            errors.append("Marks cannot be negative")
    except (ValueError, TypeError):
        errors.append("Marks must be a valid number")
        return False, errors

    # Max marks validation
    try:
        max_marks = int(max_marks)
        if max_marks <= 0:
            errors.append("Maximum marks must be greater than 0")
        elif max_marks > 1000:
            errors.append("Maximum marks seems too high")
    except (ValueError, TypeError):
        errors.append("Maximum marks must be a valid number")
        return False, errors

    # Relationship validation
    if marks_obtained > max_marks:
        errors.append("Marks obtained cannot exceed maximum marks")

    return len(errors) == 0, errors

def validate_assessment_date(assessment_date: date) -> tuple:
    """Validate assessment date"""
    errors = []

    if not assessment_date:
        errors.append("Assessment date is required")
    elif assessment_date > date.today():
        errors.append("Assessment date cannot be in the future")
    elif assessment_date < date(2020, 1, 1):  # Reasonable minimum date
        errors.append("Assessment date is too old")

    return len(errors) == 0, errors

def sanitize_input(input_text: str) -> str:
    """Sanitize text input to prevent issues"""
    if not input_text:
        return ""

    # Remove extra whitespaces
    sanitized = " ".join(input_text.split())

    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>&"\']', '', sanitized)

    return sanitized

def validate_search_term(search_term: str) -> tuple:
    """Validate search input"""
    errors = []

    if search_term and len(search_term) > 100:
        errors.append("Search term too long")

    # Check for SQL injection patterns (basic)
    dangerous_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
    upper_search = search_term.upper() if search_term else ""

    for pattern in dangerous_patterns:
        if pattern in upper_search:
            errors.append("Invalid search term")
            break

    return len(errors) == 0, errors

def display_validation_errors(errors: list) -> None:
    """Display validation errors in Streamlit"""
    if errors:
        for error in errors:
            st.error(f"❌ {error}")

def validate_file_upload(uploaded_file, allowed_types: list = None, max_size_mb: float = 10) -> tuple:
    """Validate uploaded file"""
    errors = []

    if not uploaded_file:
        return True, errors  # No file is okay

    # Check file type
    if allowed_types:
        file_type = uploaded_file.type
        if file_type not in allowed_types:
            errors.append(f"File type {file_type} not allowed. Allowed types: {', '.join(allowed_types)}")

    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        errors.append(f"File size {file_size_mb:.1f}MB exceeds limit of {max_size_mb}MB")

    return len(errors) == 0, errors
