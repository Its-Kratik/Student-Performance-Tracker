#!/usr/bin/env python3
"""
Installation script for Student Performance Tracker
Handles Python 3.13 compatibility issues
"""
import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("🎓 Student Performance Tracker - Installation Script")
    print("=" * 60)
    print(f"Python version: {sys.version}")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)

    # For Python 3.13, we need to handle some dependencies carefully
    if sys.version_info >= (3, 13):
        print("⚠️  Python 3.13 detected - using compatible package versions")

        # Install packages one by one to handle conflicts
        packages = [
            "streamlit==1.37.0",
            "pandas==2.2.2", 
            "altair==5.3.0",
            "plotly==5.22.0",
            "fpdf2==2.7.9"
        ]

        # Optional packages that might have issues
        optional_packages = [
            "mysql-connector-python==9.0.0",
            "reportlab==4.2.2",
            "streamlit-extras==0.4.3",
            "Pillow==10.4.0",
            "openpyxl==3.1.5",
            "matplotlib==3.9.1"
        ]

        print("\n📦 Installing core packages...")
        for package in packages:
            print(f"Installing {package}...")
            success, output = run_command(f"pip install {package}")
            if success:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}: {output}")

        print("\n📦 Installing optional packages...")
        for package in optional_packages:
            print(f"Installing {package}...")
            success, output = run_command(f"pip install {package}")
            if success:
                print(f"✅ {package} installed successfully")
            else:
                print(f"⚠️  {package} failed (optional): {output}")

    else:
        # For older Python versions, try regular requirements
        print("📦 Installing all requirements...")
        success, output = run_command("pip install -r requirements.txt")
        if success:
            print("✅ All requirements installed successfully")
        else:
            print(f"❌ Installation failed: {output}")
            print("\nTrying minimal requirements...")
            success2, output2 = run_command("pip install -r requirements-minimal.txt")
            if success2:
                print("✅ Minimal requirements installed")
            else:
                print(f"❌ Minimal installation also failed: {output2}")
                sys.exit(1)

    print("\n🧪 Testing installation...")

    # Test imports
    test_imports = [
        ("streamlit", "Streamlit web framework"),
        ("pandas", "Data processing"),
        ("altair", "Charts and visualization"),
        ("plotly", "Interactive charts")
    ]

    failed_imports = []

    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description} - OK")
        except ImportError:
            print(f"❌ {description} - FAILED")
            failed_imports.append(module)

    # Test optional imports
    optional_imports = [
        ("mysql.connector", "MySQL database support"),
        ("fpdf", "PDF generation"),
        ("matplotlib", "Additional charts")
    ]

    for module, description in optional_imports:
        try:
            __import__(module)
            print(f"✅ {description} - OK")
        except ImportError:
            print(f"⚠️  {description} - Not available (optional)")

    if failed_imports:
        print(f"\n❌ Critical modules failed to install: {', '.join(failed_imports)}")
        print("The application may not work properly.")
        sys.exit(1)
    else:
        print("\n🎉 Installation completed successfully!")
        print("\nYou can now run the application with:")
        print("python start.py")
        print("or")
        print("streamlit run app.py")

if __name__ == "__main__":
    main()
