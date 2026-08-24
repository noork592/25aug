#!/usr/bin/env python3
"""
Backend API Test for JK Products Factory Order Management
Testing bug fix: PATCH /customers/{cid} false 404 for restored customers
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://staging-env-299.preview.emergentagent.com/api"

# Test data
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
EXISTING_CUSTOMER_ID = "e22aeb9d-4ce2-4955-8fed-c6bcd5343773"  # HARI OM AUTO MOBILES
NON_EXISTENT_CUSTOMER_ID = "00000000-0000-0000-0000-000000000000"
DISPATCH_SLIP_NO = 288

# Test results
test_results = []
token = None


def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = {
        "test": test_name,
        "passed": passed,
        "details": details,
        "status": status
    }
    test_results.append(result)
    print(f"\n{status}: {test_name}")
    if details:
        print(f"  Details: {details}")


def test_1_login():
    """Test 1: Login as admin and obtain JWT token"""
    global token
    print("\n" + "="*80)
    print("TEST 1: Admin Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                token = data["token"]
                log_test("Admin Login", True, f"Token obtained successfully")
                return True
            else:
                log_test("Admin Login", False, f"No token in response: {data}")
                return False
        else:
            log_test("Admin Login", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Admin Login", False, f"Exception: {str(e)}")
        return False


def test_2_patch_existing_customer():
    """Test 2: PATCH existing customer with private_mark - should return 200"""
    print("\n" + "="*80)
    print("TEST 2: PATCH Existing Customer (Bug Fix Verification)")
    print("="*80)
    
    if not token:
        log_test("PATCH Existing Customer", False, "No auth token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(
            f"{BASE_URL}/customers/{EXISTING_CUSTOMER_ID}",
            json={"private_mark": "aaaa"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("id") == EXISTING_CUSTOMER_ID:
                log_test("PATCH Existing Customer", True, 
                        f"Customer updated successfully. Name: {data.get('name', 'N/A')}")
                return True
            else:
                log_test("PATCH Existing Customer", False, 
                        f"Response doesn't contain expected customer: {data}")
                return False
        else:
            log_test("PATCH Existing Customer", False, 
                    f"Expected 200, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("PATCH Existing Customer", False, f"Exception: {str(e)}")
        return False


def test_3_full_save_all_sequence():
    """Test 3: Full 'Save all' sequence for dispatch slip_no 288"""
    print("\n" + "="*80)
    print("TEST 3: Full 'Save All' Sequence for Dispatch Slip 288")
    print("="*80)
    
    if not token:
        log_test("Full Save All Sequence", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    dispatch_id = None
    
    # Step 3a: GET dispatch by slip number
    try:
        print("\nStep 3a: GET /dispatches/by-slip/288")
        response = requests.get(
            f"{BASE_URL}/dispatches/by-slip/{DISPATCH_SLIP_NO}",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            # Response has nested structure: {"dispatch": {...}}
            dispatch_data = data.get("dispatch", data)
            dispatch_id = dispatch_data.get("id")
            if dispatch_id:
                print(f"✓ Dispatch ID obtained: {dispatch_id}")
            else:
                log_test("Full Save All Sequence - Get Dispatch", False, 
                        f"No dispatch ID in response: {data}")
                return False
        else:
            log_test("Full Save All Sequence - Get Dispatch", False, 
                    f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Full Save All Sequence - Get Dispatch", False, f"Exception: {str(e)}")
        return False
    
    # Step 3b: PATCH dispatch with GR details
    try:
        print("\nStep 3b: PATCH /dispatches/{id} with GR details")
        response = requests.patch(
            f"{BASE_URL}/dispatches/{dispatch_id}",
            json={
                "gr_number": "1770117",
                "gr_date": "2026-08-18",
                "total_value": 5947
            },
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            log_test("Full Save All Sequence - Update GR", False, 
                    f"Status {response.status_code}: {response.text}")
            return False
        else:
            print("✓ GR details updated")
            
    except Exception as e:
        log_test("Full Save All Sequence - Update GR", False, f"Exception: {str(e)}")
        return False
    
    # Step 3c: PATCH customer with private_mark
    try:
        print("\nStep 3c: PATCH /customers/{cid} with private_mark")
        response = requests.patch(
            f"{BASE_URL}/customers/{EXISTING_CUSTOMER_ID}",
            json={"private_mark": "aaaa"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            log_test("Full Save All Sequence - Update Customer", False, 
                    f"Status {response.status_code}: {response.text}")
            return False
        else:
            print("✓ Customer private_mark updated")
            
    except Exception as e:
        log_test("Full Save All Sequence - Update Customer", False, f"Exception: {str(e)}")
        return False
    
    # Step 3d: PATCH dispatch with bag_count
    try:
        print("\nStep 3d: PATCH /dispatches/{id} with bag_count")
        response = requests.patch(
            f"{BASE_URL}/dispatches/{dispatch_id}",
            json={"bag_count": 1},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            log_test("Full Save All Sequence - Update Bag Count", False, 
                    f"Status {response.status_code}: {response.text}")
            return False
        else:
            print("✓ Bag count updated")
            log_test("Full Save All Sequence", True, 
                    "All steps completed successfully")
            return True
            
    except Exception as e:
        log_test("Full Save All Sequence - Update Bag Count", False, f"Exception: {str(e)}")
        return False


def test_4_patch_nonexistent_customer():
    """Test 4: PATCH non-existent customer - should return 404"""
    print("\n" + "="*80)
    print("TEST 4: PATCH Non-Existent Customer (Regression Test)")
    print("="*80)
    
    if not token:
        log_test("PATCH Non-Existent Customer", False, "No auth token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.patch(
            f"{BASE_URL}/customers/{NON_EXISTENT_CUSTOMER_ID}",
            json={"private_mark": "x"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 404:
            data = response.json()
            if "Customer not found" in data.get("detail", ""):
                log_test("PATCH Non-Existent Customer", True, 
                        "Correctly returned 404 'Customer not found'")
                return True
            else:
                log_test("PATCH Non-Existent Customer", False, 
                        f"Got 404 but wrong message: {data}")
                return False
        else:
            log_test("PATCH Non-Existent Customer", False, 
                    f"Expected 404, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("PATCH Non-Existent Customer", False, f"Exception: {str(e)}")
        return False


def test_5_get_blocked_items():
    """Test 5: GET blocked-items for existing customer - should return 200"""
    print("\n" + "="*80)
    print("TEST 5: GET Customer Blocked Items")
    print("="*80)
    
    if not token:
        log_test("GET Customer Blocked Items", False, "No auth token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/customers/{EXISTING_CUSTOMER_ID}/blocked-items",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("GET Customer Blocked Items", True, 
                    f"Successfully retrieved blocked items. Count: {len(data.get('items', []))}")
            return True
        else:
            log_test("GET Customer Blocked Items", False, 
                    f"Expected 200, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("GET Customer Blocked Items", False, f"Exception: {str(e)}")
        return False


def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["passed"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for result in test_results:
            if not result["passed"]:
                print(f"  - {result['test']}")
                print(f"    {result['details']}")
    
    print("\n" + "="*80)
    
    return failed == 0


if __name__ == "__main__":
    print("="*80)
    print("JK PRODUCTS FACTORY ORDER MANAGEMENT - BACKEND API TEST")
    print("Bug Fix Verification: PATCH /customers/{cid} false 404")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Run all tests
    test_1_login()
    test_2_patch_existing_customer()
    test_3_full_save_all_sequence()
    test_4_patch_nonexistent_customer()
    test_5_get_blocked_items()
    
    # Print summary
    all_passed = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)
