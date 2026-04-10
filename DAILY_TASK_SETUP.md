# Daily Astrological Report - Windows Scheduled Task Setup

## Overview

A Windows scheduled task has been successfully configured to generate daily astrological reports at midnight and save them to the `MyReports` folder.

## What Was Created

### 1. Daily Report Script
**File:** `daily_report_to_myreports.bat`

This batch script:
- Reads birth configuration from `birth_config.json`
- Automatically detects the Python installation
- Generates weekly astrological reports
- Copies the generated reports to the `MyReports` folder with timestamps
- Handles errors gracefully (emoji encoding warnings are non-critical)

### 2. Task Setup Script
**File:** `setup_daily_task.ps1`

PowerShell script to register the Windows scheduled task. Features:
- Creates a scheduled task named "DailyAstrologicalReport"
- Schedules execution daily at midnight (00:00)
- Works with or without administrator privileges
- Provides detailed status and verification

### 3. Output Directory
**Folder:** `MyReports\`

All generated reports are saved here with timestamps:
- Format: `MyReports\report_YYYYMMDD_HHMMSS\`
- Each folder contains:
  - Daily reports (*.txt files)
  - Transit charts (*.svg files)
  - Birth chart (birth_chart.svg)
  - Weekly summary (weekly_summary.txt)

## Scheduled Task Details

**Task Name:** `DailyAstrologicalReport`
**Schedule:** Daily at midnight (00:00)
**Status:** Ready and active
**Next Run:** Every day at midnight
**User:** Current user (runs whether logged in or not)

## Managing the Task

### View Task Status
```powershell
Get-ScheduledTaskInfo -TaskName 'DailyAstrologicalReport'
```

### Run Task Manually (for testing)
```powershell
Start-ScheduledTask -TaskName 'DailyAstrologicalReport'
```

### View Task Details
```powershell
Get-ScheduledTask -TaskName 'DailyAstrologicalReport'
```

### Disable Task
```powershell
Disable-ScheduledTask -TaskName 'DailyAstrologicalReport'
```

### Enable Task
```powershell
Enable-ScheduledTask -TaskName 'DailyAstrologicalReport'
```

### Remove Task
```powershell
Unregister-ScheduledTask -TaskName 'DailyAstrologicalReport' -Confirm:$false
```

### Re-create Task
```powershell
.\setup_daily_task.ps1
```

## Using Task Scheduler GUI

1. Press `Win + R` and type: `taskschd.msc`
2. Navigate to "Task Scheduler Library"
3. Find "DailyAstrologicalReport"
4. Right-click for options:
   - Run: Execute immediately
   - Disable/Enable: Toggle the task
   - Properties: View/edit settings
   - Delete: Remove the task

## Configuration

### Birth Data
Edit `birth_config.json` to update your birth information:
```json
{
  "birth_date": "2000-06-20",
  "birth_time": "00:11",
  "birth_location": "Cincinatti;Ohio",
  "current_location": "Las Vegas;Nevada"
}
```

After changing the configuration, the next scheduled run will use the new values.

## Testing

### Manual Test
Run the batch file directly:
```cmd
daily_report_to_myreports.bat
```

### Test Scheduled Task
```powershell
Start-ScheduledTask -TaskName 'DailyAstrologicalReport'
```

Check `MyReports\` folder for the new report with current timestamp.

## Troubleshooting

### Task Not Running
1. Check task status: `Get-ScheduledTaskInfo -TaskName 'DailyAstrologicalReport'`
2. Verify LastTaskResult is 0 (success)
3. Check that the task is enabled
4. Ensure `birth_config.json` exists and is valid

### Python Errors
The script automatically finds Python in common locations:
- `C:\Users\USERNAME\AppData\Local\Programs\Python\PythonXXX\`
- `C:\PythonXXX\`
- Falls back to `py.exe` launcher

If Python is not found, install it from https://www.python.org/

### Reports Not Generated
1. Run the batch file manually to see error messages
2. Check that Python and required packages are installed
3. Verify `birth_config.json` is properly formatted
4. Ensure the astrological analyzer script is present

### Emoji Encoding Warnings
These are non-critical warnings that occur when the console doesn't support Unicode emojis. The reports are still generated successfully.

## Files and Folders

```
astrological-program/
├── daily_report_to_myreports.bat    # Main execution script
├── setup_daily_task.ps1              # Task registration script
├── birth_config.json                 # Birth data configuration
├── MyReports/                        # Output folder for reports
│   ├── report_20260108_210140/      # Example timestamped report
│   └── report_20260108_210317/      # Example timestamped report
└── astrological-calculations/
    └── astrological_analyzer.py      # Python analysis engine
```

## Success Criteria

✅ Windows scheduled task created successfully
✅ Task is enabled and ready
✅ Next run scheduled for midnight
✅ Manual execution tested and verified
✅ Reports successfully saved to MyReports folder
✅ All task management commands documented

## Next Steps

The task will now run automatically every night at midnight. You can:
- Check `MyReports\` folder each morning for new reports
- Customize the schedule by editing the task in Task Scheduler
- Modify `birth_config.json` to update your information
- Run the task manually anytime using PowerShell commands

---

**Setup Date:** January 8, 2026
**Task Status:** Active and verified
**Next Scheduled Run:** Daily at 00:00 (midnight)
