#!/usr/bin/env python3
"""
Test script for Jira Report Generator

Tests the month parsing and report generation functionality
"""

import sys
from jira_report_generator import JiraReportGenerator

def test_month_parsing():
    """Test month name parsing functionality"""
    print("Testing month parsing...")
    
    try:
        generator = JiraReportGenerator()
        
        # Test various month formats
        test_cases = [
            'september', 'September', 'SEPTEMBER',
            'august', 'ijul', 'december',
            'jan', 'feb', 'mar'
        ]
        
        for month_text in test_cases:
            try:
                month_num, year = generator.parse_month_year(month_text)
                print(f"OK '{month_text}' -> Month {month_num}, Year {year}")
            except ValueError as e:
                print(f"ERROR '{month_text}' -> Error: {e}")
                
    except Exception as e:
        print(f"ERROR Failed to initialize generator: {e}")
        return False
    
    return True

def test_date_range():
    """Test date range calculation"""
    print("\nTesting date range calculation...")
    
    try:
        generator = JiraReportGenerator()
        
        # Test September 2024
        first_day, last_day = generator.get_month_date_range(9, 2024)
        print(f"OK September 2024: {first_day} to {last_day}")
        
        # Test February (leap year)
        first_day, last_day = generator.get_month_date_range(2, 2024)
        print(f"OK February 2024 (leap): {first_day} to {last_day}")
        
        return True
        
    except Exception as e:
        print(f"ERROR Date range test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        generator = JiraReportGenerator()
        
        print(f"OK Jira Server: {generator.jira_server}")
        print(f"OK Jira Username: {generator.jira_username}")
        print(f"OK Report Author: {generator.report_author}")
        print(f"OK API Token configured: {'Yes' if generator.jira_api_token else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"ERROR Configuration test failed: {e}")
        print("INFO Make sure Jira parameters are set in bot/config.env")
        return False

def main():
    """Main test function"""
    print("Starting Jira Report Generator Tests\n")
    
    tests = [
        test_config_loading,
        test_month_parsing,
        test_date_range
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed. Check the configuration and dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
