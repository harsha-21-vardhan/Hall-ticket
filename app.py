import os
import uuid
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['TESTING'] = True

# SQLite for local testing (no setup required)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hall_ticket.db')

# MySQL for production (uncomment and configure):
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/hall_ticket_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/qr_codes'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    register_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    hall_tickets = db.relationship(
        'HallTicket', backref='student', lazy=True,
        cascade='all, delete-orphan'
    )

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    exams = db.relationship(
        'Exam', backref='subject', lazy=True,
        cascade='all, delete-orphan'
    )

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=True)
    hall_no = db.Column(db.String(20), nullable=False)
    exam_name = db.Column(db.String(100), nullable=False)

class HallTicket(db.Model):
    __tablename__ = 'hall_tickets'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    qr_token = db.Column(db.String(100), unique=True, nullable=False)
    pdf_path = db.Column(db.String(200), nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    if 'admin_id' in session:
        return db.session.get(Admin, int(user_id))
    return db.session.get(Student, int(user_id))

def generate_qr_code(token):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    try:
        qr_url = url_for('download_hall_ticket', token=token, _external=True)
    except RuntimeError:
        qr_url = f"http://localhost:5000/download/{token}"
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"{token}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img.save(filepath)
    return filename

def generate_pdf(student, hall_ticket, qr_filename):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.rect(20, 20, width - 40, height - 40)
    c.setLineWidth(1)
    c.rect(30, 30, width - 60, height - 60)
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 80, "HALL TICKET")
    
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 120, "Smart Examination System")
    
    c.setLineWidth(1)
    c.line(50, height - 140, width - 50, height - 140)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 180, "Student Name:")
    c.setFont("Helvetica", 12)
    c.drawString(180, height - 180, student.name)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 210, "Register Number:")
    c.setFont("Helvetica", 12)
    c.drawString(180, height - 210, student.register_number)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 240, "Department:")
    c.setFont("Helvetica", 12)
    c.drawString(180, height - 240, student.department)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 270, "Email:")
    c.setFont("Helvetica", 12)
    c.drawString(180, height - 270, student.email)
    
    c.line(50, height - 290, width - 50, height - 290)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 320, "EXAM SCHEDULE")
    
    y = height - 360
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Subject")
    c.drawString(200, y, "Exam Name")
    c.drawString(350, y, "Date")
    c.drawString(430, y, "Time")
    c.drawString(510, y, "Hall No.")
    
    c.line(50, y - 10, width - 50, y - 10)
    
    exams = Exam.query.all()
    c.setFont("Helvetica", 10)
    for exam in exams:
        y -= 25
        c.drawString(50, y, exam.subject.subject_name)
        c.drawString(200, y, exam.exam_name)
        c.drawString(350, y, str(exam.date))
        time_str = exam.time
        if exam.end_time:
            time_str += " - " + exam.end_time
        c.drawString(430, y, time_str)
        c.drawString(510, y, exam.hall_no)
    
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    if os.path.exists(qr_path):
        c.drawImage(qr_path, width - 180, 50, 130, 130)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 50, f"Token: {hall_ticket.qr_token}")
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Scan QR code to download hall ticket")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 80, "Authorized Signature")
    c.line(50, 70, 200, 70)
    
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        student = Student.query.filter_by(email=email).first()
        
        if not student:
            flash('Email not found. Please register first.', 'danger')
            return render_template('login.html')
        
        if not bcrypt.check_password_hash(student.password, password):
            flash('Invalid password. Please try again.', 'danger')
            return render_template('login.html')
        
        session['student_id'] = student.id
        session['user_id'] = student.id
        
        return redirect(url_for('student_dashboard'))
        
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        register_number = request.form.get('register_number')
        new_password = request.form.get('new_password')
        
        student = Student.query.filter_by(email=email, register_number=register_number).first()
        
        if not student:
            flash('Email or register number not found', 'danger')
            return render_template('login.html')
        
        hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
        student.password = hashed
        db.session.commit()
        
        flash('Password reset successful! Please login with new password.', 'success')
        return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['is_admin'] = True
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/forgot-password', methods=['POST'])
def admin_forgot_password():
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin:
        flash('Admin username not found', 'danger')
        return redirect(url_for('admin_login'))
    
    hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
    admin.password = hashed
    db.session.commit()
    
    flash('Password reset successful! Please login with new password.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        register_number = request.form.get('register_number')
        password = request.form.get('password')
        department = request.form.get('department')
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        if Student.query.filter_by(register_number=register_number).first():
            flash('Register number already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_student = Student(name=name, email=email, register_number=register_number, 
                          password=hashed_password, department=department)
        db.session.add(new_student)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login') + '?next=/student/dashboard')
    
    student_id = session.get('student_id')
    student = db.session.get(Student, student_id)
    if not student:
        return redirect(url_for('login'))
    
    hall_ticket = HallTicket.query.filter_by(student_id=student_id).first()
    exams = Exam.query.all()
    return render_template('student/dashboard.html', hall_ticket=hall_ticket, exams=exams, current_user=student)

@app.route('/student/qr-code')
def student_qr_code():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    hall_ticket = HallTicket.query.filter_by(student_id=session['student_id']).first()
    if hall_ticket:
        qr_file = f"{hall_ticket.qr_token}.png"
    else:
        qr_file = None
    return render_template('student/qr_code.html', qr_file=qr_file, token=hall_ticket.qr_token if hall_ticket else None)

@app.route('/student/download-pdf')
def student_download_pdf():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    hall_ticket = HallTicket.query.filter_by(student_id=session['student_id']).first()
    if hall_ticket:
        return redirect(url_for('download_hall_ticket', token=hall_ticket.qr_token))
    flash('Hall ticket not generated', 'warning')
    return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    total_exams = Exam.query.count()
    total_hall_tickets = HallTicket.query.count()
    
    students = Student.query.all()
    subjects = Subject.query.all()
    exams = Exam.query.all()
    
    return render_template('admin/dashboard.html', 
                       total_students=total_students,
                       total_subjects=total_subjects,
                       total_exams=total_exams,
                       total_hall_tickets=total_hall_tickets,
                       students=students, subjects=subjects, exams=exams)

@app.route('/admin/add-student', methods=['POST'])
@login_required
def add_student():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    name = request.form.get('name')
    email = request.form.get('email')
    register_number = request.form.get('register_number')
    password = request.form.get('password')
    department = request.form.get('department')
    
    if Student.query.filter_by(email=email).first():
        flash('Email already exists', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_student = Student(name=name, email=email, register_number=register_number,
                      password=hashed_password, department=department)
    db.session.add(new_student)
    db.session.commit()
    
    flash('Student added successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit-student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.register_number = request.form.get('register_number')
        student.department = request.form.get('department')
        if request.form.get('password'):
            student.password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
        db.session.commit()
        flash('Student updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_student.html', student=student)

@app.route('/admin/delete-student/<int:id>')
@login_required
def delete_student(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Unable to delete student. Remove their hall ticket first or try again.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-subject', methods=['POST'])
@login_required
def add_subject():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    subject_name = request.form.get('subject_name')
    subject_code = request.form.get('subject_code')
    
    if Subject.query.filter_by(subject_code=subject_code).first():
        flash('Subject code already exists', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_subject = Subject(subject_name=subject_name, subject_code=subject_code)
    db.session.add(new_subject)
    db.session.commit()
    
    flash('Subject added successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit-subject/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(id)
    if request.method == 'POST':
        subject.subject_name = request.form.get('subject_name')
        subject.subject_code = request.form.get('subject_code')
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_subject.html', subject=subject)

@app.route('/admin/delete-subject/<int:id>')
@login_required
def delete_subject(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    subject = Subject.query.get_or_404(id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully', 'success')
    except Exception:
        db.session.rollback()
        flash('Unable to delete subject. Remove related exams first or try again.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-exam', methods=['POST'])
@login_required
def add_exam():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    subject_id = request.form.get('subject_id')
    exam_name = request.form.get('exam_name')
    date_str = request.form.get('date')
    time = request.form.get('time')
    end_time = request.form.get('end_time')
    hall_no = request.form.get('hall_no')
    
    from datetime import datetime
    exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    new_exam = Exam(subject_id=subject_id, exam_name=exam_name, date=exam_date, time=time, end_time=end_time, hall_no=hall_no)
    db.session.add(new_exam)
    db.session.commit()
    
    flash('Exam added successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit-exam/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_exam(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    exam = Exam.query.get_or_404(id)
    subjects = Subject.query.all()
    if request.method == 'POST':
        from datetime import datetime
        exam.subject_id = request.form.get('subject_id')
        exam.exam_name = request.form.get('exam_name')
        exam.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        exam.time = request.form.get('time')
        exam.end_time = request.form.get('end_time')
        exam.hall_no = request.form.get('hall_no')
        db.session.commit()
        flash('Exam updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_exam.html', exam=exam, subjects=subjects)

@app.route('/admin/delete-exam/<int:id>')
@login_required
def delete_exam(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    exam = Exam.query.get_or_404(id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/generate-ticket/<int:student_id>')
@login_required
def generate_ticket(student_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    student = Student.query.get_or_404(student_id)
    existing_ticket = HallTicket.query.filter_by(student_id=student_id).first()
    
    if existing_ticket:
        flash('Hall ticket already exists for this student', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    token = str(uuid.uuid4())
    qr_filename = generate_qr_code(token)
    
    new_ticket = HallTicket(student_id=student_id, qr_token=token)
    db.session.add(new_ticket)
    db.session.commit()
    
    flash('Hall ticket generated successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/generate-all-tickets')
@login_required
def generate_all_tickets():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    students = Student.query.all()
    count = 0
    for student in students:
        existing_ticket = HallTicket.query.filter_by(student_id=student.id).first()
        if not existing_ticket:
            token = str(uuid.uuid4())
            qr_filename = generate_qr_code(token)
            new_ticket = HallTicket(student_id=student.id, qr_token=token)
            db.session.add(new_ticket)
            count += 1
    
    db.session.commit()
    flash(f'{count} hall tickets generated successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view-tickets')
@login_required
def view_tickets():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    tickets = HallTicket.query.all()
    return render_template('admin/view_tickets.html', tickets=tickets)

@app.route('/download/<token>')
def download_hall_ticket(token):
    hall_ticket = HallTicket.query.filter_by(qr_token=token).first()
    if not hall_ticket:
        flash('Invalid token', 'danger')
        return redirect(url_for('home'))
    
    student = hall_ticket.student
    qr_filename = f"{token}.png"
    pdf_buffer = generate_pdf(student, hall_ticket, qr_filename)
    
    return send_file(pdf_buffer, as_attachment=True, download_name=f"hall_ticket_{student.register_number}.pdf", 
                   mimetype='application/pdf')

@app.route('/verify/<token>')
def verify_token(token):
    hall_ticket = HallTicket.query.filter_by(qr_token=token).first()
    if hall_ticket:
        hall_ticket.is_used = True
        db.session.commit()
        student = hall_ticket.student
        exams = Exam.query.all()
        return render_template('verify.html', valid=True, student=student, exams=exams)
    return render_template('verify.html', valid=False, student=None)

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    print("Chatbot called")
    print("Session:", dict(session))
    print("is_admin:", session.get('is_admin'))
    print("current_user:", current_user)
    
    if not session.get('is_admin'):
        print("Not admin, returning unauthorized")
        return jsonify({'response': 'Unauthorized'})
    
    message = request.json.get('message', '').lower()
    print("Message received:", message)
    response = process_chatbot_command(message)
    print("Response:", response)
    return jsonify({'response': response})

def process_chatbot_command(message):
    if 'add student' in message:
        msg = message.replace('add student', '').strip()
        if not msg:
            return "Please provide: name email regNo department\nExample: add student Rahul Sharma rahul@test.com REG001 CSE"
        
        email = None
        for p in msg.split():
            if '@' in p:
                email = p
                break
        
        if not email:
            return "Email not found. Use format: add student [name] [email] [regNo] [dept]\nExample: add student Rahul rahul@test.com REG001 CSE"
        
        parts = msg.split()
        email_index = parts.index(email)
        
        name = ' '.join(parts[:email_index])
        remaining = parts[email_index + 1:]
        
        if len(remaining) < 2:
            return "Missing register number or department. Use: add student [name] [email] [regNo] [dept]"
        
        regNo = remaining[0]
        dept = remaining[1]
        
        if not name:
            return "Name is required"
        
        if Student.query.filter_by(email=email).first():
            return "Email already exists"
        if Student.query.filter_by(register_number=regNo.upper()).first():
            return "Register number already exists"
        
        password = "pass" + regNo.replace("REG", "").replace("reg", "")
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        new_student = Student(name=name.title(), email=email, register_number=regNo.upper(), 
                         password=hashed, department=dept.upper())
        db.session.add(new_student)
        db.session.commit()
        return f"Student {name.title()} added successfully!\nLogin: {email}\nPassword: {password}"
    
    if 'create subject' in message:
        parts = message.replace('create subject', '').strip().split()
        if len(parts) >= 1:
            subj_name = ' '.join(parts)
            subj_code = f"SUB{Subject.query.count() + 1:03d}"
            new_subject = Subject(subject_name=subj_name.title(), subject_code=subj_code)
            db.session.add(new_subject)
            db.session.commit()
            return f"Subject {subj_name.title()} created successfully"
        return "Please provide subject name. Example: 'create subject DBMS'"
    
    if 'show all students' in message or 'list students' in message:
        students = Student.query.all()
        if not students:
            return "No students found in the database."
        result = "Total Students:\n"
        for s in students[:10]:
            result += f"- {s.name} ({s.register_number})\n"
        if len(students) > 10:
            result += f"... and {len(students) - 10} more"
        return result
    
    if 'show all subjects' in message or 'list subjects' in message:
        subjects = Subject.query.all()
        if not subjects:
            return "No subjects found."
        result = "Total Subjects:\n"
        for s in subjects:
            result += f"- {s.subject_name} ({s.subject_code})\n"
        return result
    
    if 'generate ticket' in message or 'generate all tickets' in message:
        students = Student.query.all()
        count = 0
        for student in students:
            if not HallTicket.query.filter_by(student_id=student.id).first():
                token = str(uuid.uuid4())
                generate_qr_code(token)
                new_ticket = HallTicket(student_id=student.id, qr_token=token)
                db.session.add(new_ticket)
                count += 1
        db.session.commit()
        return f"{count} hall tickets generated successfully"
    
    if 'total students' in message or 'count students' in message:
        count = Student.query.count()
        return f"Total students: {count}"
    
    if 'total subjects' in message or 'count subjects' in message:
        count = Subject.query.count()
        return f"Total subjects: {count}"
    
    if 'total exams' in message or 'count exams' in message:
        count = Exam.query.count()
        return f"Total exams: {count}"
    
    if 'delete student' in message:
        parts = message.replace('delete student', '').strip()
        if parts:
            student = Student.query.filter_by(register_number=parts.upper()).first()
            if not student:
                student = Student.query.filter(Student.name.ilike(f"%{parts}%")).first()
            if student:
                db.session.delete(student)
                db.session.commit()
                return f"Student {student.name} deleted successfully"
            return "Student not found"
        return "Please provide register number. Example: 'delete student REG0001'"
    
    if 'delete subject' in message:
        parts = message.replace('delete subject', '').strip()
        if parts:
            subject = Subject.query.filter_by(subject_code=parts.upper()).first()
            if not subject:
                subject = Subject.query.filter(Subject.subject_name.ilike(f"%{parts}%")).first()
            if not subject:
                all_subjects = Subject.query.all()
                for s in all_subjects:
                    if parts.upper() in s.subject_code.upper() or parts.lower() in s.subject_name.lower():
                        subject = s
                        break
            if subject:
                db.session.delete(subject)
                db.session.commit()
                return f"Subject {subject.subject_name} ({subject.subject_code}) deleted successfully"
            return "Subject not found. Use subject name or code (e.g., 'DBMS' or 'SUB001')"
        return "Please provide subject name or code. Example: 'delete subject DBMS' or 'delete subject SUB001'"
    
    if 'delete exam' in message:
        msg = message.replace('delete exam', '').strip()
        if not msg:
            return "Please provide exam name. Example: 'delete exam DBMS Mid' or 'delete exam DBMS'"
        
        exams = Exam.query.all()
        exam = None
        for e in exams:
            exam_name_match = msg.lower() in e.exam_name.lower() if e.exam_name else False
            subject_match = False
            if e.subject:
                subject_match = msg.lower() in e.subject.subject_name.lower()
            if exam_name_match or subject_match:
                exam = e
                break
        
        if exam:
            subject_name = exam.subject.subject_name if exam.subject else "Unknown"
            db.session.delete(exam)
            db.session.commit()
            return f"Exam '{exam.exam_name}' ({subject_name}) deleted successfully"
        return "Exam not found. Use exam name or subject name. Example: 'delete exam DBMS Mid' or 'delete exam DBMS'"
    
    if 'reset password' in message:
        parts = message.replace('reset password', '').strip().split()
        if len(parts) >= 2:
            email = parts[0]
            new_password = parts[1]
            student = Student.query.filter_by(email=email).first()
            if not student:
                return "Student not found with this email"
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            student.password = hashed
            db.session.commit()
            return f"Password reset successfully for {student.name}\nEmail: {email}\nNew Password: {new_password}"
        return "Please provide email and new password\nExample: reset password student@email.com newpass123"
    
    if 'help' in message:
        return """Available commands:
- 'add student [name] [email] [regNo] [dept]' - Add new student (e.g., add student Rahul rahul@test.com REG001 CSE)
- 'create subject [name]' - Create new subject (e.g., create subject DBMS)
- 'delete student [name/register]' - Delete student by name or register number
- 'delete subject [name/code]' - Delete subject by name or code (e.g., delete subject DBMS or SUB001)
- 'delete exam [name]' - Delete exam by name (e.g., delete exam DBMS Mid)
- 'show all students' - List all students
- 'show all subjects' - List all subjects
- 'generate all tickets' - Generate tickets for all students
- 'total students' - Count students
- 'total subjects' - Count subjects
- 'total exams' - Count exams"""
    
    return "I didn't understand that. Type 'help' for available commands."

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('home'))

def init_db():
    with app.app_context():
        db.create_all()
        
        if not Admin.query.filter_by(username='admin').first():
            hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = Admin(username='admin', password=hashed)
            db.session.add(admin)
            db.session.commit()
            print("Admin account created: admin / admin123")

# Call init_db() at import time so tables exist when the app is imported by WSGI servers
try:
    init_db()
except Exception:
    # If DB cannot be initialized at import time (permissions, env), skip silently
    pass

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)