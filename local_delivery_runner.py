#!/usr/bin/env python3
"""
Local Delivery Runner for Automated Reports
Handles the delivery of generated reports, prioritizing LLM-enhanced versions.
"""

from pathlib import Path
import os
import datetime

def main():
    """Main delivery processing function."""
    try:
        from local_delivery import LocalDeliveryManager
        delivery_manager = LocalDeliveryManager()

        tosend_path = Path('tosend')
        if not tosend_path.exists():
            print('❌ tosend folder not found')
            return

        # Prioritize enhanced ZIP files first
        enhanced_zips = list(tosend_path.glob('*enhanced*.zip'))
        if enhanced_zips:
            latest_zip = max(enhanced_zips, key=os.path.getctime)
            print(f'Delivering enhanced report: {latest_zip.name}')
        else:
            # Fall back to any ZIP file
            zip_files = list(tosend_path.glob('*.zip'))
            if zip_files:
                latest_zip = max(zip_files, key=os.path.getctime)
                print(f'Delivering standard report: {latest_zip.name}')
            else:
                print('No ZIP files found for delivery')
                return

        week_info = f'LLM-Enhanced Report Generated on {datetime.datetime.now().strftime("%B %d, %Y")}'
        delivery_manager.deliver_report(str(latest_zip), week_info)
        print('✅ Report delivered successfully via local delivery system')

    except ImportError:
        print('Local delivery not available - reports saved in tosend/ folder only')
        # Still list what's available
        tosend_path = Path('tosend')
        if tosend_path.exists():
            files = list(tosend_path.glob('*'))
            if files:
                print(f'Available in tosend/: {[f.name for f in files]}')
    except Exception as e:
        print(f'❌ Delivery failed: {e}')

if __name__ == "__main__":
    main()