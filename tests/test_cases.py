"""
Test Cases for Student Performance Tracker
This file contains unit tests and test cases for the application
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.student import Student
from models.subject import Subject
from models.marks import Marks
from utils.validations import validate_name, validate_class_section, validate_marks

class TestStudentModel(unittest.TestCase):
    """Test cases for Student model"""

    def test_validate_student_data(self):
        """Test student data validation"""
        from datetime import date

        # Valid data
        valid, errors = Student.validate_student_data("John Doe", "10", "A", date(2008, 5, 20))
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid name (too short)
        valid, errors = Student.validate_student_data("J", "10", "A", date(2008, 5, 20))
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid date (future)
        valid, errors = Student.validate_student_data("John Doe", "10", "A", date(2030, 5, 20))
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

class TestSubjectModel(unittest.TestCase):
    """Test cases for Subject model"""

    def test_validate_subject_data(self):
        """Test subject data validation"""
        # Valid subject name
        valid, errors = Subject.validate_subject_data("Mathematics")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid subject name (too short)
        valid, errors = Subject.validate_subject_data("M")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid subject name (too long)
        valid, errors = Subject.validate_subject_data("A" * 51)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

class TestMarksModel(unittest.TestCase):
    """Test cases for Marks model"""

    def test_calculate_percentage(self):
        """Test percentage calculation"""
        # Normal case
        percentage = Marks.calculate_percentage(78, 100)
        self.assertEqual(percentage, 78.0)

        # Perfect score
        percentage = Marks.calculate_percentage(100, 100)
        self.assertEqual(percentage, 100.0)

        # Zero marks
        percentage = Marks.calculate_percentage(0, 100)
        self.assertEqual(percentage, 0.0)

        # Edge case: zero max marks
        percentage = Marks.calculate_percentage(50, 0)
        self.assertEqual(percentage, 0.0)

    def test_calculate_grade(self):
        """Test grade calculation"""
        # A+ grade
        grade = Marks.calculate_grade(95)
        self.assertEqual(grade, "A+")

        # A grade
        grade = Marks.calculate_grade(85)
        self.assertEqual(grade, "A")

        # B+ grade
        grade = Marks.calculate_grade(75)
        self.assertEqual(grade, "B+")

        # B grade
        grade = Marks.calculate_grade(65)
        self.assertEqual(grade, "B")

        # C+ grade
        grade = Marks.calculate_grade(55)
        self.assertEqual(grade, "C+")

        # C grade
        grade = Marks.calculate_grade(45)
        self.assertEqual(grade, "C")

        # F grade
        grade = Marks.calculate_grade(35)
        self.assertEqual(grade, "F")

    def test_validate_marks_data(self):
        """Test marks data validation"""
        from datetime import date

        # Valid marks
        valid, errors = Marks.validate_marks_data(78, 100, date.today())
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid marks (negative)
        valid, errors = Marks.validate_marks_data(-10, 100, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid marks (exceeds max)
        valid, errors = Marks.validate_marks_data(120, 100, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid max marks (zero)
        valid, errors = Marks.validate_marks_data(50, 0, date.today())
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

class TestValidationUtils(unittest.TestCase):
    """Test cases for validation utilities"""

    def test_validate_name(self):
        """Test name validation"""
        # Valid name
        valid, errors = validate_name("John Doe")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid name (too short)
        valid, errors = validate_name("J")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid name (numbers)
        valid, errors = validate_name("John123")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_validate_class_section(self):
        """Test class and section validation"""
        # Valid class and section
        valid, errors = validate_class_section("10", "A")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid class (empty)
        valid, errors = validate_class_section("", "A")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid section (empty)
        valid, errors = validate_class_section("10", "")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_validate_marks(self):
        """Test marks validation"""
        # Valid marks
        valid, errors = validate_marks(78, 100)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # Invalid marks (negative)
        valid, errors = validate_marks(-10, 100)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

        # Invalid marks (exceeds max)
        valid, errors = validate_marks(120, 100)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios"""

    def test_complete_student_workflow(self):
        """Test complete student management workflow"""
        # This would require database setup for full testing
        # For now, we'll test the data processing logic

        # Sample student data
        student_summary = {
            'student_name': 'John Doe',
            'total_subjects': 5,
            'total_marks_obtained': 400,
            'total_max_marks': 500,
            'overall_percentage': 80.0,
            'overall_grade': 'A',
            'subject_details': [
                {
                    'subject': 'Mathematics',
                    'marks_obtained': 85,
                    'max_marks': 100,
                    'percentage': 85.0,
                    'grade': 'A',
                    'assessment_date': '2024-01-15',
                    'assessment_type': 'Final'
                },
                {
                    'subject': 'Physics',
                    'marks_obtained': 78,
                    'max_marks': 100,
                    'percentage': 78.0,
                    'grade': 'B+',
                    'assessment_date': '2024-01-16',
                    'assessment_type': 'Final'
                }
            ],
            'pass_fail_status': 'Pass'
        }

        # Test calculations
        expected_percentage = (400 / 500) * 100
        self.assertEqual(student_summary['overall_percentage'], expected_percentage)

        # Test grade assignment
        expected_grade = Marks.calculate_grade(80.0)
        self.assertEqual(student_summary['overall_grade'], expected_grade)

        # Test pass/fail status
        self.assertEqual(student_summary['pass_fail_status'], 'Pass')

    def test_class_analytics_calculations(self):
        """Test class analytics calculations"""
        # Sample class data
        students_data = [
            {'name': 'Student A', 'percentage': 85.0, 'grade': 'A'},
            {'name': 'Student B', 'percentage': 75.0, 'grade': 'B+'},
            {'name': 'Student C', 'percentage': 65.0, 'grade': 'B'},
            {'name': 'Student D', 'percentage': 55.0, 'grade': 'C+'},
            {'name': 'Student E', 'percentage': 35.0, 'grade': 'F'}
        ]

        # Calculate class average
        total_percentage = sum(student['percentage'] for student in students_data)
        class_average = total_percentage / len(students_data)
        expected_average = 63.0

        self.assertEqual(class_average, expected_average)

        # Calculate pass rate
        passing_students = sum(1 for student in students_data if student['percentage'] >= 40)
        pass_rate = (passing_students / len(students_data)) * 100
        expected_pass_rate = 80.0  # 4 out of 5 students passing

        self.assertEqual(pass_rate, expected_pass_rate)

    def test_grade_distribution(self):
        """Test grade distribution calculations"""
        # Sample grade data
        grades = ['A+', 'A', 'A', 'B+', 'B+', 'B', 'C+', 'C', 'F', 'F']

        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        expected_counts = {
            'A+': 1,
            'A': 2, 
            'B+': 2,
            'B': 1,
            'C+': 1,
            'C': 1,
            'F': 2
        }

        self.assertEqual(grade_counts, expected_counts)

        # Test percentage calculations
        total_students = len(grades)
        a_percentage = (grade_counts.get('A+', 0) + grade_counts.get('A', 0)) / total_students * 100
        expected_a_percentage = 30.0  # 3 out of 10 students

        self.assertEqual(a_percentage, expected_a_percentage)

def run_all_tests():
    """Run all test cases"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestStudentModel,
        TestSubjectModel, 
        TestMarksModel,
        TestValidationUtils,
        TestIntegrationScenarios
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result

if __name__ == "__main__":
    # Sample test data for manual testing
    print("🧪 Student Performance Tracker - Test Cases")
    print("=" * 50)

    # Test grade calculation
    print("\n1. Testing Grade Calculations:")
    test_percentages = [95, 85, 75, 65, 55, 45, 35]
    for percentage in test_percentages:
        grade = Marks.calculate_grade(percentage)
        print(f"   {percentage}% → Grade: {grade}")

    # Test percentage calculation
    print("\n2. Testing Percentage Calculations:")
    test_marks = [(78, 100), (85, 100), (45, 50), (0, 100)]
    for obtained, maximum in test_marks:
        percentage = Marks.calculate_percentage(obtained, maximum)
        print(f"   {obtained}/{maximum} → {percentage}%")

    # Test validation functions
    print("\n3. Testing Validation Functions:")
    test_names = ["John Doe", "J", "John123", ""]
    for name in test_names:
        valid, errors = validate_name(name)
        status = "✅ Valid" if valid else f"❌ Invalid: {', '.join(errors)}"
        print(f"   Name '{name}' → {status}")

    print("\n4. Running Unit Tests:")
    print("-" * 30)

    # Run unit tests
    result = run_all_tests()

    print(f"\n📊 Test Results:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
