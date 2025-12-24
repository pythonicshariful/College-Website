import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import (
    db, Notice, Result, Admin, StudentResult,
    SiteSetting, MenuItem, PrincipalMessage, QuickLink, HomeSection, Page, NewsTicker
)
from PIL import Image

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Initialize CMS routes
from routes_cms import init_cms_routes
init_cms_routes(app, db, SiteSetting, MenuItem, PrincipalMessage, QuickLink, HomeSection, Page, NewsTicker)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_webp(image_file, output_path):
    """Convert uploaded image to WebP format"""
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Save as WebP
        img.save(output_path, 'WEBP', quality=85, optimize=True)
        return True
    except Exception as e:
        print(f"Error converting image to WebP: {str(e)}")
        return False

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Initialize CMS routes
from routes_cms import init_cms_routes
init_cms_routes(app, db, SiteSetting, MenuItem, PrincipalMessage, QuickLink, HomeSection, Page, NewsTicker)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Public Routes
@app.route('/')
def index():
    """Homepage"""
    notices = Notice.query.order_by(Notice.date.desc()).limit(5).all()
    
    # Get CMS data for homepage
    principal = PrincipalMessage.query.filter_by(is_active=True).first()
    quick_links = QuickLink.query.filter_by(is_active=True).order_by(QuickLink.order).all()
    
    return render_template('index.html', 
                         notices=notices,
                         principal=principal,
                         quick_links=quick_links)

@app.route('/notices')
def notices():
    """All notices page"""
    all_notices = Notice.query.order_by(Notice.date.desc()).all()
    return render_template('notices.html', notices=all_notices)

@app.route('/results')
def results():
    """Results page with filters"""
    # Get unique values for filters
    classes = db.session.query(Result.class_name).distinct().all()
    sessions = db.session.query(Result.session).distinct().all()
    sections = db.session.query(Result.section).distinct().all()
    
    all_results = Result.query.order_by(Result.date.desc()).all()
    return render_template('results.html', 
                         results=all_results,
                         classes=[c[0] for c in classes],
                         sessions=[s[0] for s in sessions],
                         sections=[sec[0] for sec in sections])

@app.route('/results/lookup', methods=['GET', 'POST'])
def result_lookup():
    """Student result lookup page"""
    # Get unique values for dropdowns
    classes = db.session.query(Result.class_name).distinct().all()
    sessions = db.session.query(Result.session).distinct().all()
    sections = db.session.query(Result.section).distinct().all()
    
    student_result = None
    result_info = None
    
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        session = request.form.get('session')
        section = request.form.get('section')
        roll_number = request.form.get('roll_number')
        
        # Find the result
        result = Result.query.filter_by(
            class_name=class_name,
            session=session,
            section=section
        ).first()
        
        if result:
            # Find student result
            student_result = StudentResult.query.filter_by(
                result_id=result.id,
                roll_number=roll_number
            ).first()
            
            if student_result:
                result_info = result
            else:
                flash('রোল নম্বর পাওয়া যায়নি', 'error')
        else:
            flash('এই শ্রেণি, সেশন এবং বিভাগের জন্য কোনো ফলাফল পাওয়া যায়নি', 'error')
    
    return render_template('result_lookup.html',
                         classes=[c[0] for c in classes],
                         sessions=[s[0] for s in sessions],
                         sections=[sec[0] for sec in sections],
                         student_result=student_result,
                         result_info=result_info)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    # Normalize path separators (replace backslashes with forward slashes)
    filename = filename.replace('\\', '/')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    total_notices = Notice.query.count()
    total_results = Result.query.count()
    recent_notices = Notice.query.order_by(Notice.created_at.desc()).limit(5).all()
    recent_results = Result.query.order_by(Result.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_notices=total_notices,
                         total_results=total_results,
                         recent_notices=recent_notices,
                         recent_results=recent_results)

@app.route('/admin/notices')
@login_required
def admin_notices():
    """Admin notices management"""
    all_notices = Notice.query.order_by(Notice.date.desc()).all()
    return render_template('admin/notices.html', notices=all_notices)

@app.route('/admin/notices/add', methods=['POST'])
@login_required
def admin_add_notice():
    """Add new notice"""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        # Handle file uploads
        file_path = None
        image_path = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join('notices', filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_path))
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                imagename = secure_filename(image.filename)
                imagename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{imagename}"
                image_path = os.path.join('notices', imagename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))
        
        # Create notice
        notice = Notice(
            title=title,
            description=description,
            file_path=file_path,
            image_path=image_path,
            date=datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        )
        
        db.session.add(notice)
        db.session.commit()
        
        flash('Notice added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding notice: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_notices'))

@app.route('/admin/notices/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_delete_notice(id):
    """Delete notice"""
    try:
        notice = Notice.query.get_or_404(id)
        
        # Delete files if they exist
        if notice.file_path:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], notice.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if notice.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], notice.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(notice)
        db.session.commit()
        
        flash('Notice deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting notice: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_notices'))

@app.route('/admin/results')
@login_required
def admin_results():
    """Admin results management"""
    all_results = Result.query.order_by(Result.date.desc()).all()
    return render_template('admin/results.html', results=all_results)

@app.route('/admin/results/add', methods=['POST'])
@login_required
def admin_add_result():
    """Add new result with Excel upload"""
    try:
        title = request.form.get('title')
        class_name = request.form.get('class_name')
        session = request.form.get('session')
        section = request.form.get('section')
        exam_type = request.form.get('exam_type')
        date_str = request.form.get('date')
        
        # Validate required fields
        if not all([title, class_name, session, section]):
            flash('শিরোনাম, শ্রেণি, সেশন এবং বিভাগ আবশ্যক!', 'error')
            return redirect(url_for('admin_results'))
        
        # Handle Excel file upload
        file_path = None
        if 'file' not in request.files:
            flash('এক্সেল ফাইল আবশ্যক!', 'error')
            return redirect(url_for('admin_results'))
        
        file = request.files['file']
        if not file or file.filename == '':
            flash('এক্সেল ফাইল আবশ্যক!', 'error')
            return redirect(url_for('admin_results'))
        
        # Check file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            flash('শুধুমাত্র Excel ফাইল (.xlsx, .xls) অনুমোদিত!', 'error')
            return redirect(url_for('admin_results'))
        
        # Save Excel file
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file_path = os.path.join('results', filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        file.save(full_path)
        
        # Create result record
        result = Result(
            title=title,
            class_name=class_name,
            session=session,
            section=section,
            exam_type=exam_type,
            file_path=file_path,
            date=datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        )
        
        db.session.add(result)
        db.session.flush()  # Get the result ID
        
        # Parse Excel file
        try:
            df = pd.read_excel(full_path)
            
            # Expected columns: Roll Number, Name, Subject columns, Total, Percentage, Grade
            required_cols = ['Roll Number', 'Name']
            
            # Check if required columns exist
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Excel ফাইলে '{', '.join(required_cols)}' কলাম থাকতে হবে")
            
            # Get subject columns (all columns except Roll Number, Name, Total, Percentage, Grade)
            exclude_cols = ['Roll Number', 'Name', 'Total', 'Percentage', 'Grade']
            subject_cols = [col for col in df.columns if col not in exclude_cols]
            
            # Process each student
            students_added = 0
            for index, row in df.iterrows():
                try:
                    roll_number = str(row['Roll Number']).strip()
                    student_name = str(row['Name']).strip()
                    
                    # Skip empty rows
                    if pd.isna(roll_number) or roll_number == '' or roll_number == 'nan':
                        continue
                    
                    # Get subject results
                    subject_results = {}
                    for subject in subject_cols:
                        if subject in row and not pd.isna(row[subject]):
                            subject_results[subject] = float(row[subject])
                    
                    # Get total, percentage, grade
                    total_marks = float(row['Total']) if 'Total' in row and not pd.isna(row['Total']) else None
                    percentage = float(row['Percentage']) if 'Percentage' in row and not pd.isna(row['Percentage']) else None
                    grade = str(row['Grade']).strip() if 'Grade' in row and not pd.isna(row['Grade']) else None
                    
                    # Create student result
                    student_result = StudentResult(
                        result_id=result.id,
                        roll_number=roll_number,
                        student_name=student_name,
                        subject_results=subject_results,
                        total_marks=total_marks,
                        percentage=percentage,
                        grade=grade
                    )
                    
                    db.session.add(student_result)
                    students_added += 1
                    
                except Exception as e:
                    print(f"Error processing row {index}: {str(e)}")
                    continue
            
            db.session.commit()
            flash(f'ফলাফল সফলভাবে যোগ করা হয়েছে! {students_added} জন শিক্ষার্থীর ফলাফল আপলোড হয়েছে।', 'success')
            
        except Exception as e:
            db.session.rollback()
            # Delete uploaded file if parsing failed
            if os.path.exists(full_path):
                os.remove(full_path)
            flash(f'Excel ফাইল প্রসেস করতে ত্রুটি: {str(e)}', 'error')
            return redirect(url_for('admin_results'))
        
    except Exception as e:
        flash(f'ফলাফল যোগ করতে ত্রুটি: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_results'))

@app.route('/admin/results/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_delete_result(id):
    """Delete result and associated student results"""
    try:
        result = Result.query.get_or_404(id)
        
        # Delete Excel file if it exists
        if result.file_path:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], result.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete result (student results will be deleted automatically due to cascade)
        db.session.delete(result)
        db.session.commit()
        
        flash('ফলাফল সফলভাবে মুছে ফেলা হয়েছে!', 'success')
    except Exception as e:
        flash(f'ফলাফল মুছতে ত্রুটি: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_results'))

def init_db():
    """Initialize database and create default admin"""
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(username=app.config['ADMIN_USERNAME']).first():
            admin = Admin(username=app.config['ADMIN_USERNAME'])
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"Default admin created: {app.config['ADMIN_USERNAME']}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)
