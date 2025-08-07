<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 🎓 Student Performance Tracker

[
[
[
[

> **A comprehensive web-based application for tracking and analyzing student academic performance with interactive dashboards, detailed analytics, and automated reporting capabilities.**

## 🚀 Live Demo

**[🌐 Access the Application](https://student-performance-tracker.streamlit.app/)**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)


## 🎯 Overview

The **Student Performance Tracker** is a modern, intuitive web application designed to help educators, administrators, and institutions efficiently manage and analyze student academic performance. Built with Streamlit and powered by SQLite, it provides real-time insights, comprehensive reporting, and data-driven decision-making capabilities.

### 🎨 Key Highlights

- **🔄 Real-time Analytics**: Live performance dashboards and insights
- **📊 Interactive Visualizations**: Charts, graphs, and visual reports
- **🎯 Automated Grading**: Intelligent grade calculation and classification
- **📱 Responsive Design**: Works seamlessly across all devices
- **⚡ Fast Performance**: Optimized SQLite database with caching
- **🛡️ Data Validation**: Comprehensive input validation and error handling


## ✨ Features

### 👥 **Student Management**

- ✅ Complete CRUD operations (Create, Read, Update, Delete)
- ✅ Advanced search and filtering capabilities
- ✅ Bulk import/export functionality
- ✅ Student profile management with personal details
- ✅ Class and section organization


### 📚 **Subject Management**

- ✅ Dynamic subject creation and management
- ✅ Quick-add subject functionality
- ✅ Subject-wise performance tracking
- ✅ Curriculum organization tools


### 📝 **Marks \& Assessment Management**

- ✅ Flexible marks entry with multiple assessment types
- ✅ Real-time grade calculation (A+, A, B+, B, C+, C, F)
- ✅ Percentage calculation and validation
- ✅ Assessment date tracking
- ✅ Bulk marks import capabilities


### 📋 **Report Cards \& Analytics**

- ✅ Individual student report cards
- ✅ Class-wise performance analytics
- ✅ Subject-wise comparison reports
- ✅ Grade distribution analysis
- ✅ Pass/fail rate tracking
- ✅ Top performers identification


### 📊 **Visual Reports \& Dashboards**

- ✅ Interactive performance dashboards
- ✅ Real-time charts and graphs
- ✅ Trend analysis and insights
- ✅ Comparative analytics
- ✅ Performance metrics visualization


### 📤 **Data Export \& Backup**

- ✅ CSV export for all data types
- ✅ PDF report generation (coming soon)
- ✅ Automated backup system
- ✅ Data import/export tools
- ✅ Archive and restore functionality


### ⚙️ **System Management**

- ✅ Application settings and preferences
- ✅ Database management tools
- ✅ Sample data generation
- ✅ System information and statistics
- ✅ Performance optimization


## 🛠️ Tech Stack

### **Frontend**

- **[Streamlit](https://streamlit.io/)** - Modern web app framework
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[Plotly](https://plotly.com/)** - Interactive visualizations


### **Backend**

- **[Python 3.8+](https://www.python.org/)** - Core programming language
- **[SQLite](https://www.sqlite.org/)** - Lightweight database engine


### **Development Tools**

- **Git** - Version control
- **GitHub** - Code repository
- **Streamlit Cloud** - Deployment platform


## 🚀 Installation

### **Prerequisites**

- Python 3.8 or higher
- Git (for cloning the repository)


### **Quick Start**

1. **Clone the Repository**

```bash
git clone https://github.com/Its-Kratik/student-performance-tracker.git
cd student-performance-tracker
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the Application**

```bash
streamlit run app.py
```

4. **Access the Application**
    - Open your browser and navigate to `http://localhost:8501`
    - The database will be automatically initialized with sample data

### **Alternative Setup**

**Using the Quick Launcher:**

```bash
python run.py
```

**Manual Dependency Installation:**

```bash
pip install streamlit pandas plotly sqlite3
```


## 📖 Usage Guide

### **Getting Started**

1. **🏠 Dashboard**: Overview of system statistics and quick actions
2. **👥 Manage Students**: Add, edit, delete, and search students
3. **📚 Manage Subjects**: Create and organize subject curriculum
4. **📝 Enter Marks**: Input student assessments and grades
5. **📋 Report Cards**: Generate individual student reports
6. **📊 Class Analytics**: Analyze class and section performance
7. **📈 Visual Reports**: Interactive charts and insights
8. **⚙️ Settings**: Configure application preferences

### **Sample Workflow**

```
1. Add Students → 2. Create Subjects → 3. Enter Marks → 4. Generate Reports
```


### **Key Operations**

- **Adding a Student**: Navigate to "Manage Students" → Click "Add New Student"
- **Entering Marks**: Go to "Enter Marks" → Select student and subject → Input scores
- **Viewing Analytics**: Access "Class Analytics" → Select class/section → View insights
- **Exporting Data**: Use export buttons in any section → Download CSV files


## 📁 Project Structure

```
student-performance-tracker/
├── 📄 app.py                    # Main application entry point
├── 📂 pages/                    # Streamlit pages
│   ├── 1_Manage_Students.py     # Student management interface
│   ├── 2_Manage_Subjects.py     # Subject management interface
│   ├── 3_Enter_Update_Marks.py  # Marks entry and updating
│   ├── 4_Student_Report_Card.py # Individual report generation
│   ├── 5_Class_Analytics.py     # Class performance analytics
│   ├── 6_Visual_Reports.py      # Interactive visual dashboards
│   └── 7_Settings.py            # Application configuration
├── 📂 models/                   # Data models and business logic
│   ├── student.py               # Student model and operations
│   ├── subject.py               # Subject model and operations
│   └── marks.py                 # Marks model and calculations
├── 📂 db/                       # Database layer
│   └── connection.py            # SQLite connection and utilities
├── 📂 utils/                    # Utility functions
│   └── analytics.py             # Advanced analytics functions
├── 📂 tests/                    # Test suite
│   └── test_cases.py            # Unit and integration tests
├── 📄 requirements.txt          # Python dependencies
├── 📄 run.py                    # Quick launcher script
├── 📄 README.md                 # Project documentation
└── 📄 student_tracker.db        # SQLite database (auto-generated)
```


## 🔧 API Documentation

### **Database Models**

#### **Student Model**

```python
Student {
    student_id: Integer (Primary Key)
    name: String (Required)
    class: String (Required)
    section: String (Required)
    dob: Date
    created_at: Timestamp
}
```


#### **Subject Model**

```python
Subject {
    subject_id: Integer (Primary Key)
    subject_name: String (Unique, Required)
    created_at: Timestamp
}
```


#### **Marks Model**

```python
Marks {
    mark_id: Integer (Primary Key)
    student_id: Integer (Foreign Key)
    subject_id: Integer (Foreign Key)
    marks_obtained: Integer (Required)
    max_marks: Integer (Default: 100)
    assessment_date: Date
    assessment_type: String (Default: 'Assignment')
    created_at: Timestamp
}
```


### **Grade Calculation System**

| Percentage Range | Grade |
| :-- | :-- |
| 90% - 100% | A+ |
| 80% - 89% | A |
| 70% - 79% | B+ |
| 60% - 69% | B |
| 50% - 59% | C+ |
| 40% - 49% | C |
| Below 40% | F |

## 📸 Screenshots

### **Dashboard Overview**

> *Main dashboard showing system statistics and quick access buttons*

### **Student Management**

> *Comprehensive student CRUD interface with search and filtering*

### **Class Analytics**

> *Performance analytics with charts, metrics, and insights*

### **Visual Reports**

> *Interactive dashboards with real-time data visualization*

## 🤝 Contributing

We welcome contributions to improve the Student Performance Tracker! Here's how you can help:

### **Getting Started**

1. **Fork the Repository**

```bash
git fork https://github.com/Its-Kratik/student-performance-tracker.git
```

2. **Create a Feature Branch**

```bash
git checkout -b feature/amazing-feature
```

3. **Make Your Changes**
    - Follow Python PEP 8 style guidelines
    - Add tests for new functionality
    - Update documentation as needed
4. **Commit Your Changes**

```bash
git commit -m "Add amazing feature"
```

5. **Push to Your Branch**

```bash
git push origin feature/amazing-feature
```

6. **Open a Pull Request**

### **Development Guidelines**

- **Code Style**: Follow PEP 8 conventions
- **Testing**: Add unit tests for new features
- **Documentation**: Update README and inline docs
- **Commits**: Use clear, descriptive commit messages


### **Areas for Contribution**

- 🔧 **New Features**: Additional analytics, reporting capabilities
- 🐛 **Bug Fixes**: Identify and resolve issues
- 📚 **Documentation**: Improve guides and examples
- 🎨 **UI/UX**: Enhance user interface and experience
- ⚡ **Performance**: Optimize database queries and rendering


## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Kratik Jain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```


## 🙋♂️ Contact

**Kratik Jain** - *Full Stack Developer \& Data Enthusiast*

- 📧 **Email**: [kratikjain121@gmail.com](mailto:kratikjain121@gmail.com)
- 📱 **Phone**: [+91 7410990404](tel:+917410990404)
- 💼 **LinkedIn**: [kratik-jain12](https://www.linkedin.com/in/kratik-jain12/)
- 🔗 **GitHub**: [Its-Kratik](https://github.com/Its-Kratik)
- 🌐 **Live App**: [Student Performance Tracker](https://student-performance-tracker.streamlit.app/)


## 🙏 Acknowledgments

- **[Streamlit Team](https://streamlit.io/)** for the amazing framework
- **[SQLite](https://www.sqlite.org/)** for the reliable database engine
- **[Pandas](https://pandas.pydata.org/)** for powerful data manipulation
- **[Plotly](https://plotly.com/)** for interactive visualizations
- **Open Source Community** for inspiration and support


## 🔮 Future Roadmap

### **Phase 1 - Enhanced Analytics**

- [ ] Advanced statistical analysis
- [ ] Predictive performance modeling
- [ ] Comparative benchmarking


### **Phase 2 - Extended Features**

- [ ] PDF report generation
- [ ] Email notification system
- [ ] Multi-language support
- [ ] Advanced user roles and permissions


### **Phase 3 - Integration \& APIs**

- [ ] REST API development
- [ ] Third-party integrations
- [ ] Mobile application
- [ ] Cloud storage integration


## ⭐ Show Your Support

If you find this project helpful, please consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** issues and bugs
- 💡 **Suggesting** new features
- 🤝 **Contributing** to the codebase
- 📢 **Sharing** with others

<div align="center">

**Built with ❤️ by [Kratik Jain](https://github.com/Its-Kratik)**

[

*Making education data-driven, one student at a time* 📚✨

</div>
<div style="text-align: center">⁂</div>

[^1]: https://github.com/Its-Kratik

