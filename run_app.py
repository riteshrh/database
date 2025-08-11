#!/usr/bin/env python3
"""
Startup script for Snowflake Natural Language Query Application

This script provides an easy way to launch different components of the application.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import snowflake.connector
        import openai
        import pandas
        import dotenv
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("Please create a .env file with your configuration")
        return False

def run_streamlit_app(app_file):
    """Run a Streamlit application"""
    try:
        print(f"🚀 Starting {app_file}...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {app_file}: {e}")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")

def main():
    """Main function"""
    print("❄️🏥 Snowflake Natural Language Query Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment file
    if not check_env_file():
        print("\n📝 Please create a .env file with the following variables:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("SNOWFLAKE_USER=your_snowflake_username")
        print("SNOWFLAKE_PASSWORD=your_snowflake_password")
        print("SNOWFLAKE_ACCOUNT=your_snowflake_account_identifier")
        print("SNOWFLAKE_WAREHOUSE=your_warehouse_name")
        print("SNOWFLAKE_DATABASE=userprofiles")
        print("SNOWFLAKE_SCHEMA=public")
        return
    
    print("\n🎯 Choose an application to run:")
    print("1. Main Application (General Query + NP Search)")
    print("2. General Query Interface Only")
    print("3. Nurse Practitioner Search Only")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                run_streamlit_app("main_app.py")
                break
            elif choice == "2":
                run_streamlit_app("app.py")
                break
            elif choice == "3":
                run_streamlit_app("nurse_practitioner_search.py")
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 