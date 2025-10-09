#!/usr/bin/env python3
"""
Test script to verify timezone support implementation.
Run this after implementing timezone support to ensure everything works correctly.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def test_database_schema():
    """Test that timezone columns were added to the database"""
    print("🔍 Testing database schema...")
    
    # Create database connection (adjust connection string as needed)
    engine = create_engine("sqlite:///./test.db")  # Adjust for your database
    
    try:
        with engine.connect() as conn:
            # Test each table has the timezone columns
            tables_and_columns = [
                ("access_logs", "device_timezone"),
                ("user_login_logs", "client_timezone"),
                ("companies", "record_timezone"),
                ("employees", "record_timezone"),
                ("users", "record_timezone"),
                ("face_encodings", "record_timezone"),
                ("password_history", "record_timezone"),
            ]
            
            for table, column in tables_and_columns:
                try:
                    result = conn.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
                    print(f"✅ {table}.{column} - Column exists")
                except Exception as e:
                    print(f"❌ {table}.{column} - Column missing: {e}")
                    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("✅ Database schema test completed\n")
    return True

def test_timezone_formats():
    """Test various timezone format validations"""
    print("🔍 Testing timezone format validation...")
    
    valid_timezones = [
        "UTC",
        "GMT-05",
        "GMT+09",
        "America/New_York",
        "Europe/London",
        "Asia/Tokyo",
        "Australia/Sydney"
    ]
    
    invalid_timezones = [
        "",
        None,
        "InvalidTimezone",
        "GMT-25",  # Invalid offset
        "Random/String"
    ]
    
    def validate_timezone(tz):
        """Simple timezone validation for testing"""
        if not tz or not isinstance(tz, str):
            return False
        
        import re
        patterns = [
            r'^UTC$',
            r'^GMT[+-]\d{2}$',
            r'^[A-Za-z_]+/[A-Za-z_]+$'
        ]
        
        return any(re.match(pattern, tz) for pattern in patterns)
    
    # Test valid timezones
    for tz in valid_timezones:
        if validate_timezone(tz):
            print(f"✅ Valid timezone: {tz}")
        else:
            print(f"❌ Failed validation for valid timezone: {tz}")
    
    # Test invalid timezones
    for tz in invalid_timezones:
        if not validate_timezone(tz):
            print(f"✅ Correctly rejected invalid timezone: {tz}")
        else:
            print(f"❌ Incorrectly accepted invalid timezone: {tz}")
    
    print("✅ Timezone format test completed\n")

def test_model_imports():
    """Test that updated models can be imported"""
    print("🔍 Testing model imports...")
    
    try:
        from models import AccessLog, User, Employee, FaceEncoding, UserLoginLog, PasswordHistory, Company
        print("✅ All models imported successfully")
        
        # Test that timezone fields exist in models
        models_and_fields = [
            (AccessLog, "device_timezone"),
            (UserLoginLog, "client_timezone"),
            (User, "record_timezone"),
            (Employee, "record_timezone"),
            (FaceEncoding, "record_timezone"),
            (PasswordHistory, "record_timezone"),
            (Company, "record_timezone"),
        ]
        
        for model, field in models_and_fields:
            if hasattr(model, field):
                print(f"✅ {model.__name__}.{field} - Field exists")
            else:
                print(f"❌ {model.__name__}.{field} - Field missing")
        
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    print("✅ Model import test completed\n")
    return True

def test_schema_imports():
    """Test that updated schemas can be imported"""
    print("🔍 Testing schema imports...")
    
    try:
        from schemas import CheckReq, UserCreate, EmployeeCreate, CompanyCreate
        print("✅ All schemas imported successfully")
        
        # Test CheckReq has device_timezone
        test_check_req = CheckReq(
            image_base64="test_image_data",
            device_timezone="America/New_York"
        )
        print(f"✅ CheckReq.device_timezone = {test_check_req.device_timezone}")
        
        # Test UserCreate has record_timezone
        test_user_create = UserCreate(
            company_id=1,
            role_id=1,
            username="testuser",
            password="testpass",
            record_timezone="Europe/London"
        )
        print(f"✅ UserCreate.record_timezone = {test_user_create.record_timezone}")
        
        # Test EmployeeCreate has record_timezone
        test_employee_create = EmployeeCreate(
            warehouse_id=1,
            first_name="John",
            last_name="Doe",
            record_timezone="Asia/Tokyo"
        )
        print(f"✅ EmployeeCreate.record_timezone = {test_employee_create.record_timezone}")
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False
    
    print("✅ Schema test completed\n")
    return True

def test_service_functions():
    """Test that service functions accept timezone parameters"""
    print("🔍 Testing service function signatures...")
    
    try:
        from services.log_service import create_user_login_log
        from services.user_service import UserService
        from services.auth_service import login
        
        import inspect
        
        # Test create_user_login_log function signature
        sig = inspect.signature(create_user_login_log)
        if 'client_timezone' in sig.parameters:
            print("✅ create_user_login_log accepts client_timezone parameter")
        else:
            print("❌ create_user_login_log missing client_timezone parameter")
        
        # Test UserService.create_user function signature
        sig = inspect.signature(UserService.create_user)
        if 'record_timezone' in sig.parameters:
            print("✅ UserService.create_user accepts record_timezone parameter")
        else:
            print("❌ UserService.create_user missing record_timezone parameter")
        
        # Test auth_service.login function signature
        sig = inspect.signature(login)
        if 'client_timezone' in sig.parameters:
            print("✅ auth_service.login accepts client_timezone parameter")
        else:
            print("❌ auth_service.login missing client_timezone parameter")
        
    except Exception as e:
        print(f"❌ Service function test failed: {e}")
        return False
    
    print("✅ Service function test completed\n")
    return True

def generate_test_report():
    """Generate a summary test report"""
    print("📋 TIMEZONE IMPLEMENTATION TEST REPORT")
    print("=" * 50)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Timezone Formats", test_timezone_formats),
        ("Model Imports", test_model_imports),
        ("Schema Imports", test_schema_imports),
        ("Service Functions", test_service_functions),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Timezone implementation is ready.")
        print("\n📝 NEXT STEPS:")
        print("1. Update frontend code to capture and send timezone information")
        print("2. Test with real devices in different timezones")
        print("3. Verify reports display correct local times")
        print("4. Test daylight saving time transitions")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        print("Check the error messages above and fix the issues.")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 Starting Timezone Implementation Tests...\n")
    success = generate_test_report()
    sys.exit(0 if success else 1)