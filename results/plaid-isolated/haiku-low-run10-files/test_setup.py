#!/usr/bin/env python3
"""
Test script to verify Plaid Link setup and dependencies
"""

import sys
import os


def check_python_version():
    """Check if Python 3.9+ is installed"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✓ Python {version.major}.{version.minor} detected")
    return True


def check_dependencies():
    """Check if all required packages are installed"""
    required = [
        'plaid',
        'plaid_link_verify',
        'flask',
        'dotenv',
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            all_installed = False

    return all_installed


def check_environment_variables():
    """Check if Plaid environment variables are set"""
    required_vars = ['PLAID_CLIENT_ID', 'PLAID_SECRET']
    all_set = True

    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"❌ {var} is NOT set")
            all_set = False

    return all_set


def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    elif os.path.exists('.env.example'):
        print("⚠ .env file does NOT exist, but .env.example is available")
        print("  Run: cp .env.example .env")
        return False
    else:
        print("❌ Neither .env nor .env.example files found")
        return False


def main():
    print("\n🔍 Plaid Link Setup Verification\n")
    print("-" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Environment Variables", check_environment_variables),
    ]

    results = []
    for name, check in checks:
        print(f"\n{name}:")
        results.append(check())

    print("\n" + "-" * 50)

    if all(results[:2]):  # Python and dependencies are critical
        if not results[2] or not results[3]:
            print("\n⚠️  Setup is incomplete. Please:")
            print("   1. Copy .env.example to .env")
            print("   2. Add your Plaid credentials to .env")
            print("\n   Then run: python app.py")
        else:
            print("\n✅ All checks passed! Ready to run: python app.py")
    else:
        print("\n❌ Critical setup issues detected. Please fix the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
