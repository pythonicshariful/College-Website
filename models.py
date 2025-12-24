from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Notice(db.Model):
    """Notice model for storing college notices"""
    __tablename__ = 'notices'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(300))
    image_path = db.Column(db.String(300))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notice {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'image_path': self.image_path,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Result(db.Model):
    """Result model for storing exam results"""
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)  # Inter First Year / Inter Second Year
    session = db.Column(db.String(20), nullable=False)  # e.g., 2019-2020
    section = db.Column(db.String(50), nullable=False)  # Science / Business Studies / Arts
    exam_type = db.Column(db.String(100))  # Annual, Half-Yearly, etc.
    file_path = db.Column(db.String(300), nullable=False)  # Excel file path
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to student results
    student_results = db.relationship('StudentResult', backref='result', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Result {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'class_name': self.class_name,
            'session': self.session,
            'section': self.section,
            'exam_type': self.exam_type,
            'file_path': self.file_path,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class StudentResult(db.Model):
    """StudentResult model for storing individual student results"""
    __tablename__ = 'student_results'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    subject_results = db.Column(db.JSON)  # Dictionary of subject: marks
    total_marks = db.Column(db.Float)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudentResult {self.roll_number} - {self.student_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'result_id': self.result_id,
            'roll_number': self.roll_number,
            'student_name': self.student_name,
            'subject_results': self.subject_results,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'grade': self.grade,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Admin(UserMixin, db.Model):
    """Admin model for authentication"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


# Import CMS models
from models_cms import (
    SiteSetting, MenuItem, PrincipalMessage, 
    QuickLink, HomeSection, Page, NewsTicker
)
