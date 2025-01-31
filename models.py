from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
import pytz
import datetime

db = SQLAlchemy()

class Teacher(UserMixin, db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    alloted_classes = db.relationship('Class', backref='teacher', lazy=True, cascade="all, delete-orphan")
    subjects = db.Column(db.JSON, nullable=False)
    def __repr__(self):
        return f'<Teacher {self.name}>'

class Class(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False) 
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    students = db.relationship('Student', backref='class', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Class {self.name}>'

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    roll_no = db.Column(db.Integer, nullable=False, unique=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")
 
    def __repr__(self):
        return f'<Student {self.name}>'

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True ,nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date())
    present = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.String(255), nullable=True)  # Optional note for attendance
    subject = db.Column(db.String(64), nullable=False)  # Add subject to distinguish between different subjects
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)  # Track who took attendance

    def __repr__(self):
        return f'<Attendance {self.id}>'
