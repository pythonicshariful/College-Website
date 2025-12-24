"""
CMS Models for dynamic content management
"""
from datetime import datetime
from models import db


class SiteSetting(db.Model):
    """Site settings model for global configuration"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='text')  # text, image, json
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSetting {self.key}>'


class MenuItem(db.Model):
    """Navigation menu items"""
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for submenus
    children = db.relationship('MenuItem', backref=db.backref('parent', remote_side=[id]))
    
    def __repr__(self):
        return f'<MenuItem {self.label}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'url': self.url,
            'icon': self.icon,
            'order': self.order,
            'parent_id': self.parent_id,
            'is_active': self.is_active
        }


class PrincipalMessage(db.Model):
    """Principal's message on homepage"""
    __tablename__ = 'principal_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    designation = db.Column(db.String(200))
    photo = db.Column(db.String(300))  # Path to photo
    message = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrincipalMessage {self.name}>'


class QuickLink(db.Model):
    """Quick access links on homepage"""
    __tablename__ = 'quick_links'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    color = db.Column(db.String(20), default='#7B1F1F')  # Background color
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuickLink {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'icon': self.icon,
            'color': self.color,
            'order': self.order,
            'is_active': self.is_active
        }


class HomeSection(db.Model):
    """Dynamic homepage sections"""
    __tablename__ = 'home_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    section_key = db.Column(db.String(50), unique=True, nullable=False)  # about, hotline, subarnajaynti, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    images = db.Column(db.JSON)  # Array of image paths
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HomeSection {self.section_key}>'


class Page(db.Model):
    """Dynamic pages (About, Departments, etc.)"""
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    meta_description = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Page {self.slug}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'content': self.content,
            'meta_description': self.meta_description,
            'is_published': self.is_published,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class NewsTicker(db.Model):
    """News ticker items"""
    __tablename__ = 'news_ticker'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(200))  # Optional link
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewsTicker {self.text[:30]}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'url': self.url,
            'order': self.order,
            'is_active': self.is_active
        }
