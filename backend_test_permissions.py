#!/usr/bin/env python3
"""
Backend API Test for Fine-Grained Edit/Delete Permission System
Testing separate edit:* and delete:* permissions per module
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://preview-24aug.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@factory.com"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "user@factory.com"
USER_PASSWORD = "user123"

# Test results
test_results = []
admin_token = None
user_token = None
user_id = None
test_customer_id = None
test_product_id = None


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


def test_1_admin_login():
    """Test 1: Admin login works and returns a token"""
    global admin_token
    print("\n" + "="*80)
    print("TEST 1: Admin Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                admin_token = data["token"]
                log_test("Admin Login", True, f"Token obtained successfully for {data['user'].get('email', 'N/A')}")
                return True
            else:
                log_test("Admin Login", False, f"Missing token or user in response: {data}")
                return False
        else:
            log_test("Admin Login", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Admin Login", False, f"Exception: {str(e)}")
        return False


def test_2_user_login():
    """Test 2: Regular user login works and returns a token"""
    global user_token
    print("\n" + "="*80)
    print("TEST 2: Regular User Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                user_token = data["token"]
                log_test("Regular User Login", True, f"Token obtained successfully for {data['user'].get('email', 'N/A')}")
                return True
            else:
                log_test("Regular User Login", False, f"Missing token or user in response: {data}")
                return False
        else:
            log_test("Regular User Login", False, f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Regular User Login", False, f"Exception: {str(e)}")
        return False


def get_test_data():
    """Get test customer and product IDs"""
    global test_customer_id, test_product_id, user_id
    
    if not admin_token:
        print("⚠️  No admin token, skipping test data retrieval")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get a customer
    try:
        response = requests.get(f"{BASE_URL}/customers", headers=headers, timeout=10)
        if response.status_code == 200:
            customers = response.json()
            if customers and len(customers) > 0:
                test_customer_id = customers[0].get("id")
                print(f"✓ Test customer ID: {test_customer_id}")
    except Exception as e:
        print(f"⚠️  Could not get customers: {e}")
    
    # Get a product
    try:
        response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=10)
        if response.status_code == 200:
            products = response.json()
            if products and len(products) > 0:
                test_product_id = products[0].get("id")
                print(f"✓ Test product ID: {test_product_id}")
    except Exception as e:
        print(f"⚠️  Could not get products: {e}")
    
    # Get user ID for user@factory.com
    try:
        response = requests.get(f"{BASE_URL}/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get("email") == USER_EMAIL:
                    user_id = user.get("id")
                    print(f"✓ Regular user ID: {user_id}")
                    break
    except Exception as e:
        print(f"⚠️  Could not get users: {e}")
    
    return test_customer_id and test_product_id and user_id


def test_3_user_no_permissions():
    """Test 3: Regular user with default (no grants) cannot edit customers or products"""
    print("\n" + "="*80)
    print("TEST 3: Regular User Without Permissions (Expect 403)")
    print("="*80)
    
    if not user_token or not test_customer_id or not test_product_id:
        log_test("User Without Permissions", False, "Missing token or test data")
        return False
    
    headers = {"Authorization": f"Bearer {user_token}"}
    all_passed = True
    
    # Test 3a: PATCH customer should fail with 403
    try:
        print("\nTest 3a: PATCH /customers/{id} (expect 403)")
        response = requests.patch(
            f"{BASE_URL}/customers/{test_customer_id}",
            json={"private_mark": "x"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 403:
            print("✓ Correctly blocked with 403")
        else:
            log_test("User PATCH Customer Without Permission", False, 
                    f"Expected 403, got {response.status_code}")
            all_passed = False
    except Exception as e:
        log_test("User PATCH Customer Without Permission", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3b: PATCH product should fail with 403
    try:
        print("\nTest 3b: PATCH /products/{id} (expect 403)")
        response = requests.patch(
            f"{BASE_URL}/products/{test_product_id}",
            json={"max_per_bag": 10},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 403:
            print("✓ Correctly blocked with 403")
        else:
            log_test("User PATCH Product Without Permission", False, 
                    f"Expected 403, got {response.status_code}")
            all_passed = False
    except Exception as e:
        log_test("User PATCH Product Without Permission", False, f"Exception: {str(e)}")
        all_passed = False
    
    if all_passed:
        log_test("User Without Permissions", True, "Both PATCH operations correctly blocked with 403")
    
    return all_passed


def test_4_grant_edit_customers():
    """Test 4: Admin grants regular user ONLY edit:customers permission"""
    print("\n" + "="*80)
    print("TEST 4: Admin Grants edit:customers Permission")
    print("="*80)
    
    if not admin_token or not user_id:
        log_test("Grant edit:customers Permission", False, "Missing admin token or user ID")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Grant edit:customers (include default nav keys + edit:customers)
        permissions = [
            "dashboard", "orders", "dispatch", "dispatchLedger", "dailyReport", 
            "estimates", "customers", "products", "edit:customers"
        ]
        
        response = requests.patch(
            f"{BASE_URL}/users/{user_id}/permissions",
            json={"permissions": permissions},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            returned_perms = data.get("permissions", [])
            if "edit:customers" in returned_perms:
                log_test("Grant edit:customers Permission", True, 
                        f"Successfully granted. Permissions: {returned_perms}")
                return True
            else:
                log_test("Grant edit:customers Permission", False, 
                        f"edit:customers not in returned permissions: {returned_perms}")
                return False
        else:
            log_test("Grant edit:customers Permission", False, 
                    f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Grant edit:customers Permission", False, f"Exception: {str(e)}")
        return False


def test_5_user_with_edit_customers():
    """Test 5: Regular user with edit:customers can edit customers but not delete or edit products"""
    print("\n" + "="*80)
    print("TEST 5: Regular User With edit:customers Permission")
    print("="*80)
    
    if not user_token or not test_customer_id or not test_product_id:
        log_test("User With edit:customers", False, "Missing token or test data")
        return False
    
    headers = {"Authorization": f"Bearer {user_token}"}
    all_passed = True
    
    # Test 5a: PATCH customer should now succeed with 200
    try:
        print("\nTest 5a: PATCH /customers/{id} (expect 200)")
        response = requests.patch(
            f"{BASE_URL}/customers/{test_customer_id}",
            json={"private_mark": "test_edit"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            print("✓ Successfully edited customer with edit:customers permission")
        else:
            log_test("User PATCH Customer With Permission", False, 
                    f"Expected 200, got {response.status_code}: {response.text}")
            all_passed = False
    except Exception as e:
        log_test("User PATCH Customer With Permission", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 5b: DELETE customer should fail with 403 (delete:customers not granted)
    try:
        print("\nTest 5b: DELETE /customers/{id} (expect 403 - delete:customers not granted)")
        # Use a non-existent ID to avoid actually deleting data
        fake_customer_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/customers/{fake_customer_id}",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 403:
            print("✓ Correctly blocked DELETE with 403 (permission check before business logic)")
        else:
            log_test("User DELETE Customer Without delete Permission", False, 
                    f"Expected 403, got {response.status_code}")
            all_passed = False
    except Exception as e:
        log_test("User DELETE Customer Without delete Permission", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 5c: PATCH product should still fail with 403 (edit:products not granted)
    try:
        print("\nTest 5c: PATCH /products/{id} (expect 403 - edit:products not granted)")
        response = requests.patch(
            f"{BASE_URL}/products/{test_product_id}",
            json={"max_per_bag": 10},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 403:
            print("✓ Correctly blocked with 403")
        else:
            log_test("User PATCH Product Without Permission", False, 
                    f"Expected 403, got {response.status_code}")
            all_passed = False
    except Exception as e:
        log_test("User PATCH Product Without Permission", False, f"Exception: {str(e)}")
        all_passed = False
    
    if all_passed:
        log_test("User With edit:customers", True, 
                "PATCH customer allowed (200), DELETE customer blocked (403), PATCH product blocked (403)")
    
    return all_passed


def test_6_admin_can_edit():
    """Test 6: Admin can PATCH customers regardless of grants"""
    print("\n" + "="*80)
    print("TEST 6: Admin Can Edit Customers (Regression)")
    print("="*80)
    
    if not admin_token or not test_customer_id:
        log_test("Admin Can Edit", False, "Missing admin token or test customer")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/customers/{test_customer_id}",
            json={"private_mark": "admin_test"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            log_test("Admin Can Edit", True, "Admin successfully edited customer")
            return True
        else:
            log_test("Admin Can Edit", False, 
                    f"Expected 200, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Admin Can Edit", False, f"Exception: {str(e)}")
        return False


def test_7_invalid_permission_keys():
    """Test 7: Validation - invalid permission keys should be rejected with 400"""
    print("\n" + "="*80)
    print("TEST 7: Invalid Permission Keys Validation")
    print("="*80)
    
    if not admin_token or not user_id:
        log_test("Invalid Permission Keys", False, "Missing admin token or user ID")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/users/{user_id}/permissions",
            json={"permissions": ["bogus:key"]},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 400:
            log_test("Invalid Permission Keys", True, "Invalid keys correctly rejected with 400")
            return True
        else:
            log_test("Invalid Permission Keys", False, 
                    f"Expected 400, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Invalid Permission Keys", False, f"Exception: {str(e)}")
        return False


def test_8_regression_admin_patch():
    """Test 8: Regression - Admin PATCH /customers with private_mark still works"""
    print("\n" + "="*80)
    print("TEST 8: Regression - Admin PATCH Customer private_mark")
    print("="*80)
    
    if not admin_token or not test_customer_id:
        log_test("Regression Admin PATCH", False, "Missing admin token or test customer")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/customers/{test_customer_id}",
            json={"private_mark": "regression_test"},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Regression Admin PATCH", True, 
                    f"Admin PATCH customer still works. Customer: {data.get('name', 'N/A')}")
            return True
        else:
            log_test("Regression Admin PATCH", False, 
                    f"Expected 200, got {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        log_test("Regression Admin PATCH", False, f"Exception: {str(e)}")
        return False


def reset_user_permissions():
    """Reset regular user permissions back to null"""
    print("\n" + "="*80)
    print("CLEANUP: Reset User Permissions")
    print("="*80)
    
    if not admin_token or not user_id:
        print("⚠️  Cannot reset permissions - missing admin token or user ID")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.patch(
            f"{BASE_URL}/users/{user_id}/permissions",
            json={"permissions": None},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ User permissions reset to null")
            return True
        else:
            print(f"⚠️  Could not reset permissions: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Exception resetting permissions: {str(e)}")
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
    else:
        print("\n✅ ALL TESTS PASSED!")
    
    print("\n" + "="*80)
    
    return failed == 0


if __name__ == "__main__":
    print("="*80)
    print("FINE-GRAINED EDIT/DELETE PERMISSION SYSTEM TEST")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Run all tests
    test_1_admin_login()
    test_2_user_login()
    
    # Get test data
    print("\n" + "="*80)
    print("SETUP: Getting Test Data")
    print("="*80)
    get_test_data()
    
    # Run permission tests
    test_3_user_no_permissions()
    test_4_grant_edit_customers()
    test_5_user_with_edit_customers()
    test_6_admin_can_edit()
    test_7_invalid_permission_keys()
    test_8_regression_admin_patch()
    
    # Cleanup
    reset_user_permissions()
    
    # Print summary
    all_passed = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)
