#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
import time

class JanSevaAPITester:
    def __init__(self, base_url="https://yojana-match.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.test_user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.scheme_id = "scheme_1"  # PM Scholarship Scheme for testing

    def log(self, message, success=None):
        if success is True:
            print(f"✅ {message}")
        elif success is False:
            print(f"❌ {message}")
        else:
            print(f"🔍 {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        default_headers = {'Content-Type': 'application/json'}
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"{name} - Status: {response.status_code}", True)
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"{name} - Expected {expected_status}, got {response.status_code}", False)
                if response.content:
                    try:
                        error_data = response.json()
                        self.log(f"Error details: {error_data}")
                    except:
                        self.log(f"Response: {response.text[:200]}")
                return False, {}

        except requests.exceptions.ConnectionError:
            self.log(f"{name} - Connection failed. Server might be down", False)
            return False, {}
        except requests.exceptions.Timeout:
            self.log(f"{name} - Request timeout", False)
            return False, {}
        except Exception as e:
            self.log(f"{name} - Error: {str(e)}", False)
            return False, {}

    def test_signup(self):
        """Test user signup"""
        timestamp = int(time.time())
        test_data = {
            "name": f"Test User {timestamp}",
            "email": f"testuser{timestamp}@example.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.test_user_id = response.get('user', {}).get('id')
            return True
        return False

    def test_login(self):
        """Test user login with existing user"""
        # First create a user
        timestamp = int(time.time())
        signup_data = {
            "name": f"Login Test User {timestamp}",
            "email": f"logintest{timestamp}@example.com", 
            "password": "LoginPass123!"
        }
        
        # Create user
        signup_success, _ = self.run_test(
            "Signup for Login Test",
            "POST", 
            "auth/signup",
            200,
            data=signup_data
        )
        
        if not signup_success:
            return False
            
        # Now test login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login", 
            200,
            data=login_data
        )
        
        if success and 'token' in response:
            # Keep the original token for other tests
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        invalid_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        success, _ = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data=invalid_data
        )
        return success

    def test_quiz_submission(self):
        """Test quiz submission"""
        quiz_data = {
            "age": 22,
            "gender": "Female",
            "state": "Karnataka", 
            "area": "Urban",
            "income": "₹1,00,000 – ₹3,00,000",
            "occupation": "Student",
            "education": "Undergraduate",
            "category": "OBC",
            "has_land": "No", 
            "is_disabled": "No"
        }
        
        success, response = self.run_test(
            "Quiz Submission",
            "POST",
            "quiz/submit",
            200,
            data=quiz_data
        )
        
        if success:
            # Check response structure
            if 'eligible_schemes' in response and 'fallback_schemes' in response:
                self.log(f"Found {len(response['eligible_schemes'])} eligible schemes")
                self.log(f"Found {len(response['fallback_schemes'])} fallback schemes") 
                return True
            else:
                self.log("Invalid response structure for quiz", False)
                return False
        return False

    def test_save_scheme(self):
        """Test saving a scheme"""
        success, response = self.run_test(
            "Save Scheme",
            "POST",
            f"schemes/save/{self.scheme_id}",
            200
        )
        return success

    def test_get_saved_schemes(self):
        """Test getting saved schemes"""
        success, response = self.run_test(
            "Get Saved Schemes",
            "GET",
            "schemes/saved",
            200
        )
        
        if success:
            if 'schemes' in response:
                self.log(f"Found {len(response['schemes'])} saved schemes")
                return True
            else:
                self.log("Invalid response structure for saved schemes", False)
                return False
        return False

    def test_unsave_scheme(self):
        """Test removing a scheme from saved"""
        success, response = self.run_test(
            "Unsave Scheme",
            "DELETE",
            f"schemes/unsave/{self.scheme_id}",
            200
        )
        return success

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        old_token = self.token
        self.token = None
        
        success, _ = self.run_test(
            "Unauthorized Quiz Access",
            "POST",
            "quiz/submit",
            401,
            data={"age": 25}
        )
        
        self.token = old_token
        return success

def main():
    print("🚀 Starting Jan-Seva Backend API Tests")
    print("="*50)
    
    tester = JanSevaAPITester()
    
    # Test sequence
    tests = [
        ("Signup", tester.test_signup),
        ("Login", tester.test_login), 
        ("Invalid Login", tester.test_invalid_login),
        ("Unauthorized Access", tester.test_unauthorized_access),
        ("Quiz Submission", tester.test_quiz_submission),
        ("Save Scheme", tester.test_save_scheme),
        ("Get Saved Schemes", tester.test_get_saved_schemes),
        ("Unsave Scheme", tester.test_unsave_scheme),
    ]
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            if not result:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Results summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Backend APIs are working excellently!")
        return 0
    elif success_rate >= 70:
        print("⚠️ Backend APIs are mostly working with some issues")
        return 1
    else:
        print("💥 Multiple backend API failures detected")
        return 2

if __name__ == "__main__":
    sys.exit(main())