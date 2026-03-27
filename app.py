import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import markdown2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ── Sensitive configuration loaded from .env ───────────────
db_url = os.getenv('DATABASE_URL', 'sqlite:///portfolio.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['ATTACHMENTS_FOLDER'] = os.getenv('ATTACHMENTS_FOLDER', 'static/attachments')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Warn loudly in production if using the fallback secret key
if app.config['SECRET_KEY'] == 'fallback-dev-key-change-me':
    import warnings
    warnings.warn(
        "WARNING: SECRET_KEY is not set in .env — using insecure fallback. "
        "Set a strong SECRET_KEY before deploying to production!",
        stacklevel=2
    )

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ATTACHMENTS_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- MODELS ---
class PersonalInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Developer Name")
    bio = db.Column(db.Text, default="Software Developer.")
    profile_image = db.Column(db.String(200), default="")
    email = db.Column(db.String(100), default="hello@example.com")
    social_links = db.Column(db.Text, default="{}") # JSON
    employment_status = db.Column(db.String(50), default="available")
    hiring_info = db.Column(db.Text, default="Open to new opportunities")
    admin_password = db.Column(db.String(200)) # Simple admin auth

    def get_social_links(self):
        try: return json.loads(self.social_links)
        except: return {}

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    images = db.Column(db.Text, default="[]") # JSON list of URLs
    background_image = db.Column(db.String(200))
    technologies_used = db.Column(db.Text, default="[]") # JSON list
    achievements = db.Column(db.Text, default="[]") # JSON list
    github_link = db.Column(db.String(200))
    live_demo_link = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    attachments = db.Column(db.Text, default='[]')  # JSON list of {name, path, size}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), unique=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, default="[]") # JSON list
    cover_image = db.Column(db.String(200))
    status = db.Column(db.String(20), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100))
    sender_email = db.Column(db.String(100))
    purpose = db.Column(db.String(100))
    content = db.Column(db.Text)
    status = db.Column(db.String(20), default="new")
    received_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- INIT DATABASE ---
with app.app_context():
    db.create_all()
    # Seed single personal info record with admin password from .env
    if not PersonalInformation.query.first():
        default_password = os.getenv('ADMIN_DEFAULT_PASSWORD', 'admin123')
        info = PersonalInformation(admin_password=generate_password_hash(default_password))
        db.session.add(info)
        db.session.commit()

# --- UTILS ---
def is_admin():
    return session.get('logged_in', False)

def get_personal_info():
    return PersonalInformation.query.first()

@app.context_processor
def inject_global():
    return dict(info=get_personal_info(), is_admin=is_admin())

@app.template_filter('markdown')
def md_to_html(text):
    if not text: return ""
    return markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "strike"])

@app.template_filter('from_json')
def from_json(text):
    try: return json.loads(text) if text else []
    except: return []

# --- PUBLIC ROUTES ---
@app.route('/')
def home():
    projects = Project.query.filter_by(is_featured=True).order_by(Project.sort_order).all()
    recent_articles = Article.query.filter_by(status='published').order_by(Article.created_at.desc()).limit(3).all()
    return render_template('home.html', projects=projects, articles=recent_articles)

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.sort_order).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', p=project)

@app.route('/projects/<int:id>/download/<path:filename>')
def project_download(id, filename):
    """Serve project attachment files securely."""
    Project.query.get_or_404(id)  # ensure project exists
    safe_name = secure_filename(filename)
    attachments_dir = os.path.join(app.root_path, app.config['ATTACHMENTS_FOLDER'])
    return send_from_directory(attachments_dir, safe_name, as_attachment=True)

@app.route('/blog')
def blog():
    tag = request.args.get('tag')
    q = request.args.get('q', '').lower()
    
    query = Article.query.filter_by(status='published').order_by(Article.created_at.desc())
    articles = query.all()
    
    if tag:
        articles = [a for a in articles if tag in json.loads(a.tags)]
    if q:
        articles = [a for a in articles if q in a.title.lower() or q in a.content.lower()]
        
    return render_template('blog.html', articles=articles, active_tag=tag, search_q=q)

@app.route('/blog/<path:slug>')
def blog_detail(slug):
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    return render_template('blog_detail.html', a=article)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = Message(
            sender_name=request.form.get('sender_name'),
            sender_email=request.form.get('sender_email'),
            purpose=request.form.get('purpose'),
            content=request.form.get('message')
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        exist = BlogSubscriber.query.filter_by(email=email).first()
        if not exist:
            db.session.add(BlogSubscriber(email=email))
            db.session.commit()
            flash('Subscribed successfully!', 'success')
        else:
            flash('You are already subscribed.', 'info')
    return redirect(request.referrer or url_for('home'))


# --- ADMIN ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_admin(): return redirect(url_for('admin_dash'))
    if request.method == 'POST':
        pwd = request.form.get('password')
        info = get_personal_info()
        if check_password_hash(info.admin_password, pwd):
            session['logged_in'] = True
            return redirect(url_for('admin_dash'))
        flash('Invalid password', 'error')
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.before_request
def restrict_admin():
    if request.path.startswith('/admin') and not is_admin():
        return redirect(url_for('login'))

@app.route('/admin')
def admin_dash():
    stats = {
        'articles': Article.query.count(),
        'projects': Project.query.count(),
        'unread': Message.query.filter_by(status='new').count(),
        'subs': BlogSubscriber.query.count()
    }
    msgs = Message.query.order_by(Message.received_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_msgs=msgs)

@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    info = get_personal_info()
    if request.method == 'POST':
        info.name = request.form.get('name')
        info.bio = request.form.get('bio')
        info.email = request.form.get('email')
        info.employment_status = request.form.get('employment_status')
        info.hiring_info = request.form.get('hiring_info')
        
        # Social links JSON
        social_links = {
            'github': request.form.get('github'),
            'linkedin': request.form.get('linkedin'),
            'facebook': request.form.get('facebook'),
            'youtube': request.form.get('youtube'),
        }
        info.social_links = json.dumps(social_links)
        
        # Handle file upload
        f = request.files.get('profile_image')
        if f and f.filename:
            fn = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            info.profile_image = f"/static/uploads/{fn}"
            
        # Password update
        pwd = request.form.get('new_password')
        if pwd: info.admin_password = generate_password_hash(pwd)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('admin_profile'))
    return render_template('admin/profile.html', info=info)

# Manage Projects
@app.route('/admin/projects', methods=['GET', 'POST'])
def admin_projects():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            db.session.delete(Project.query.get(request.form.get('id')))
            db.session.commit()
        elif action == 'reorder':
            orders = json.loads(request.form.get('orders', '{}'))
            for pid, idx in orders.items():
                p = Project.query.get(pid)
                if p: p.sort_order = int(idx)
            db.session.commit()
            return jsonify({'status': 'ok'})
            
    projects = Project.query.order_by(Project.sort_order).all()
    return render_template('admin/projects_list.html', projects=projects)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@app.route('/admin/projects/new', methods=['GET', 'POST'])
def admin_project_edit(id=None):
    p = Project.query.get(id) if id else Project()
    if request.method == 'POST':
        p.title = request.form.get('title')
        p.description = request.form.get('description')
        p.github_link = request.form.get('github_link')
        p.live_demo_link = request.form.get('live_demo_link')
        p.is_featured = request.form.get('is_featured') == 'on'
        
        techs = request.form.get('technologies_used')
        p.technologies_used = json.dumps([t.strip() for t in techs.split(',') if t.strip()])
        
        achievements = request.form.get('achievements')
        p.achievements = json.dumps([a.strip() for a in achievements.split('\n') if a.strip()])
        
        # Background image upload
        f = request.files.get('background_image')
        if f and f.filename:
            fn = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            p.background_image = f"/static/uploads/{fn}"

        # Multiple file attachments upload
        uploaded_files = request.files.getlist('attachments')
        existing_attachments = json.loads(p.attachments or '[]')
        for uploaded_file in uploaded_files:
            if uploaded_file and uploaded_file.filename:
                fn = secure_filename(uploaded_file.filename)
                save_path = os.path.join(app.root_path, app.config['ATTACHMENTS_FOLDER'], fn)
                uploaded_file.save(save_path)
                file_size = os.path.getsize(save_path)
                # Avoid duplicates
                if not any(a['path'] == fn for a in existing_attachments):
                    existing_attachments.append({
                        'name': uploaded_file.filename,
                        'path': fn,
                        'size': file_size
                    })
        p.attachments = json.dumps(existing_attachments)

        # Delete attachment if requested
        del_file = request.form.get('delete_attachment')
        if del_file:
            existing_attachments = [a for a in existing_attachments if a['path'] != del_file]
            p.attachments = json.dumps(existing_attachments)
            try:
                os.remove(os.path.join(app.root_path, app.config['ATTACHMENTS_FOLDER'], del_file))
            except Exception:
                pass

        if not id: db.session.add(p)
        db.session.commit()
        flash('Project saved', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin/project_form.html', p=p)

# Manage Blog
@app.route('/admin/blog', methods=['GET', 'POST'])
def admin_blog():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            db.session.delete(Article.query.get(request.form.get('id')))
            db.session.commit()
            flash('Article deleted', 'success')
            
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/blog_list.html', articles=articles)

@app.route('/admin/blog/edit/<int:id>', methods=['GET', 'POST'])
@app.route('/admin/blog/new', methods=['GET', 'POST'])
def admin_blog_edit(id=None):
    a = Article.query.get(id) if id else Article()
    if request.method == 'POST':
        a.title = request.form.get('title')
        
        # Generate slug if empty
        new_slug = request.form.get('slug')
        if not new_slug:
            new_slug = '-'.join(a.title.lower().split())[:50]
        a.slug = new_slug
        
        a.content = request.form.get('content')
        a.status = request.form.get('status')
        
        tags = request.form.get('tags')
        a.tags = json.dumps([t.strip() for t in tags.split(',') if t.strip()])
        
        f = request.files.get('cover_image')
        if f and f.filename:
            fn = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            a.cover_image = f"/static/uploads/{fn}"
            
        if not id: db.session.add(a)
        db.session.commit()
        
        if request.form.get('notify') == 'on' and a.status == 'published':
            # Simulated dummy email
            print(f"EMAILS SENT TO SUBSCRIBERS ABOUT POST: {a.title}")
            
        flash('Article saved', 'success')
        return redirect(url_for('admin_blog'))
    return render_template('admin/blog_form.html', a=a)

@app.route('/admin/messages')
def admin_messages():
    action = request.args.get('action')
    m_id = request.args.get('id')
    if action == 'read' and m_id:
        m = Message.query.get(m_id)
        if m: m.status = 'read'
        db.session.commit()
        return redirect(url_for('admin_messages'))
    
    msgs = Message.query.order_by(Message.received_at.desc()).all()
    return render_template('admin/messages.html', messages=msgs)

@app.route('/admin/subscribers', methods=['GET', 'POST'])
def admin_subscribers():
    if request.method == 'POST':
        db.session.delete(BlogSubscriber.query.get(request.form.get('id')))
        db.session.commit()
    subs = BlogSubscriber.query.order_by(BlogSubscriber.subscribed_at.desc()).all()
    return render_template('admin/subscribers.html', subs=subs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
