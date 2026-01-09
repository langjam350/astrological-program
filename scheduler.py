#!/usr/bin/env python3
"""
Windows Task Scheduler for Astrological Reports
Sets up automated weekly report generation and email delivery.
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def create_automated_script():
    """Create the automation script that will be scheduled."""
    script_content = '''@echo off
cd /d "%~dp0"

echo Starting automated weekly astrological report generation...
echo Time: %date% %time%

REM Run the astrological analyzer with your birth details
REM You'll need to update these parameters with your actual birth information
python astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA"

if %errorlevel% equ 0 (
    echo Report generation completed successfully

    REM Process local delivery if configured
    python -c "
from local_delivery import LocalDeliveryManager
from pathlib import Path
import os
import datetime

try:
    delivery_manager = LocalDeliveryManager()

    # Find the most recent ZIP file in tosend folder
    tosend_path = Path('tosend')
    if tosend_path.exists():
        zip_files = list(tosend_path.glob('*.zip'))
        if zip_files:
            latest_zip = max(zip_files, key=os.path.getctime)
            week_info = f'Generated on {datetime.datetime.now().strftime(\"%%B %%d, %%Y\")}'
            delivery_manager.deliver_report(str(latest_zip), week_info)
            print('Report delivered successfully via local delivery system')
        else:
            print('No ZIP files found for delivery')
    else:
        print('tosend folder not found')
except ImportError:
    print('Local delivery not available - reports saved in tosend/ folder only')
except Exception as e:
    print(f'Delivery failed: {e}')
"
) else (
    echo Report generation failed with error level %errorlevel%
)

echo Automated task completed at %date% %time%
'''

    with open("automated_weekly_report.bat", "w") as f:
        f.write(script_content)

    return "automated_weekly_report.bat"

def create_task_scheduler_xml():
    """Create XML file for Windows Task Scheduler."""
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "automated_weekly_report.bat")

    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2023-12-01T00:00:00</Date>
    <Author>Astrological Program</Author>
    <Description>Automated weekly astrological report generation and email delivery</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2023-12-02T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <WeeksInterval>1</WeeksInterval>
        <DaysOfWeek>
          <Saturday />
        </DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{script_path}</Command>
      <WorkingDirectory>{current_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    with open("AstrologicalReportTask.xml", "w", encoding="utf-16") as f:
        f.write(xml_content)

    return "AstrologicalReportTask.xml"

def setup_windows_scheduler():
    """Set up Windows Task Scheduler for automated reports."""
    print("🔮 Setting up Windows Task Scheduler")
    print("=" * 50)

    try:
        # Create the automation script
        script_file = create_automated_script()
        print(f"✅ Created automation script: {script_file}")

        # Create the task XML
        xml_file = create_task_scheduler_xml()
        print(f"✅ Created task definition: {xml_file}")

        print("\n🔧 Setting up automated task...")
        print("This will create a Windows scheduled task that runs every Saturday at midnight.")

        # Import the task using schtasks
        cmd = f'schtasks /create /xml "{xml_file}" /tn "Weekly Astrological Report"'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Scheduled task created successfully!")
            print("\nTask Details:")
            print("• Name: Weekly Astrological Report")
            print("• Schedule: Every Saturday at midnight")
            print("• Action: Generate report and email if configured")
            print("\nTo manage the task:")
            print("• Open Task Scheduler (taskschd.msc)")
            print("• Look for 'Weekly Astrological Report' task")
            print("• You can test, disable, or modify the schedule there")

        else:
            print("❌ Failed to create scheduled task")
            print(f"Error: {result.stderr}")
            print("\nManual setup instructions:")
            print("1. Open Task Scheduler (run 'taskschd.msc')")
            print("2. Click 'Import Task...'")
            print(f"3. Select the file: {xml_file}")
            print("4. Adjust settings as needed and save")

    except Exception as e:
        print(f"❌ Error setting up scheduler: {e}")
        print("\nManual setup:")
        print("1. Use Task Scheduler GUI (taskschd.msc)")
        print("2. Create new basic task")
        print("3. Set trigger: Weekly, Saturday, 12:00 AM")
        print("4. Set action: Start program")
        print(f"5. Program: {os.path.join(os.getcwd(), 'automated_weekly_report.bat')}")

def update_birth_info_in_script():
    """Help user update birth information in the automation script."""
    print("\n🔧 Birth Information Setup")
    print("=" * 30)

    print("The automation script needs your birth information.")
    print("Current script uses placeholder data: 1990-05-15 14:30 'New York;NY' 'Los Angeles;CA'")
    print()

    update = input("Would you like to update this now? (y/n): ").lower().strip()

    if update in ['y', 'yes']:
        birth_date = input("Birth date (YYYY-MM-DD): ").strip()
        birth_time = input("Birth time (HH:MM, 24-hour): ").strip()
        birth_location = input("Birth location (City;State): ").strip()
        current_location = input("Current location (City;State): ").strip()

        if all([birth_date, birth_time, birth_location, current_location]):
            # Read the current script
            with open("automated_weekly_report.bat", "r") as f:
                content = f.read()

            # Replace the placeholder
            old_line = 'python astrological_analyzer.py 1990-05-15 14:30 "New York;NY" "Los Angeles;CA"'
            new_line = f'python astrological_analyzer.py {birth_date} {birth_time} "{birth_location}" "{current_location}"'

            content = content.replace(old_line, new_line)

            # Write back
            with open("automated_weekly_report.bat", "w") as f:
                f.write(content)

            print("✅ Birth information updated in automation script!")
        else:
            print("❌ Invalid input. Please update the script manually later.")
    else:
        print("ℹ️  You can edit 'automated_weekly_report.bat' manually to update birth info.")

def show_task_management_info():
    """Show information about managing the scheduled task."""
    print("\n📋 Task Management")
    print("=" * 20)
    print("To manage your automated reports:")
    print()
    print("View task status:")
    print('  schtasks /query /tn "Weekly Astrological Report"')
    print()
    print("Run task immediately (for testing):")
    print('  schtasks /run /tn "Weekly Astrological Report"')
    print()
    print("Disable task:")
    print('  schtasks /change /tn "Weekly Astrological Report" /disable')
    print()
    print("Enable task:")
    print('  schtasks /change /tn "Weekly Astrological Report" /enable')
    print()
    print("Delete task:")
    print('  schtasks /delete /tn "Weekly Astrological Report" /f')
    print()
    print("Or use the GUI: Run 'taskschd.msc' and look for 'Weekly Astrological Report'")

if __name__ == "__main__":
    print("🔮 Windows Scheduler Setup for Astrological Reports")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            setup_windows_scheduler()
            update_birth_info_in_script()
            show_task_management_info()
        elif command == "info":
            show_task_management_info()
        elif command == "update":
            update_birth_info_in_script()
        else:
            print("Usage: python scheduler.py [setup|info|update]")
    else:
        # Interactive setup
        setup_windows_scheduler()
        update_birth_info_in_script()
        show_task_management_info()