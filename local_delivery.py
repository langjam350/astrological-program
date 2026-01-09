#!/usr/bin/env python3
"""
Local Delivery System for Astrological Reports
Privacy-focused delivery methods with no external dependencies.
"""

import json
import os
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DeliveryConfig:
    """Local delivery configuration settings."""
    windows_notifications: bool = True
    desktop_shortcut: bool = True
    copy_to_folders: List[str] = None
    auto_open_folder: bool = True
    cleanup_old_reports: bool = True
    keep_reports_days: int = 30

    def __post_init__(self):
        if self.copy_to_folders is None:
            self.copy_to_folders = []

class LocalDeliveryManager:
    """Manages local delivery of astrological reports."""

    def __init__(self, config_file: str = "delivery_config.json"):
        """Initialize delivery manager with configuration."""
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> DeliveryConfig:
        """Load delivery configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return DeliveryConfig(**data)
            except Exception as e:
                print(f"Error loading delivery config: {e}")
                return DeliveryConfig()
        else:
            # Create default config
            default_config = DeliveryConfig()
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: DeliveryConfig) -> None:
        """Save configuration to file."""
        try:
            # Convert dataclass to dict for JSON serialization
            config_dict = {
                'windows_notifications': config.windows_notifications,
                'desktop_shortcut': config.desktop_shortcut,
                'copy_to_folders': config.copy_to_folders,
                'auto_open_folder': config.auto_open_folder,
                'cleanup_old_reports': config.cleanup_old_reports,
                'keep_reports_days': config.keep_reports_days
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving delivery config: {e}")

    def deliver_report(self, zip_path: str, report_info: str = "") -> bool:
        """Deliver astrological report using configured methods."""
        if not os.path.exists(zip_path):
            print(f"Report file not found: {zip_path}")
            return False

        success = True
        delivered_locations = []

        try:
            # 1. Windows notification
            if self.config.windows_notifications:
                self._send_windows_notification(zip_path, report_info)

            # 2. Copy to additional folders (cloud sync, USB, etc.)
            for folder_path in self.config.copy_to_folders:
                if self._copy_to_folder(zip_path, folder_path):
                    delivered_locations.append(folder_path)

            # 3. Create desktop shortcut to report
            if self.config.desktop_shortcut:
                self._create_desktop_shortcut(zip_path)

            # 4. Auto-open containing folder
            if self.config.auto_open_folder:
                self._open_containing_folder(zip_path)

            # 5. Cleanup old reports
            if self.config.cleanup_old_reports:
                self._cleanup_old_reports()

            # Summary notification
            if delivered_locations:
                locations_text = ", ".join(delivered_locations)
                print(f"📦 Report delivered to: {locations_text}")

            return success

        except Exception as e:
            print(f"Delivery failed: {e}")
            return False

    def _send_windows_notification(self, zip_path: str, report_info: str) -> None:
        """Send Windows 10/11 notification."""
        try:
            # Use PowerShell to send Windows notification
            title = "🔮 Weekly Astrological Report Ready!"
            message = f"Your personalized report is ready: {os.path.basename(zip_path)}"

            if report_info:
                message += f"\n{report_info}"

            ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.Visible = $true
$notification.ShowBalloonTip(10000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 2
$notification.Dispose()
'''

            # Alternative simpler method using msg command
            try:
                subprocess.run(['msg', '*', f"{title}\n\n{message}"],
                             check=False, capture_output=True)
            except:
                # If msg fails, try PowerShell
                subprocess.run(['powershell', '-Command', ps_script],
                             check=False, capture_output=True)

            print("📢 Windows notification sent")

        except Exception as e:
            print(f"Notification failed: {e}")

    def _copy_to_folder(self, zip_path: str, destination_folder: str) -> bool:
        """Copy report to specified folder."""
        try:
            dest_path = Path(destination_folder)

            # Create destination if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)

            # Copy file
            dest_file = dest_path / os.path.basename(zip_path)
            shutil.copy2(zip_path, dest_file)

            print(f"📁 Copied to: {dest_file}")
            return True

        except Exception as e:
            print(f"Failed to copy to {destination_folder}: {e}")
            return False

    def _create_desktop_shortcut(self, zip_path: str) -> None:
        """Create desktop shortcut to the report."""
        try:
            desktop_path = Path.home() / "Desktop"
            shortcut_name = f"Astrological_Report_{datetime.datetime.now().strftime('%Y%m%d')}.lnk"
            shortcut_path = desktop_path / shortcut_name

            # Create a simple .url file instead of .lnk for simplicity
            url_content = f'''[InternetShortcut]
URL=file:///{zip_path.replace(os.sep, '/')}
IconFile={zip_path}
IconIndex=0
'''

            url_path = desktop_path / f"Astrological_Report_{datetime.datetime.now().strftime('%Y%m%d')}.url"

            with open(url_path, 'w') as f:
                f.write(url_content)

            print(f"🔗 Desktop shortcut created: {url_path.name}")

        except Exception as e:
            print(f"Shortcut creation failed: {e}")

    def _open_containing_folder(self, zip_path: str) -> None:
        """Open the folder containing the report."""
        try:
            folder_path = os.path.dirname(zip_path)
            subprocess.run(['explorer', folder_path], check=False)
            print(f"📂 Opened folder: {folder_path}")
        except Exception as e:
            print(f"Failed to open folder: {e}")

    def _cleanup_old_reports(self) -> None:
        """Remove old report files based on retention policy."""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.config.keep_reports_days)

            # Clean up tosend folder
            tosend_path = Path("tosend")
            if tosend_path.exists():
                removed_count = 0
                for file_path in tosend_path.glob("*.zip"):
                    file_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        removed_count += 1

                if removed_count > 0:
                    print(f"🧹 Cleaned up {removed_count} old report(s)")

        except Exception as e:
            print(f"Cleanup failed: {e}")

    def add_delivery_location(self, folder_path: str) -> None:
        """Add a new delivery location."""
        if folder_path not in self.config.copy_to_folders:
            self.config.copy_to_folders.append(folder_path)
            self._save_config(self.config)
            print(f"✅ Added delivery location: {folder_path}")

    def remove_delivery_location(self, folder_path: str) -> None:
        """Remove a delivery location."""
        if folder_path in self.config.copy_to_folders:
            self.config.copy_to_folders.remove(folder_path)
            self._save_config(self.config)
            print(f"❌ Removed delivery location: {folder_path}")

    def setup_cloud_integration(self) -> None:
        """Help user set up cloud folder integration."""
        print("☁️ Cloud Integration Setup")
        print("=" * 30)
        print("You can automatically copy reports to your cloud sync folders:")
        print()

        # Common cloud sync folders
        cloud_options = {
            "1": ("Dropbox", Path.home() / "Dropbox" / "Astrological Reports"),
            "2": ("OneDrive", Path.home() / "OneDrive" / "Astrological Reports"),
            "3": ("Google Drive", Path.home() / "Google Drive" / "Astrological Reports"),
            "4": ("iCloud", Path.home() / "iCloudDrive" / "Astrological Reports"),
            "5": ("Custom folder", None)
        }

        for key, (name, path) in cloud_options.items():
            status = "✅" if path and path.parent.exists() else "❌"
            print(f"{key}. {name} {status}")

        print("\nSelect option(s) (comma-separated, e.g., 1,2): ", end="")
        choices = input().strip().split(',')

        for choice in choices:
            choice = choice.strip()
            if choice in cloud_options:
                name, path = cloud_options[choice]

                if choice == "5":  # Custom folder
                    custom_path = input("Enter custom folder path: ").strip()
                    if custom_path:
                        path = Path(custom_path) / "Astrological Reports"

                if path:
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        self.add_delivery_location(str(path))
                        print(f"✅ {name} integration enabled: {path}")
                    except Exception as e:
                        print(f"❌ Failed to setup {name}: {e}")

def setup_local_delivery():
    """Interactive setup for local delivery options."""
    print("🔮 Local Delivery Setup")
    print("=" * 30)
    print("Configure how you want to receive your astrological reports:")
    print()

    manager = LocalDeliveryManager()

    # Windows notifications
    notifications = input("Enable Windows notifications? (y/n): ").lower().strip()
    manager.config.windows_notifications = notifications in ['y', 'yes']

    # Desktop shortcuts
    shortcuts = input("Create desktop shortcuts to reports? (y/n): ").lower().strip()
    manager.config.desktop_shortcut = shortcuts in ['y', 'yes']

    # Auto-open folder
    auto_open = input("Automatically open report folder? (y/n): ").lower().strip()
    manager.config.auto_open_folder = auto_open in ['y', 'yes']

    # Cloud integration
    cloud_setup = input("Set up cloud folder integration? (y/n): ").lower().strip()
    if cloud_setup in ['y', 'yes']:
        manager.setup_cloud_integration()

    # Cleanup policy
    cleanup = input("Automatically cleanup old reports? (y/n): ").lower().strip()
    manager.config.cleanup_old_reports = cleanup in ['y', 'yes']

    if manager.config.cleanup_old_reports:
        try:
            days = int(input("Keep reports for how many days? (default 30): ").strip() or "30")
            manager.config.keep_reports_days = days
        except ValueError:
            manager.config.keep_reports_days = 30

    # Save configuration
    manager._save_config(manager.config)

    print("\n✅ Local delivery configured!")
    print("\nYour reports will be delivered to:")
    print("• tosend/ folder (always)")
    if manager.config.copy_to_folders:
        for folder in manager.config.copy_to_folders:
            print(f"• {folder}")
    if manager.config.windows_notifications:
        print("• Windows notification system")
    if manager.config.desktop_shortcut:
        print("• Desktop shortcut")

if __name__ == "__main__":
    setup_local_delivery()