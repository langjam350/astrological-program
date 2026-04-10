# PowerShell script to set up daily astrological report Windows scheduled task
# Run this script as Administrator to create the scheduled task

# Configuration
$TaskName = "DailyAstrologicalReport"
$Description = "Generates daily astrological report at midnight and saves to MyReports folder"
$ScriptPath = Join-Path $PSScriptRoot "daily_report_to_myreports.bat"
$WorkingDirectory = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Daily Astrological Report Task Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Running without Administrator privileges" -ForegroundColor Yellow
    Write-Host "Task will be created for current user only" -ForegroundColor Yellow
    Write-Host ""
}

# Verify script file exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script file not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Script Path: $ScriptPath" -ForegroundColor Green
Write-Host "Working Directory: $WorkingDirectory" -ForegroundColor Green
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$TaskName' already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove and recreate it? (y/n)"

    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Existing task removed." -ForegroundColor Green
    } else {
        Write-Host "Keeping existing task. Exiting..." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Creating scheduled task..." -ForegroundColor Cyan

# Create the action
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDirectory

# Create the trigger (daily at midnight)
$Trigger = New-ScheduledTaskTrigger -Daily -At "00:00"

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# Create the principal (run whether user is logged on or not)
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $Description `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Force | Out-Null

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS: Task created successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at midnight (00:00)" -ForegroundColor White
    Write-Host "  Script: $ScriptPath" -ForegroundColor White
    Write-Host ""
    Write-Host "To manage this task:" -ForegroundColor Cyan
    Write-Host "  - Open Task Scheduler (taskschd.msc)" -ForegroundColor White
    Write-Host "  - Navigate to Task Scheduler Library" -ForegroundColor White
    Write-Host "  - Find task named '$TaskName'" -ForegroundColor White
    Write-Host ""
    Write-Host "To test the task immediately:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To remove the task:" -ForegroundColor Cyan
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Yellow
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Verify the task was created
$verifyTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($verifyTask) {
    Write-Host "Verification: Task registered successfully!" -ForegroundColor Green
    Write-Host ""

    # Show task information
    $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host "Task Status: " -NoNewline
    Write-Host $verifyTask.State -ForegroundColor $(if ($verifyTask.State -eq 'Ready') { 'Green' } else { 'Yellow' })

    if ($taskInfo.LastRunTime) {
        Write-Host "Last Run: $($taskInfo.LastRunTime)"
    } else {
        Write-Host "Last Run: Never" -ForegroundColor Yellow
    }

    if ($taskInfo.NextRunTime) {
        Write-Host "Next Run: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
    }

} else {
    Write-Host "WARNING: Task may not have been created properly" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
