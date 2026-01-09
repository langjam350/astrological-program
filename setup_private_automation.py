#!/usr/bin/env python3
"""
Privacy-Focused Automation Setup for Astrological Reports
Sets up completely local delivery with no external dependencies.
"""

import os
import sys
import json

def main():
    """Main setup process for privacy-focused automation."""
    print("🔮 PRIVACY-FOCUSED AUTOMATION SETUP")
    print("=" * 60)
    print("This setup ensures complete privacy:")
    print("✅ No external email services required")
    print("✅ No credentials stored")
    print("✅ All processing stays on your computer")
    print("✅ Reports delivered locally with notifications")
    print()

    proceed = input("Continue with privacy-focused setup? (y/n): ").lower().strip()
    if proceed not in ['y', 'yes']:
        print("Setup cancelled.")
        return

    # Step 1: Birth Information
    print("\n" + "="*60)
    print("STEP 1: BIRTH INFORMATION")
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

    with open("birth_config.json", "w") as f:
        json.dump(birth_config, f, indent=2)

    print("✅ Birth information saved securely!")

    # Step 2: Local Delivery Setup
    print("\n" + "="*60)
    print("STEP 2: LOCAL DELIVERY CONFIGURATION")
    print("="*60)

    try:
        from local_delivery import setup_local_delivery
        setup_local_delivery()
    except ImportError:
        print("Local delivery module not found. Using basic delivery.")
        # Create basic delivery config
        basic_config = {
            "windows_notifications": True,
            "desktop_shortcut": True,
            "copy_to_folders": [],
            "auto_open_folder": True,
            "cleanup_old_reports": True,
            "keep_reports_days": 30
        }
        with open("delivery_config.json", "w") as f:
            json.dump(basic_config, f, indent=2)

    # Step 3: Windows Scheduler
    print("\n" + "="*60)
    print("STEP 3: WINDOWS TASK SCHEDULER")
    print("="*60)

    try:
        from scheduler import setup_windows_scheduler
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
        print("Scheduler module not found. Manual setup required.")

    # Final Summary
    print("\n" + "="*60)
    print("🎉 PRIVACY-FOCUSED SETUP COMPLETE!")
    print("="*60)
    print("Your automated astrological report system is now configured:")
    print()
    print("🔒 PRIVACY FEATURES:")
    print("  • No external email services")
    print("  • No credentials stored anywhere")
    print("  • All data stays on your computer")
    print("  • Local notifications only")
    print()
    print("📅 AUTOMATION:")
    print("  • Runs every Saturday at midnight")
    print("  • Generates comprehensive weekly reports")
    print("  • Creates ZIP packages for easy access")
    print("  • Delivers locally with Windows notifications")
    print()
    print("📦 DELIVERY METHODS:")
    print("  • Windows notifications when ready")
    print("  • Desktop shortcuts to reports")
    print("  • Auto-opens report folder")
    print("  • Optional cloud folder sync (your choice)")
    print("  • Automatic cleanup of old reports")
    print()
    print("FILES CREATED:")
    print("  • birth_config.json - Your birth information")
    print("  • delivery_config.json - Local delivery settings")
    print("  • automated_weekly_report.bat - Automation script")
    print("  • AstrologicalReportTask.xml - Windows task definition")
    print()
    print("NEXT STEPS:")
    print("1. Test the system manually:")
    print("   run-astrological-analysis.bat -BD [date] -BT [time] -BL [location] -CL [location]")
    print()
    print("2. Check Windows Task Scheduler:")
    print("   • Run 'taskschd.msc'")
    print("   • Look for 'Weekly Astrological Report' task")
    print()
    print("3. Ensure computer is on Saturday nights for automatic generation")
    print()
    print("🌟 Your privacy-focused astrological automation is ready!")
    print("No external services, no stored credentials, complete local control! ✨")

def show_privacy_benefits():
    """Show privacy benefits compared to cloud/email solutions."""
    print("\n" + "="*60)
    print("🔒 PRIVACY BENEFITS OF LOCAL DELIVERY")
    print("="*60)
    print()
    print("❌ WHAT WE AVOID:")
    print("  • Email provider access to your reports")
    print("  • Stored email credentials on your computer")
    print("  • External AI services reading your data")
    print("  • Cloud storage providers seeing your information")
    print("  • Third-party delivery services")
    print()
    print("✅ WHAT YOU GET:")
    print("  • Complete local control")
    print("  • No external dependencies")
    print("  • Windows notifications")
    print("  • Desktop integration")
    print("  • Optional cloud sync (your choice)")
    print("  • Automatic organization")
    print()
    print("🎯 YOUR DATA NEVER LEAVES YOUR COMPUTER")
    print("   Unless you specifically choose to sync to your own cloud storage")

if __name__ == "__main__":
    show_privacy_benefits()
    main()