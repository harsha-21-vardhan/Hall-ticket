# Smart Hall Ticket Management System with QR Code Verification & AI Admin Assistant

A complete production-level web application for managing exam hall tickets with QR code verification and AI-powered admin assistant.

## Features

- **Admin Module**: Login, dashboard, CRUD operations for students/subjects/exams, hall ticket generation
- **Student Module**: Login, dashboard, QR code display, PDF download
- **QR Hall Ticket**: Unique secure tokens, embedded QR codes in PDF
- **QR Download System**: Token-based validation and PDF download
- **Invigilator Verification**: Mobile camera QR scanner for student verification
- **AI Chatbot**: NLP-based admin assistant for database operations

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, CSS, Bootstrap 5, JavaScript
- Database: MySQL
- QR Code: python-qrcode
- PDF Generation: reportlab
- QR Scanner: html5-qrcode

## Project Structure

```
/project
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── database.sql          # Database schema
├── README.md             # Setup instructions
├── static/
│   ├── qr_codes/         # Generated QR images
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── scanner.html
    ├── verify.html
    ├── admin/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── edit_student.html
    │   ├── edit_subject.html
    │   ├── edit_exam.html
    │   └── view_tickets.html
    └── student/
        ├── dashboard.html
        └── qr_code.html
```

## Setup Instructions

### 1. Install Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher

### 2. MySQL Setup

```sql
-- Create database
CREATE DATABASE hall_ticket_db;

-- Import schema (optional - app creates tables automatically)
mysql -u root -p hall_ticket_db < database.sql
```

### 3. Configure Database Connection

Edit `app.py` to update database credentials:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/hall_ticket_db'
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The application will:
- Create database tables automatically
- Create default admin account (username: admin, password: admin123)

### 6. Access the Application

- Home: http://localhost:5000/
- Admin: http://localhost:5000/admin/login
- Student Login: http://localhost:5000/login
- QR Scanner: http://localhost:5000/scanner

## Default Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | admin    | admin123 |

## AI Chatbot Commands

Try these commands in the admin dashboard chatbot:

- `add student Rahul CSE` - Add new student
- `create subject DBMS` - Create new subject
- `show all students` - List all students
- `show all subjects` - List all subjects
- `generate all tickets` - Generate tickets for all students
- `total students` - Count students
- `total subjects` - Count subjects
- `total exams` - Count exams
- `help` - Show all commands

## Database Tables

### students
- id (PK)
- name
- email (unique)
- register_number (unique)
- password (hashed)
- department

### subjects
- id (PK)
- subject_name
- subject_code (unique)

### exams
- id (PK)
- subject_id (FK)
- exam_name
- date
- time
- hall_no

### hall_tickets
- id (PK)
- student_id (FK)
- qr_token (unique)
- pdf_path
- generated_at
- is_used

### admins
- id (PK)
- username (unique)
- password (hashed)

## Security Features

- BCrypt password hashing
- Secure UUID tokens
- Session-based authentication
- Input validation

## Running for Production

1. Change `SECRET_KEY` in app.py
2. Update database credentials
3. Use production WSGI server (gunicorn)
4. Set debug=False

## License

This project is for educational purposes.

