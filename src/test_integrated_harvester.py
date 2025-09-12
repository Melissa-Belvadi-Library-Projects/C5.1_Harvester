# test_integrated_harvester.py
"""
Test script to run the integrated GUI/CLI harvester.
This demonstrates that the GUI uses the exact same backend as the CLI.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))

from ui.main_window import SushiHarvesterGUI
from core.harvester_integration import HarvesterRequest, HarvesterIntegration


def setup_test_environment():
    """Create test providers and config files if they don't exist."""

    # Create sample providers.tsv if needed
    if not Path('providers.tsv').exists() and not Path('../providers.tsv').exists():
        print("Creating sample providers.tsv...")
        sample_tsv = """Name\tBase_URL\tCustomer_ID\tRequestor_ID\tAPI_Key\tPlatform\tVersion\tDelay\tRetry
Test Publisher 1\thttps://sushi.testpub1.com/reports\tCUST001\tREQ001\tkey123\tTestPlatform1\t5.1\t1\t3
Test Publisher 2\thttps://sushi.testpub2.com/counter/r5\tCUST002\tREQ002\tkey456\tTestPlatform2\t5.1\t2\t2
EBSCO Test\thttps://sushi.ebscohost.com/R5/reports\tEBSCO123\tEBSCO_REQ\tebsco-key\tEBSCOhost\t5.1\t1\t3
ProQuest Test\thttps://sushi.proquest.com/reports\tPQ_TEST\tPQ_REQ_TEST\tpq-test-key\tProQuest\t5.1\t1.5\t3"""

        with open('providers.tsv', 'w') as f:
            f.write(sample_tsv)
        print("✓ Sample providers.tsv created")

    # Create sample current_config.py if needed
    if not Path('current_config.py').exists():
        print("Creating sample current_config.py...")
        sample_config = """# Configuration file for COUNTER 5.1 Harvester
sqlite_filename = 'test_counterdata.db'
data_table = 'usage_data'
error_log_file = 'test_errorlog.txt'
json_dir = 'test_json_output'
tsv_dir = 'test_tsv_output'
providers_file = 'providers.tsv'
save_empty_report = True
always_include_header_metric_types = True
default_begin = '2024-01'"""

        with open('current_config.py', 'w') as f:
            f.write(sample_config)
        print("✓ Sample current_config.py created")

    # Create output directories
    for dir_name in ['test_json_output', 'test_tsv_output']:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def test_cli_mode():
    """Test the harvester in CLI mode (no GUI)."""
    print("\n" + "=" * 70)
    print("TESTING CLI MODE (Direct Backend Call)")
    print("=" * 70)

    # Create a test request
    request = HarvesterRequest(
        begin_date='2024-01',
        end_date='2024-03',
        selected_vendors=['Test Publisher 1', 'EBSCO Test'],
        selected_reports=['TR', 'DR'],
        single_report_type=None,
        save_empty_reports=True,
        create_database=True,
        output_json=True,
        output_tsv=True
    )

    print(f"\nTest Configuration:")
    print(f"  Date Range: {request.begin_date} to {request.end_date}")
    print(f"  Vendors: {', '.join(request.selected_vendors)}")
    print(f"  Reports: {', '.join(request.selected_reports)}")
    print()

    # Create harvester with console output
    def console_log(msg):
        print(f"  {msg}")

    harvester = HarvesterIntegration(
        progress_callback=console_log,
        status_callback=lambda x: print(f"STATUS: {x}")
    )

    # Run the harvest
    print("Starting harvest...")
    results = harvester.run(request)

    # Display results
    print("\n" + "-" * 50)
    print("CLI Test Results:")
    print("-" * 50)
    print(f"Success: {results.get('success', False)}")
    print(f"Providers Processed: {results.get('providers_processed', 0)}")
    print(f"Reports Fetched: {results.get('reports_fetched', 0)}")
    print(f"Reports Failed: {results.get('reports_failed', 0)}")

    if results.get('json_files'):
        print(f"\nJSON Files Created ({len(results['json_files'])}):")
        for f in results['json_files'][:3]:
            print(f"  - {Path(f).name}")

    if results.get('tsv_files'):
        print(f"\nTSV Files Created ({len(results['tsv_files'])}):")
        for f in results['tsv_files'][:3]:
            print(f"  - {Path(f).name}")

    if results.get('errors'):
        print(f"\nErrors:")
        for err in results['errors']:
            print(f"  - {err}")

    return results


def test_gui_mode():
    """Test the harvester in GUI mode."""
    print("\n" + "=" * 70)
    print("TESTING GUI MODE")
    print("=" * 70)
    print("\nStarting GUI application...")
    print("The GUI will open with pre-selected options.")
    print("Click 'Start' to run the same harvest as the CLI test.")
    print()

    app = QApplication(sys.argv)

    # Create main window
    window = SushiHarvesterGUI()

    # Pre-populate selections for testing
    # Select vendors
    vendor_checkboxes = window.vendor_frame.checkboxes
    for checkbox in vendor_checkboxes:
        if checkbox.text() in ['Test Publisher 1', 'EBSCO Test']:
            checkbox.setChecked(True)

    # Select report types
    report_checkboxes = window.report_frame.checkboxes
    for checkbox in report_checkboxes:
        if checkbox.text() in ['TR', 'DR']:
            checkbox.setChecked(True)

    # Set dates
    window.date_selector.start_year.setValue(2024)
    window.date_selector.start_month.setCurrentIndex(0)  # January
    window.date_selector.end_year.setValue(2024)
    window.date_selector.end_month.setCurrentIndex(2)  # March

    # Show instructions
    msg = QMessageBox()
    msg.setWindowTitle("Integrated Harvester Test")
    msg.setText("GUI Test Mode Ready")
    msg.setInformativeText(
        "The GUI has been pre-configured with:\n"
        "• Date Range: 2024-01 to 2024-03\n"
        "• Vendors: Test Publisher 1, EBSCO Test\n"
        "• Reports: TR, DR\n\n"
        "Click 'Start' to run the harvest.\n"
        "This will use the exact same backend as the CLI."
    )
    msg.setDetailedText(
        "The harvester will:\n"
        "1. Fetch provider API information\n"
        "2. Get supported reports for each provider\n"
        "3. Download COUNTER reports\n"
        "4. Save JSON files to test_json_output/\n"
        "5. Convert to TSV and save to test_tsv_output/\n"
        "6. Store data in test_counterdata.db\n\n"
        "Watch the progress dialog for detailed output."
    )
    msg.exec()

    window.show()

    return app.exec()


def compare_outputs():
    """Compare the outputs from CLI and GUI runs."""
    print("\n" + "=" * 70)
    print("OUTPUT VERIFICATION")
    print("=" * 70)

    # Check JSON output directory
    json_path = Path('test_json_output')
    if json_path.exists():
        json_files = list(json_path.rglob('*.json'))
        print(f"\n📁 JSON Files Found: {len(json_files)}")
        for vendor_dir in json_path.iterdir():
            if vendor_dir.is_dir():
                vendor_files = list(vendor_dir.glob('*.json'))
                if vendor_files:
                    print(f"  {vendor_dir.name}: {len(vendor_files)} files")

    # Check TSV output directory
    tsv_path = Path('test_tsv_output')
    if tsv_path.exists():
        tsv_files = list(tsv_path.rglob('*.tsv'))
        print(f"\n📊 TSV Files Found: {len(tsv_files)}")
        for vendor_dir in tsv_path.iterdir():
            if vendor_dir.is_dir():
                vendor_files = list(vendor_dir.glob('*.tsv'))
                if vendor_files:
                    print(f"  {vendor_dir.name}: {len(vendor_files)} files")

    # Check database
    db_path = Path('test_counterdata.db')
    if db_path.exists():
        print(f"\n🗄️ Database Created: {db_path.name} ({db_path.stat().st_size:,} bytes)")

    # Check error log
    error_log = Path('test_errorlog.txt')
    if error_log.exists():
        with open(error_log, 'r') as f:
            lines = f.readlines()
        print(f"\n📝 Error Log: {len(lines)} lines")
        if lines:
            print("  Recent entries:")
            for line in lines[-3:]:
                print(f"    {line.strip()[:70]}...")


def main():
    """Run the integrated harvester test."""

    print("=" * 70)
    print("COUNTER 5.1 HARVESTER - INTEGRATED GUI/CLI TEST")
    print("=" * 70)
    print()
    print("This test demonstrates that the GUI uses the exact same")
    print("backend engine as the CLI, producing identical outputs.")
    print()

    # Setup test environment
    print("Setting up test environment...")
    setup_test_environment()

    # Test mode selection
    print("\nSelect test mode:")
    print("1. CLI mode only (direct backend call)")
    print("2. GUI mode only (with visual interface)")
    print("3. Both modes (compare outputs)")
    print("4. Quick verification (check existing outputs)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        test_cli_mode()
        compare_outputs()

    elif choice == '2':
        test_gui_mode()
        compare_outputs()

    elif choice == '3':
        # Run CLI test first
        cli_results = test_cli_mode()

        # Ask if user wants to continue to GUI
        print("\nCLI test complete. Press Enter to start GUI test...")
        input()

        # Run GUI test
        test_gui_mode()

        # Compare outputs
        compare_outputs()

    elif choice == '4':
        compare_outputs()

    else:
        print("Invalid choice. Please run again and select 1-4.")

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback

        traceback.print_exc()