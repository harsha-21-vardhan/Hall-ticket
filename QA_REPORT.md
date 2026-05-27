# QA Report: Hall Ticket Generation System

## 1. Executive Summary

**Project Name:** Hall Ticket Generation System with QR Code  
**Tech Stack:** Flask, SQLite, HTML/CSS, JavaScript  
**Type:** Web Application  
**Test Date:** 2026-04-10

---

## 2. Manual Testing

### 2.1 Test Cases - Authentication Module

| ID | Test Case | Test Steps | Expected Result | Actual Result | Status |
|---|-----------|-----------|-----------------|--------------|--------|
| TC-001 | Student Login - Valid | 1. Navigate to /login 2. Enter valid email 3. Enter valid password 4. Click Login | Redirect to student dashboard | - | PENDING |
| TC-002 | Student Login - Invalid Email | 1. Navigate to /login 2. Enter unregistered email 3. Enter any password 4. Click Login | Flash error: "Email not found" | - | PENDING |
| TC-003 | Student Login - Invalid Password | 1. Navigate to /login 2. Enter valid email 3. Enter wrong password 4. Click Login | Flash error: "Invalid password" | - | PENDING |
| TC-004 | Admin Login - Valid | 1. Navigate to /admin/login 2. Enter admin username 3. Enter admin password 4. Click Login | Redirect to admin dashboard | - | PENDING |
| TC-005 | Admin Login - Invalid | 1. Navigate to /admin/login 2. Enter wrong credentials 3. Click Login | Flash error: "Invalid credentials" | - | PENDING |
| TC-006 | Forgot Password - Student | 1. Click "Forgot Password" 2. Enter email 3. Enter register number 4. Enter new password 5. Submit | Password reset successful | - | PENDING |
| TC-007 | Logout | 1. Login as student 2. Click Logout | Redirect to home page | - | PENDING |

### 2.2 Test Cases - Registration Module

| ID | Test Case | Test Steps | Expected Result | Status |
|---|-----------|-----------|-----------------|--------|
| TC-008 | Register New Student | 1. Navigate to /register 2. Fill all fields 3. Submit | Account created, redirect to login | PENDING |
| TC-009 | Register - Duplicate Email | 1. Use already registered email 2. Submit | Flash: "Email already registered" | PENDING |
| TC-010 | Register - Duplicate Reg Number | 1. Use existing register number 2. Submit | Flash: "Register number already exists" | PENDING |
| TC-011 | Register - Missing Fields | 1. Leave required fields empty 2. Submit | Form validation error | PENDING |
| TC-012 | Register - Invalid Email Format | 1. Enter invalid email format 2. Submit | HTML5 validation error | PENDING |

### 2.3 Test Cases - Student Dashboard

| ID | Test Case | Test Steps | Expected Result | Status |
|---|-----------|-----------|-----------------|--------|
| TC-013 | View Dashboard - With Ticket | 1. Login as student with ticket | Show QR code, download buttons | PENDING |
| TC-014 | View Dashboard - Without Ticket | 1. Login as student without ticket | Show "Contact admin" message | PENDING |
| TC-015 | Download PDF | 1. Click "Download PDF" | PDF file downloads | PENDING |
| TC-016 | View QR Code | 1. Click "View QR Code" | QR image displayed | PENDING |
| TC-017 | View Exam Schedule | 1. Login as student | Exam table displayed | PENDING |

### 2.4 Test Cases - Admin Dashboard

| ID | Test Case | Test Steps | Expected Result | Status |
|---|-----------|-----------|-----------------|--------|
| TC-018 | Add Student | 1. Click Add Student 2. Fill form 3. Submit | Student added to list | PENDING |
| TC-019 | Edit Student | 1. Click edit on student 2. Modify fields 3. Save | Student updated | PENDING |
| TC-020 | Delete Student | 1. Click delete 2. Confirm | Student removed | PENDING |
| TC-021 | Add Subject | 1. Click Add Subject 2. Fill form 3. Submit | Subject added | PENDING |
| TC-022 | Delete Subject | 1. Click delete on subject | Subject removed | PENDING |
| TC-023 | Add Exam | 1. Click Add Exam 2. Fill exam details 3. Submit | Exam added | PENDING |
| TC-024 | Generate Single Ticket | 1. Click generate ticket for student | Ticket created, QR generated | PENDING |
| TC-025 | Generate All Tickets | 1. Click "Generate All Tickets" | Tickets for all students | PENDING |
| TC-026 | View All Tickets | 1. Click "View All Tickets" | List of all tickets | PENDING |

### 2.5 Test Cases - QR Code & PDF

| ID | Test Case | Test Steps | Expected Result | Status |
|---|-----------|-----------|-----------------|--------|
| TC-027 | QR Code Generation | 1. Admin generates ticket | QR image created in static/qr_codes | PENDING |
| TC-028 | PDF Download | 1. Student downloads ticket | PDF with all details | PENDING |
| TC-029 | PDF Contains Correct Data | 1. Download PDF | Student info, exam schedule, QR code | PENDING |
| TC-030 | Verify Valid Token | 1. Navigate to /verify/{token} | Shows student details | PENDING |
| TC-031 | Verify Invalid Token | 1. Navigate to /verify/invalid | Shows invalid message | PENDING |

### 2.6 Edge Cases

| ID | Test Case | Test Steps | Expected Result | Status |
|---|-----------|-----------|-----------------|--------|
| EC-001 | Empty Database | 1. Login with no data | Show empty states | PENDING |
| EC-002 | Very Long Input | 1. Enter 1000+ characters | Handle gracefully | PENDING |
| EC-003 | Special Characters in Name | 1. Enter name with quotes/special chars | Store correctly | PENDING |
| EC-004 | Duplicate Ticket Generation | 1. Try to generate second ticket | Show warning message | PENDING |
| EC-005 | Concurrent Login | 1. Login from two browsers | Handle session properly | PENDING |

---

## 3. Bug Detection Report

### 3.1 Critical Bugs

| Bug ID | Description | Category | Steps to Reproduce | Expected | Actual | Severity |
|--------|------------|----------|-------------------|-----------|--------|----------|
| BUG-001 | SQL Injection in Login | Security | Enter `' OR '1'='1` in email field | Should not authenticate | May authenticate | CRITICAL |
| BUG-002 | Hardcoded Secret Key | Security | Check app.py line 18 | Should use env variable | Hardcoded | CRITICAL |
| BUG-003 | Session Cookie Not HTTPOnly | Security | Check browser cookies | HTTPOnly=True | False (line 19) | CRITICAL |

### 3.2 Major Bugs

| Bug ID | Description | Category | Steps to Reproduce | Expected | Actual | Severity |
|--------|------------|----------|-------------------|-----------|--------|----------|
| BUG-004 | No CSRF Protection | Security | Submit form from external site | Should reject | No protection | MAJOR |
| BUG-005 | Admin Forgot Password No Auth | Auth | Access /admin/forgot-password directly | Should require admin login | No protection | MAJOR |
| BUG-006 | Delete Without Confirmation UI | Usability | Click delete button | Show confirmation modal | Uses alert() | MAJOR |
| BUG-007 | No Pagination | Performance | Add 1000+ students | Paginate results | Single page | MAJOR |
| BUG-008 | QR URL Hardcoded to localhost | Functionality | Generate QR code | Dynamic URL | localhost:5000 | MAJOR |

### 3.3 Minor Bugs

| Bug ID | Description | Category | Steps to Reproduce | Expected | Actual | Severity |
|--------|------------|----------|-------------------|-----------|--------|----------|
| BUG-009 | No Input Sanitization | UI | Enter HTML in name field | Strip tags | Stores raw | MINOR |
| BUG-010 | Time Input Not Validated | UI | Enter random text in time | Validate format | Accepts any | MINOR |
| BUG-011 | Missing Error Handling | Error | Disable database | Show error page | May crash | MINOR |
| BUG-012 | No Loading Indicator | UX | Generate many tickets | Show spinner | No feedback | MINOR |

---

## 4. Automation Testing Strategy

### 4.1 Recommended Tools

| Tool | Purpose | Version |
|------|---------|---------|
| Selenium WebDriver | Web UI Automation | 4.x |
| PyTest | Test Framework | 7.x |
| pytest-html | HTML Reporter | 3.x |
| Requests | API Testing | 2.x |

### 4.2 Sample Test Scripts

```python
# tests/test_auth.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

BASE_URL = "http://localhost:5000"

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

class TestStudentLogin:
    def test_valid_login(self, browser):
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.NAME, "email").send_keys("student@test.com")
        browser.find_element(By.NAME, "password").send_keys("password123")
        browser.find_element(By.TYPE, "submit").click()
        assert "/student/dashboard" in browser.current_url
    
    def test_invalid_email(self, browser):
        browser.get(f"{BASE_URL}/login")
        browser.find_element(By.NAME, "email").send_keys("wrong@test.com")
        browser.find_element(By.NAME, "password").send_keys("password123")
        browser.find_element(By.TYPE, "submit").click()
        assert "Email not found" in browser.page_source

class TestRegistration:
    def test_register_success(self, browser):
        browser.get(f"{BASE_URL}/register")
        browser.find_element(By.NAME, "name").send_keys("Test Student")
        browser.find_element(By.NAME, "email").send_keys("new@test.com")
        browser.find_element(By.NAME, "register_number").send_keys("REG999")
        browser.find_element(By.NAME, "password").send_keys("pass123")
        browser.find_element(By.NAME, "department").send_keys("CSE")
        browser.find_element(By.TYPE, "submit").click()
        assert "/login" in browser.current_url

class TestNavigation:
    def test_home_to_login(self, browser):
        browser.get(BASE_URL)
        browser.find_element(By.LINK_TEXT, "Login").click()
        assert "/login" in browser.current_url
    
    def test_home_to_register(self, browser):
        browser.get(BASE_URL)
        browser.find_element(By.LINK_TEXT, "Register").click()
        assert "/register" in browser.current_url
```

```python
# tests/test_api.py
import pytest
import requests

BASE_URL = "http://localhost:5000"

class TestAPI:
    def test_home_page(self):
        response = requests.get(BASE_URL)
        assert response.status_code == 200
    
    def test_login_page(self):
        response = requests.get(f"{BASE_URL}/login")
        assert response.status_code == 200
    
    def test_register_page(self):
        response = requests.get(f"{BASE_URL}/register")
        assert response.status_code == 200
    
    def test_nonexistent_page(self):
        response = requests.get(f"{BASE_URL}/invalid-page")
        assert response.status_code == 404
```

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def app():
    from app import app
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

---

## 5. API Testing

### 5.1 API Test Cases

| ID | Endpoint | Method | Test Data | Expected | Status |
|----|----------|--------|----------|----------|----------|--------|
| API-001 | / | GET | - | 200, HTML | PENDING |
| API-002 | /login | GET | - | 200, HTML | PENDING |
| API-003 | /register | GET | - | 200, HTML | PENDING |
| API-004 | /student/dashboard | GET | No session | 302 Redirect | PENDING |
| API-005 | /admin/dashboard | GET | No admin session | 302 Redirect | PENDING |
| API-006 | /chatbot | POST | {"message": "help"} | 200, JSON | PENDING |
| API-007 | /download/<token> | GET | Valid token | 200, PDF | PENDING |
| API-008 | /download/<token> | GET | Invalid token | 302, Flash error | PENDING |
| API-009 | /verify/<token> | GET | Valid token | 200, HTML | PENDING |
| API-010 | /verify/<token> | GET | Invalid token | 200, invalid=False | PENDING |

---

## 6. Performance Testing

### 6.1 Load Testing Scenarios

| Scenario | Target | Metrics |
|----------|--------|----------|
| Homepage Load | 100 users/sec | Response time < 2s |
| Login Concurrent | 50 users | Handle without error |
| Generate 100 Tickets | Batch | Complete < 30s |
| PDF Download | 20 concurrent | Response < 5s |
| Database Query | Large dataset | < 500ms |

### 6.2 Identified Bottlenecks

1. **PDF Generation** - Uses reportlab, generates on-demand (slow)
2. **No Caching** - QR codes regenerated each time
3. **No Pagination** - Loads all records
4. **SQLite** - Not suitable for high concurrency
5. **No Indexes** - Slow queries on large tables

---

## 7. Security Testing

### 7.1 Vulnerability Tests

| Test | Expected | Status |
|------|----------|--------|
| SQL Injection - Login | No authentication bypass | PENDING |
| SQL Injection - Register | No data manipulation | PENDING |
| XSS in Name Field | Scripts should not execute | PENDING |
| Session Hijacking | Secure session tokens | PENDING |
| Password in Logs | Passwords not logged | PENDING |
| Directory Traversal | Should be blocked | PENDING |
| CSRF | Forms should have tokens | PENDING |

### 7.2 Security Recommendations

1. **Immediate Fixes:**
   - Change SECRET_KEY to environment variable
   - Enable SESSION_COOKIE_HTTPONLY = True
   - Add CSRF protection (Flask-WTF)
   - Add SQLAlchemy ORM with parameterized queries

2. **Production Hardening:**
   - Use production WSGI server (gunicorn)
   - Enable HTTPS
   - Use MySQL/PostgreSQL
   - Add rate limiting
   - Add input validation (WTForms)
   - Add security headers (Flask-Talisman)

---

## 8. Test Summary

| Category | Total | Passed | Failed | Pending |
|----------|-------|--------|--------|---------|
| Manual Test Cases | 31 | 0 | 0 | 31 |
| Edge Cases | 5 | 0 | 0 | 5 |
| API Tests | 10 | 0 | 0 | 10 |
| Security Tests | 7 | 0 | 0 | 7 |
| **TOTAL** | **53** | **0** | **0** | **53** |

---

## 9. Bugs Summary

| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 5 |
| Minor | 4 |
| **TOTAL** | **12** |

---

## 10. Improvement Suggestions

### High Priority

1. **Security Fixes**
   - Add CSRF protection
   - Use environment variables for secrets
   - Enable session security flags
   - Add input validation

2. **Performance**
   - Add pagination
   - Cache QR codes
   - Add database indexes

3. **Reliability**
   - Add error handling
   - Add logging
   - Add backup strategy

### Medium Priority

4. **User Experience**
   - Add loading indicators
   - Improve mobile responsiveness
   - Add confirmation modals
   - Add form validation feedback

5. **Functionality**
   - Add password strength validation
   - Add email verification
   - Add ticket expiration
   - Add audit logs

### Low Priority

6. **Enhancements**
   - Add dark mode
   - Add export to Excel
   - Add email notifications
   - Add mobile app support

---

## Appendix: Quick Reference

### Default Credentials
- **Admin:** admin / admin123
- **Test Student:** Create via registration page

### Key Endpoints
| Route | Description |
|-------|-------------|
| / | Home page |
| /login | Student login |
| /register | Student registration |
| /admin/login | Admin login |
| /student/dashboard | Student dashboard |
| /admin/dashboard | Admin dashboard |
| /download/<token> | Download PDF |
| /verify/<token> | Verify ticket |
| /scanner | QR scanner |
| /chatbot | AI assistant |

### Database Models
- Admin (id, username, password)
- Student (id, name, email, register_number, password, department)
- Subject (id, subject_name, subject_code)
- Exam (id, subject_id, date, time, end_time, hall_no, exam_name)
- HallTicket (id, student_id, qr_token, pdf_path, generated_at, is_used)

---

*Report Generated: 2026-04-10*