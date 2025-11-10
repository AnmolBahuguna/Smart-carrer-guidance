#!/usr/bin/env python
"""
SmartCareer Website Testing Script
Tests all major routes and functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def print_result(test_name, success, details=""):
    """Print colored test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def test_pages():
    """Test all main pages"""
    print("\n" + "="*60)
    print("TESTING MAIN PAGES")
    print("="*60)
    
    pages = [
        ('/', 'Home Page'),
        ('/quiz', 'Quiz Page'),
        ('/chatbot', 'Chatbot Page'),
        ('/login', 'Login Page'),
        ('/register', 'Register Page'),
        ('/college-finder', 'College Finder'),
        ('/scholarships', 'Scholarships'),
        ('/career-insights', 'Career Insights'),
        ('/resume-builder', 'Resume Builder'),
        ('/ai-ml-datascience', 'AI/ML/Data Science'),
        ('/roadmap', 'Roadmap'),
    ]
    
    results = []
    for route, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            success = response.status_code == 200
            print_result(name, success, f"Status: {response.status_code}")
            results.append(success)
        except Exception as e:
            print_result(name, False, f"Error: {str(e)}")
            results.append(False)
    
    return results

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    endpoints = [
        ('/api/scholarships', 'Scholarships API'),
        ('/api/internships', 'Internships API'),
        ('/api/jobs', 'Jobs API'),
        ('/api/opportunities', 'Opportunities API'),
    ]
    
    results = []
    for route, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = data.get('count', data.get('counts', {}).get('total', 0))
                print_result(name, success, f"Status: {response.status_code}, Items: {count}")
            else:
                print_result(name, success, f"Status: {response.status_code}")
            
            results.append(success)
        except Exception as e:
            print_result(name, False, f"Error: {str(e)}")
            results.append(False)
    
    return results

def test_chatbot():
    """Test chatbot functionality"""
    print("\n" + "="*60)
    print("TESTING CHATBOT")
    print("="*60)
    
    results = []
    
    # Test regular chat endpoint
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={'message': 'hello'},
            timeout=10
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            has_response = 'response' in data and len(data['response']) > 0
            print_result("Chatbot Regular Response", has_response, 
                        f"Got response: {data['response'][:50]}..." if has_response else "No response")
            results.append(has_response)
        else:
            print_result("Chatbot Regular Response", False, f"Status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print_result("Chatbot Regular Response", False, f"Error: {str(e)}")
        results.append(False)
    
    return results

def test_authentication():
    """Test user authentication"""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION")
    print("="*60)
    
    session = requests.Session()
    results = []
    
    # Test registration
    try:
        test_user = {
            'name': 'Test User',
            'email': f'test_{datetime.now().timestamp()}@example.com',
            'password': 'TestPass123'
        }
        
        response = session.post(
            f"{BASE_URL}/register",
            data=test_user,
            allow_redirects=False,
            timeout=5
        )
        
        # Flask redirects on success (302)
        success = response.status_code in [200, 302]
        print_result("User Registration", success, f"Status: {response.status_code}")
        results.append(success)
        
        # Test login
        response = session.post(
            f"{BASE_URL}/login",
            data={'email': test_user['email'], 'password': test_user['password']},
            allow_redirects=False,
            timeout=5
        )
        
        success = response.status_code in [200, 302]
        print_result("User Login", success, f"Status: {response.status_code}")
        results.append(success)
        
    except Exception as e:
        print_result("Authentication", False, f"Error: {str(e)}")
        results.append(False)
        results.append(False)
    
    return results

def test_quiz_submission():
    """Test quiz submission"""
    print("\n" + "="*60)
    print("TESTING QUIZ SUBMISSION")
    print("="*60)
    
    results = []
    
    try:
        quiz_data = {
            'answers': {
                'interests': ['technology', 'analytics'],
                'skills': ['programming', 'problem solving'],
                'personality': 'analytical'
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/submit_quiz",
            json=quiz_data,
            timeout=10
        )
        
        success = response.status_code == 200
        
        if success:
            data = response.json()
            has_recommendations = 'recommendations' in data and len(data['recommendations']) > 0
            print_result("Quiz Submission", has_recommendations, 
                        f"Got {len(data.get('recommendations', []))} career recommendations")
            results.append(has_recommendations)
        else:
            print_result("Quiz Submission", False, f"Status: {response.status_code}")
            results.append(False)
            
    except Exception as e:
        print_result("Quiz Submission", False, f"Error: {str(e)}")
        results.append(False)
    
    return results

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 SMARTCAREER WEBSITE TESTING")
    print("="*60)
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Run all test suites
    all_results.extend(test_pages())
    all_results.extend(test_api_endpoints())
    all_results.extend(test_chatbot())
    all_results.extend(test_authentication())
    all_results.extend(test_quiz_submission())
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Website is working perfectly!")
    elif success_rate >= 80:
        print("\n⚠️  Most tests passed, but some issues need attention")
    else:
        print("\n❌ Multiple failures detected. Please review errors above")
    
    print("="*60)

if __name__ == "__main__":
    main()
