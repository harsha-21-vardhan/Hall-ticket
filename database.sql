-- Smart Hall Ticket Management System Database Schema
-- MySQL Database

-- Create database
CREATE DATABASE IF NOT EXISTS hall_ticket_db;
USE hall_ticket_db;

-- Admin table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    register_number VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    department VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) UNIQUE NOT NULL
);

-- Exams table
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    exam_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    time VARCHAR(20) NOT NULL,
    hall_no VARCHAR(20) NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Hall Tickets table
CREATE TABLE IF NOT EXISTS hall_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    qr_token VARCHAR(100) UNIQUE NOT NULL,
    pdf_path VARCHAR(200),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_student_email ON students(email);
CREATE INDEX idx_student_reg ON students(register_number);
CREATE INDEX idx_hall_ticket_token ON hall_tickets(qr_token);
CREATE INDEX idx_hall_ticket_student ON hall_tickets(student_id);

-- Insert default admin (password: admin123 - bcrypt hash)
INSERT INTO admins (username, password) VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq');

-- Sample data for testing

-- Sample subjects
INSERT INTO subjects (subject_name, subject_code) VALUES 
('Database Management Systems', 'CS301'),
('Data Structures', 'CS302'),
('Operating Systems', 'CS303'),
('Computer Networks', 'CS304'),
('Software Engineering', 'CS305');

-- Sample students (password for all: password123)
INSERT INTO students (name, email, register_number, password, department) VALUES 
('Rahul Sharma', 'rahul@college.com', 'CS2021001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq', 'CSE'),
('Priya Patel', 'priya@college.com', 'CS2021002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq', 'CSE'),
('Ajay Kumar', 'ajay@college.com', 'CS2021003', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq', 'CSE'),
('Sneha Reddy', 'sneha@college.com', 'CS2021004', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq', 'CSE'),
('Arjun Singh', 'arjun@college.com', 'CS2021005', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LhY3I0d3GxR1WYymq', 'CSE');

-- Sample exams
INSERT INTO exams (subject_id, exam_name, date, time, hall_no) VALUES 
(1, 'DBMS Mid Exam', '2026-04-10', '09:00 AM', 'Hall-A101'),
(2, 'DS Internal Test', '2026-04-11', '09:00 AM', 'Hall-A102'),
(3, 'OS Quiz', '2026-04-12', '02:00 PM', 'Hall-A103'),
(4, 'CN Practical', '2026-04-13', '09:00 AM', 'Lab-L201'),
(5, 'SE Project Review', '2026-04-14', '02:00 PM', 'Hall-A104');

-- Note: In production, use proper bcrypt hashes for passwords
-- Default password for sample students is: password123