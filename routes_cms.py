"""
CMS Routes for content management
"""
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json


def init_cms_routes(app, db, Gallery, SiteSetting, MenuItem, PrincipalMessage, QuickLink, HomeSection, Page, NewsTicker):
    """Initialize CMS routes"""
    
    from PIL import Image
    
    # Helper function to get setting value
    def get_setting(key, default=''):
        setting = SiteSetting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    # Helper function to set setting value
    def set_setting(key, value, setting_type='text'):
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SiteSetting(key=key, value=value, setting_type=setting_type)
            db.session.add(setting)
        db.session.commit()
    
    # ==================== SITE SETTINGS ====================
    
    @app.route('/admin/settings', methods=['GET', 'POST'])
    @login_required
    def admin_settings():
        """Site settings management"""
        if request.method == 'POST':
            try:
                from PIL import Image
                
                # Update general settings
                set_setting('college_name_bn', request.form.get('college_name_bn'))
                set_setting('college_name_en', request.form.get('college_name_en'))
                set_setting('contact_phone', request.form.get('contact_phone'))
                set_setting('contact_email', request.form.get('contact_email'))
                set_setting('contact_address', request.form.get('contact_address'))
                set_setting('facebook_url', request.form.get('facebook_url'))
                set_setting('youtube_url', request.form.get('youtube_url'))
                
                # Handle logo upload with WebP conversion
                if 'logo' in request.files:
                    logo = request.files['logo']
                    if logo and logo.filename:
                        # Generate WebP filename
                        base_filename = secure_filename(logo.filename)
                        name_without_ext = os.path.splitext(base_filename)[0]
                        filename = f"logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name_without_ext}.webp"
                        logo_path = os.path.join('settings', filename)
                        full_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_path)
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        
                        # Convert to WebP
                        try:
                            img = Image.open(logo)
                            # Convert RGBA to RGB if necessary
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            
                            # Save as WebP
                            img.save(full_path, 'WEBP', quality=85, optimize=True)
                            # Store path with forward slashes for URLs
                            set_setting('logo', logo_path.replace('\\', '/'), 'image')
                        except Exception as e:
                            flash(f'লোগো আপলোড করতে ত্রুটি: {str(e)}', 'error')
                            return redirect(url_for('admin_settings'))
                
                flash('সেটিংস সফলভাবে আপডেট হয়েছে!', 'success')
            except Exception as e:
                flash(f'সেটিংস আপডেট করতে ত্রুটি: {str(e)}', 'error')
                db.session.rollback()
            
            return redirect(url_for('admin_settings'))
        
        # Get current settings
        settings = {
            'college_name_bn': get_setting('college_name_bn', 'সরকারি আদমজীনগর মার্চেন্ট ওয়ার্কার্স কলেজ'),
            'college_name_en': get_setting('college_name_en', 'Govt. Adamjeenagar Merchant Workers\' College'),
            'contact_phone': get_setting('contact_phone'),
            'contact_email': get_setting('contact_email'),
            'contact_address': get_setting('contact_address'),
            'facebook_url': get_setting('facebook_url'),
            'youtube_url': get_setting('youtube_url'),
            'logo': get_setting('logo')
        }
        
        return render_template('admin/settings.html', settings=settings)
    
    # ==================== NAVIGATION MENU ====================
    
    @app.route('/admin/menu')
    @login_required
    def admin_menu():
        """Navigation menu management"""
        menu_items = MenuItem.query.filter_by(parent_id=None).order_by(MenuItem.order).all()
        return render_template('admin/menu.html', menu_items=menu_items)
    
    @app.route('/admin/menu/add', methods=['POST'])
    @login_required
    def admin_add_menu_item():
        """Add menu item"""
        try:
            menu_item = MenuItem(
                label=request.form.get('label'),
                url=request.form.get('url'),
                icon=request.form.get('icon'),
                order=int(request.form.get('order', 0)),
                is_active=request.form.get('is_active') == 'on'
            )
            db.session.add(menu_item)
            db.session.commit()
            flash('মেনু আইটেম যোগ করা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_menu'))
    
    @app.route('/admin/menu/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_delete_menu_item(id):
        """Delete menu item"""
        try:
            menu_item = MenuItem.query.get_or_404(id)
            db.session.delete(menu_item)
            db.session.commit()
            flash('মেনু আইটেম মুছে ফেলা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_menu'))
    
    # ==================== HOMEPAGE CONTENT ====================
    
    @app.route('/admin/homepage')
    @login_required
    def admin_homepage():
        """Homepage content management"""
        principal = PrincipalMessage.query.filter_by(is_active=True).first()
        quick_links = QuickLink.query.filter_by(is_active=True).order_by(QuickLink.order).all()
        sections = HomeSection.query.order_by(HomeSection.order).all()
        
        return render_template('admin/homepage.html', 
                             principal=principal,
                             quick_links=quick_links,
                             sections=sections)
    
    @app.route('/admin/homepage/principal', methods=['POST'])
    @login_required
    def admin_update_principal():
        """Update principal's message"""
        try:
            from PIL import Image
            
            principal = PrincipalMessage.query.filter_by(is_active=True).first()
            
            if not principal:
                principal = PrincipalMessage()
                db.session.add(principal)
            
            principal.name = request.form.get('name')
            principal.designation = request.form.get('designation')
            principal.message = request.form.get('message')
            
            # Handle photo upload with WebP conversion
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename:
                    # Generate WebP filename
                    base_filename = secure_filename(photo.filename)
                    name_without_ext = os.path.splitext(base_filename)[0]
                    filename = f"principal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name_without_ext}.webp"
                    photo_path = os.path.join('principal', filename)
                    full_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_path)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Convert to WebP
                    try:
                        img = Image.open(photo)
                        # Convert RGBA to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                        
                        # Save as WebP
                        img.save(full_path, 'WEBP', quality=85, optimize=True)
                        # Store path with forward slashes for URLs
                        principal.photo = photo_path.replace('\\', '/')
                    except Exception as e:
                        flash(f'ছবি আপলোড করতে ত্রুটি: {str(e)}', 'error')
                        return redirect(url_for('admin_homepage'))
            
            db.session.commit()
            flash('অধ্যক্ষের বার্তা আপডেট হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_homepage'))
    
    @app.route('/admin/homepage/quicklink/add', methods=['POST'])
    @login_required
    def admin_add_quick_link():
        """Add quick link"""
        try:
            quick_link = QuickLink(
                title=request.form.get('title'),
                url=request.form.get('url'),
                icon=request.form.get('icon'),
                color=request.form.get('color', '#7B1F1F'),
                order=int(request.form.get('order', 0))
            )
            db.session.add(quick_link)
            db.session.commit()
            flash('দ্রুত লিংক যোগ করা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_homepage'))
    
    @app.route('/admin/homepage/quicklink/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_delete_quick_link(id):
        """Delete quick link"""
        try:
            quick_link = QuickLink.query.get_or_404(id)
            db.session.delete(quick_link)
            db.session.commit()
            flash('দ্রুত লিংক মুছে ফেলা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_homepage'))
    
    @app.route('/admin/homepage/section/add', methods=['POST'])
    @login_required
    def admin_add_home_section():
        """Add homepage section"""
        try:
            section = HomeSection(
                section_key=request.form.get('section_key'),
                title=request.form.get('title'),
                content=request.form.get('content'),
                order=int(request.form.get('order', 0))
            )
            db.session.add(section)
            db.session.commit()
            flash('সেকশন যোগ করা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_homepage'))
    
    # ==================== PAGES ====================
    
    @app.route('/admin/pages')
    @login_required
    def admin_pages():
        """Page management"""
        pages = Page.query.order_by(Page.created_at.desc()).all()
        return render_template('admin/pages.html', pages=pages)
    
    @app.route('/admin/pages/add', methods=['POST'])
    @login_required
    def admin_add_page():
        """Add new page"""
        try:
            page = Page(
                slug=request.form.get('slug'),
                title=request.form.get('title'),
                content=request.form.get('content'),
                meta_description=request.form.get('meta_description'),
                is_published=request.form.get('is_published') == 'on'
            )
            db.session.add(page)
            db.session.commit()
            flash('পেজ তৈরি হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_pages'))
    
    @app.route('/admin/pages/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_delete_page(id):
        """Delete page"""
        try:
            page = Page.query.get_or_404(id)
            db.session.delete(page)
            db.session.commit()
            flash('পেজ মুছে ফেলা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_pages'))
    
    # ==================== NEWS TICKER ====================
    
    @app.route('/admin/newsticker')
    @login_required
    def admin_newsticker():
        """News ticker management"""
        news_items = NewsTicker.query.order_by(NewsTicker.order).all()
        return render_template('admin/newsticker.html', news_items=news_items)
    
    @app.route('/admin/newsticker/add', methods=['POST'])
    @login_required
    def admin_add_news():
        """Add news ticker item"""
        try:
            news = NewsTicker(
                text=request.form.get('text'),
                url=request.form.get('url'),
                order=int(request.form.get('order', 0))
            )
            db.session.add(news)
            db.session.commit()
            flash('নিউজ টিকার যোগ করা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_newsticker'))
    
    @app.route('/admin/newsticker/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_delete_news(id):
        """Delete news ticker item"""
        try:
            news = NewsTicker.query.get_or_404(id)
            db.session.delete(news)
            db.session.commit()
            flash('নিউজ টিকার মুছে ফেলা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_newsticker'))
    
    # ==================== GALLERY ====================
    
    @app.route('/admin/gallery')
    @login_required
    def admin_gallery():
        """Gallery management"""
        photos = Gallery.query.order_by(Gallery.order, Gallery.created_at.desc()).all()
        return render_template('admin/gallery.html', photos=photos)
    
    @app.route('/admin/gallery/add', methods=['POST'])
    @login_required
    def admin_add_gallery_photo():
        """Add gallery photo"""
        try:
            if 'photo' not in request.files:
                flash('ছবি নির্বাচন করুন', 'error')
                return redirect(url_for('admin_gallery'))
            
            photo = request.files['photo']
            if not photo or not photo.filename:
                flash('ছবি নির্বাচন করুন', 'error')
                return redirect(url_for('admin_gallery'))
            
            # Generate WebP filename
            base_filename = secure_filename(photo.filename)
            name_without_ext = os.path.splitext(base_filename)[0]
            filename = f"gallery_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name_without_ext}.webp"
            photo_path = os.path.join('gallery', filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Convert to WebP
            img = Image.open(photo)
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save as WebP
            img.save(full_path, 'WEBP', quality=85, optimize=True)
            
            # Create gallery entry
            gallery_photo = Gallery(
                title=request.form.get('title', 'Untitled'),
                description=request.form.get('description', ''),
                image_path=photo_path.replace('\\', '/'),
                order=int(request.form.get('order', 0))
            )
            db.session.add(gallery_photo)
            db.session.commit()
            
            flash('ছবি যোগ করা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_gallery'))
    
    @app.route('/admin/gallery/delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_delete_gallery_photo(id):
        """Delete gallery photo"""
        try:
            photo = Gallery.query.get_or_404(id)
            
            # Delete file
            if photo.image_path:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            db.session.delete(photo)
            db.session.commit()
            flash('ছবি মুছে ফেলা হয়েছে!', 'success')
        except Exception as e:
            flash(f'ত্রুটি: {str(e)}', 'error')
            db.session.rollback()
        
        return redirect(url_for('admin_gallery'))
    
    # ==================== PUBLIC GALLERY ====================
    
    @app.route('/gallery')
    def gallery():
        """Public gallery page"""
        photos = Gallery.query.filter_by(is_active=True).order_by(Gallery.order, Gallery.created_at.desc()).all()
        # Convert to dict for JSON serialization in template
        photos_dict = [photo.to_dict() for photo in photos]
        return render_template('gallery.html', photos=photos, photos_json=photos_dict)
    
    # ==================== PUBLIC PAGES ====================
    
    @app.route('/page/<slug>')
    def view_page(slug):
        """View dynamic page"""
        page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
        return render_template('page.html', page=page)
    
    # Context processor to make menu items and settings available in all templates
    @app.context_processor
    def inject_cms_data():
        menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order).all()
        news_items = NewsTicker.query.filter_by(is_active=True).order_by(NewsTicker.order).all()
        
        return dict(
            cms_menu_items=menu_items,
            cms_news_items=news_items,
            get_setting=get_setting
        )
