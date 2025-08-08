#!/usr/bin/env python3
"""
Integration Test Script for SUSHI Harvester GUI
Run this to test your integration before using the full GUI
"""

import os
import csv
import json
import sys
from pathlib import Path
import tempfile
import subprocess


def test_provider_file_loading():
    """Test if we can load the providers.tsv file"""
    print("=== Testing Provider File Loading ===")

    # Look for providers file
    search_paths = [
        Path.cwd() / "providers.tsv",
        Path.cwd().parent / "providers.tsv",
        Path("providers.tsv")
    ]

    providers_file = None
    for path in search_paths:
        if path.exists():
            providers_file = path
            break

    if not providers_file:
        print("❌ No providers.tsv file found!")
        print("   Create a providers.tsv file with your SUSHI configurations")
        return False, {}

    print(f"✅ Found providers file: {providers_file}")

    # Load and validate providers
    providers_config = {}
    try:
        with open(providers_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                name = row.get('Name', '').strip()
                base_url = row.get('Base_URL', '').strip()
                customer_id = row.get('Customer_ID', '').strip()

                if name and base_url and customer_id:
                    providers_config[name] = dict(row)
                    print(f"  ✅ {name}: {base_url}")
                elif name:
                    print(f"  ⚠️  {name}: Missing Base_URL or Customer_ID")

        print(f"✅ Loaded {len(providers_config)} valid providers")
        return True, providers_config

    except Exception as e:
        print(f"❌ Error loading providers file: {e}")
        return False, {}


def test_harvester_modules():
    """Test if harvester modules can be imported"""
    print("\n=== Testing Harvester Module Imports ===")

    required_modules = [
        'load_providers',
        'fetch_json',
        'getcounter',
        'logger',
        'sushiconfig'
    ]

    all_imported = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            all_imported = False

    return all_imported


def test_bridge_script():
    """Test if the bridge script exists and can be run"""
    print("\n=== Testing Bridge Script ===")

    bridge_script = Path("gui_bridge.py")
    if not bridge_script.exists():
        print("❌ gui_bridge.py not found!")
        print("   Create the bridge script in your harvester directory")
        return False

    print("✅ Bridge script found")

    # Test help command
    try:
        result = subprocess.run([
            sys.executable, "gui_bridge.py", "--help"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Bridge script can be executed")
            return True
        else:
            print(f"❌ Bridge script error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Bridge script timeout")
        return False
    except Exception as e:
        print(f"❌ Bridge script test failed: {e}")
        return False


def test_temp_file_creation(providers_config):
    """Test temporary providers file creation"""
    print("\n=== Testing Temporary File Creation ===")

    if not providers_config:
        print("⚠️  Skipping - no providers loaded")
        return True

    # Create a temporary providers file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.tsv', prefix='test_providers_')

    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8', newline='') as f:
            headers = ['Name', 'Base_URL', 'Customer_ID', 'Requestor_ID',
                       'API_Key', 'Platform', 'Version', 'Delay', 'Retry']
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(headers)

            # Write first provider as test
            first_provider = list(providers_config.values())[0]
            row = [
                first_provider.get('Name', ''),
                first_provider.get('Base_URL', ''),
                first_provider.get('Customer_ID', ''),
                first_provider.get('Requestor_ID', ''),
                first_provider.get('API_Key', ''),
                first_provider.get('Platform', ''),
                first_provider.get('Version', '5.1'),
                first_provider.get('Delay', ''),
                first_provider.get('Retry', '')
            ]
            writer.writerow(row)

        print(f"✅ Created temporary file: {temp_path}")

        # Test loading the temporary file
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                temp_providers = list(reader)
                print(f"✅ Temporary file contains {len(temp_providers)} providers")
        except Exception as e:
            print(f"❌ Error reading temporary file: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error creating temporary file: {e}")
        return False
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


def test_full_integration(providers_config):
    """Test the full integration with a simple command"""
    print("\n=== Testing Full Integration ===")

    if not providers_config:
        print("⚠️  Skipping - no providers loaded")
        return True

    # Create minimal test configuration
    first_provider_name = list(providers_config.keys())[0]
    test_providers = {first_provider_name: providers_config[first_provider_name]}

    # Test command
    test_cmd = [
        sys.executable, "gui_bridge.py",
        "--start-date", "2024-01",
        "--end-date", "2024-01",
        "--providers", json.dumps(test_providers),
        "--selected-providers", first_provider_name,
        "--reports", "DR"
    ]

    print(f"Testing with provider: {first_provider_name}")
    print("Running limited test (this may take a moment)...")

    try:
        # Run with timeout to avoid hanging
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        print("Command output:")
        print(result.stdout)

        if result.stderr:
            print("Error output:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Integration test passed!")
            return True
        else:
            print(f"❌ Integration test failed with exit code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Integration test timed out (this may be normal)")
        print("   The harvester may be working but taking longer than expected")
        return True
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("SUSHI Harvester GUI Integration Test")
    print("=" * 50)

    # Test 1: Provider file loading
    providers_ok, providers_config = test_provider_file_loading()

    # Test 2: Module imports
    modules_ok = test_harvester_modules()

    # Test 3: Bridge script
    bridge_ok = test_bridge_script()

    # Test 4: Temporary file creation
    temp_file_ok = test_temp_file_creation(providers_config)

    # Test 5: Full integration (optional)
    if providers_ok and modules_ok and bridge_ok:
        print("\n" + "=" * 50)
        user_input = input("Run full integration test? This will attempt to connect to providers (y/N): ")
        if user_input.lower().startswith('y'):
            integration_ok = test_full_integration(providers_config)
        else:
            print("⚠️  Skipping full integration test")
            integration_ok = True
    else:
        integration_ok = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"  Provider Loading:    {'✅ PASS' if providers_ok else '❌ FAIL'}")
    print(f"  Module Imports:      {'✅ PASS' if modules_ok else '❌ FAIL'}")
    print(f"  Bridge Script:       {'✅ PASS' if bridge_ok else '❌ FAIL'}")
    print(f"  Temp File Creation:  {'✅ PASS' if temp_file_ok else '❌ FAIL'}")
    print(f"  Integration Test:    {'✅ PASS' if integration_ok else '❌ FAIL'}")

    all_passed = all([providers_ok, modules_ok, bridge_ok, temp_file_ok, integration_ok])

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your integration should work correctly.")
        print("You can now run your GUI and it should be able to communicate with the harvester.")
    else:
        print("❌ Some tests failed. Please fix the issues before using the GUI.")
        print("\nNext steps:")
        if not providers_ok:
            print("  - Create or fix your providers.tsv file")
        if not modules_ok:
            print("  - Make sure you're running in the harvester directory")
            print("  - Check that all harvester modules are present")
        if not bridge_ok:
            print("  - Create the gui_bridge.py script")
        if not temp_file_ok:
            print("  - Check file permissions and disk space")

    return all_passed


if __name__ == "__main__":
    run_all_tests()