#!/usr/bin/env python3
"""
Complete Automation Setup for Astrological Reports
Sets up email and Windows scheduling in one go.
"""

import os
import sys

def main():
    """Main setup process."""
    print("🔮 COMPLETE AUTOMATION SETUP")
    print("=" * 60)
    print("This will set up:")
    print("1. Email configuration for report delivery")
    print("2. Windows Task Scheduler for automatic weekly generation")
    print("3. Birth information configuration")
    print()

    proceed = input("Continue with setup? (y/n): ").lower().strip()
    if proceed not in ['y', 'yes']:
        print("Setup cancelled.")
        return

    # Step 1: Email Setup
    print("\n" + "="*60)
    print("STEP 1: EMAIL CONFIGURATION")
    print("="*60)

    try:
        from email_sender import setup_email_interactive
        setup_email_interactive()
    except ImportError:
        print("Email module not found. Please ensure email_sender.py exists.")
        return

    # Step 2: Birth Information
    print("\n" + "="*60)
    print("STEP 2: BIRTH INFORMATION")
    print("="*60)

    birth_date = input("Your birth date (YYYY-MM-DD): ").strip()
    birth_time = input("Your birth time (HH:MM, 24-hour format): ").strip()
    birth_location = input("Your birth location (City;State): ").strip()
    current_location = input("Your current location (City;State): ").strip()

    if not all([birth_date, birth_time, birth_location, current_location]):
        print("❌ Invalid birth information. Setup incomplete.")
        return

    # Save birth info to config file
    birth_config = {
        "birth_date": birth_date,
        "birth_time": birth_time,
        "birth_location": birth_location,
        "current_location": current_location
    }

    import json
    with open("birth_config.json", "w") as f:
        json.dump(birth_config, f, indent=2)

    print("✅ Birth information saved!")

    # Step 3: Windows Scheduler
    print("\n" + "="*60)
    print("STEP 3: WINDOWS TASK SCHEDULER")
    print("="*60)

    try:
        from scheduler import setup_windows_scheduler, update_birth_info_in_script
        setup_windows_scheduler()

        # Update the automation script with the birth info
        try:
            with open("automated_weekly_report.bat", "r") as f:
                content = f.read()

            old_line = 'python astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA"'
            new_line = f'python astrological_analyzer.py {birth_date} {birth_time} "{birth_location}" "{current_location}"'

            content = content.replace(old_line, new_line)

            with open("automated_weekly_report.bat", "w") as f:
                f.write(content)

            print("✅ Automation script updated with your birth information!")

        except Exception as e:
            print(f"⚠️  Could not update automation script: {e}")

    except ImportError:
        print("Scheduler module not found. Please ensure scheduler.py exists.")

    # Final Summary
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("Your automated astrological report system is now configured:")
    print()
    print("📧 Email: Reports will be sent to langjam350@gmail.com")
    print("⏰ Schedule: Every Saturday at midnight")
    print("📊 Content: Weekly forecasts, charts, and AI-enhanced reports")
    print("🔒 Privacy: All processing happens locally on your computer")
    print()
    print("Next steps:")
    print("1. Test the system: Run the automation script manually")
    print("2. Check Task Scheduler to verify the task was created")
    print("3. Ensure your computer is on Saturday nights for automatic generation")
    print()
    print("Files created:")
    print("• email_config.json - Email settings")
    print("• birth_config.json - Your birth information")
    print("• automated_weekly_report.bat - Automation script")
    print("• AstrologicalReportTask.xml - Windows task definition")
    print()
    print("Enjoy your automated weekly astrological insights! ✨")

if __name__ == "__main__":
    main()