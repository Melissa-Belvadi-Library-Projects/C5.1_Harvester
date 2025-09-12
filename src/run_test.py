# run_test.py
"""
Simple launcher for testing the harvester with realistic delays.
Run this to see the full harvesting process with your actual providers.
"""

import sys
import os
from pathlib import Path


def main():
    """Run the test with proper setup."""

    # Clear terminal for better visibility
    os.system('clear' if os.name == 'posix' else 'cls')

    print("=" * 70)
    print("COUNTER 5.1 HARVESTER - TEST MODE")
    print("=" * 70)
    print()
    print("This test will:")
    print("  1. Load your actual providers from providers.tsv")
    print("  2. Simulate realistic API calls with delays")
    print("  3. Show detailed progress in the terminal")
    print("  4. Allow you to test Stop and Save Log functions")
    print("  5. Generate a summary report")
    print()
    print("=" * 70)

    # Check for required files
    required_files = [
        'providers.tsv',  # or providers_all.tsv based on your config
        'current_config.py'
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists() and not Path(f"../{file}").exists():
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️  Warning: Missing files: {', '.join(missing_files)}")
        print("The test will create sample data if needed.\n")

    # Create sample providers.tsv if it doesn't exist
    if not Path('providers.tsv').exists() and not Path('../providers.tsv').exists():
        print("Creating sample providers.tsv...")
        sample_tsv = """Name	Base_URL	Customer_ID	Requestor_ID	API_Key	Platform	Version	Delay	Retry
EBSCO	https://sushi.ebscohost.com/R5	CID123456	RID789	abc123xyz	EBSCOhost	5.1	2	3
ProQuest	https://sushi.proquest.com/counter/r5	PQ_CUST_001	PQ_REQ_001	proquest-key-456	ProQuest One	5.1	1	3
Springer Nature	https://counter.springernature.com	SN_CUSTOMER	SN_REQUEST	springer-api-key	SpringerLink	5.1	1.5	2
Wiley	https://onlinelibrary.wiley.com/reports	WILEY_ID_789	WILEY_REQ	wiley-secret-key	Wiley Online	5.1	1	3
Elsevier	https://counter.elsevier.com/api/r5	ELS_CUST_456	ELS_REQ_123	elsevier-token	ScienceDirect	5.1	2	4
JSTOR	https://www.jstor.org/sushi/r5	JSTOR_ORG_001	JSTOR_REQ	jstor-api-2024	JSTOR	5.1	1	2
Oxford	https://sushi5.scholarlyiq.com	OUP_CUSTOMER	OUP_REQUEST	oxford-key-789	Oxford Academic	5.1	1.5	3
Cambridge	https://counter.cambridge.org/r5	CAM_ID_2024	CAM_REQ_001	cambridge-token	Cambridge Core	5.1	1	3
"""
        with open('providers.tsv', 'w') as f:
            f.write(sample_tsv)
        print("✓ Sample providers.tsv created\n")

    # Create sample config if it doesn't exist
    if not Path('current_config.py').exists():
        print("Creating sample current_config.py...")
        sample_config = """# Configuration file for COUNTER 5.1 Harvester
sqlite_filename = 'counterdata.db'
data_table = 'usage_data'
error_log_file = 'errorlog.txt'
json_dir = 'json_folder'
tsv_dir = 'tsv_folder'
providers_file = 'providers.tsv'
save_empty_report = False
always_include_header_metric_types = True
default_begin = '2024-01'
"""
        with open('current_config.py', 'w') as f:
            f.write(sample_config)
        print("✓ Sample current_config.py created\n")

    print("Starting test application...")
    print("-" * 70)
    print()

    # Import and run the test
    try:
        from test_harvester_realistic import main as run_test
        return run_test()
    except ImportError as e:
        print(f"\n❌ Error: Could not import test module: {e}")
        print("\nMake sure you have:")
        print("  1. test_harvester_realistic.py in the current directory")
        print("  2. All required dependencies installed (PyQt6, python-dateutil)")
        print("\nInstall dependencies with:")
        print("  pip install PyQt6 python-dateutil")
        return 1


if __name__ == "__main__":
    sys.exit(main())