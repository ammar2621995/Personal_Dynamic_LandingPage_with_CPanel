# 🚀 BA Portfolio — Full-Stack Developer Portfolio & CMS

A professional **Flask-based personal portfolio and content management system** built for developers who want full control over their digital identity. Features a stunning dark-mode UI, a private admin dashboard, Markdown-powered blog, project showcase with file attachments, and a contact system.

---

## ✨ Features

### 🌐 Public Site
| Feature | Details |
|---|---|
| **Homepage** | Hero section, featured projects, recent blog posts |
| **Portfolio** | Full project grid with tech stack, achievements, gallery, file downloads |
| **Blog** | Article listing with tag filtering, search, Markdown rendering |
| **Blog Detail** | Responsive 2-column layout with interactive Table of Contents, scroll spy, reading progress bar |
| **Project Detail** | Case study layout with sticky sidebar, hero image, YouTube embeds, downloadable files |
| **Contact** | Message form with flash feedback |
| **Newsletter** | Email subscription system |

### 🔐 Admin Dashboard (`/admin`)
| Module | Capabilities |
|---|---|
| **Profile** | Name, bio, social links, profile photo, password change |
| **Projects** | Create / edit / delete / reorder projects with drag-and-drop sort |
| **Blog** | Full Markdown editor (SimpleMDE), tags, slug, cover image, publish/draft status |
| **File Attachments** | Upload multiple files (PDFs, ZIPs, videos, docs) per project — visitors can download them |
| **Messages** | View and mark contact form messages as read |
| **Subscribers** | Manage newsletter subscriber list |

### 🎨 UI/UX
- **Glassmorphism** design with backdrop blur panels
- **AOS (Animate on Scroll)** entrance animations
- **Mouse particle trail** effect with random colors
- **Reading progress bar** fixed to the navigation header
- **YouTube auto-embed** — paste any YouTube link in Markdown and it renders as a responsive iframe
- **Fully responsive** — mobile-first, works on all screen sizes

---

## 🗂️ Project Structure

```
LandingPage with CMS/
├── ba_portfolio/
│   ├── app.py                  # Main Flask application (routes, models, logic)
│   ├── requirements.txt        # Python dependencies
│   ├── instance/
│   │   └── portfolio.db        # SQLite database (auto-created)
│   ├── static/
│   │   ├── uploads/            # Profile & background images
│   │   └── attachments/        # Project file attachments (downloads)
│   └── templates/
│       ├── base.html           # Global layout, navbar, progress bar, particle effect
│       ├── home.html           # Landing page
│       ├── projects.html       # Portfolio list
│       ├── project_detail.html # Project case study page
│       ├── blog.html           # Blog listing
│       ├── blog_detail.html    # Blog article reader with TOC
│       ├── contact.html        # Contact form
│       └── admin/
│           ├── layout.html     # Admin base layout
│           ├── dashboard.html  # Admin overview
│           ├── project_form.html
│           ├── projects_list.html
│           ├── blog_form.html
│           ├── blog_list.html
│           ├── profile.html
│           ├── messages.html
│           ├── subscribers.html
│           └── login.html
├── migrate_attachments.py      # One-time DB migration script
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip
- PostgreSQL (for production)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ba-portfolio.git
cd "ba-portfolio/LandingPage with CMS"
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv ba_portfolio/venv
ba_portfolio\venv\Scripts\activate

# macOS / Linux
python -m venv ba_portfolio/venv
source ba_portfolio/venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r ba_portfolio/requirements.txt
```

### 4. Configure Database
Copy `.env.example` to `.env` and update the `DATABASE_URL`.
- For **Local Development**: You can keep the default `sqlite:///portfolio.db`.
- For **Production**: Use `postgresql://username:password@localhost:5432/db_name`.

### 5. Run the development server

```bash
cd ba_portfolio
python app.py
```

The app will be available at **http://127.0.0.1:5000**

### 5. First-time login

| URL | Credentials |
|---|---|
| `http://127.0.0.1:5000/login` | Password: `admin123` |

> ⚠️ **Change your password immediately** after first login via the Profile page.

---

## 🗃️ Database Migrations

If you update the database model after the initial setup (e.g. adding a new column), run the relevant migration script:

```bash
# Add the 'attachments' column (run once if upgrading from an older version)
python migrate_attachments.py
```

SQLAlchemy's `db.create_all()` will handle brand-new installations automatically.

---

## 📝 Content Guide

### Writing Blog Posts
- Go to **Admin → Blog → New Article**
- Use the **SimpleMDE** editor for full Markdown support
- Paste a YouTube URL on its own line — it will auto-embed as a video player on the public site
- Set status to **Published** to make it visible

### Adding Projects
- Go to **Admin → Projects → New Project**
- Description supports **full Markdown** (headings, lists, code blocks, links, YouTube embeds)
- Achievements are one per line and support inline Markdown
- Upload multiple files in the **Attachments** section — visitors will see a "Project Files" section with download buttons

### Featured Projects
- Check **"Feature on Homepage"** in the project form to show the project on the landing page
- Drag and drop in the projects list to change the display order

---

## 🚀 Production Deployment

### Using Gunicorn (recommended)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables (optional)

Create a `.env` file in `ba_portfolio/`:

```env
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=sqlite:///portfolio.db
```

### Nginx (reverse proxy example)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/ba_portfolio/static/;
    }
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask, Flask-SQLAlchemy |
| **Database** | SQLite (via SQLAlchemy ORM) |
| **Auth** | Werkzeug password hashing, Flask session |
| **Markdown** | markdown2 (with extras: fenced code, tables, strikethrough) |
| **Frontend** | Tailwind CSS (CDN), Vanilla JavaScript |
| **Animations** | AOS (Animate on Scroll), custom CSS transitions |
| **Admin Editor** | SimpleMDE (Markdown editor) |
| **Production** | Gunicorn WSGI server |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙋 Author

Built and designed with ❤️ as a full-stack developer portfolio platform.  
Feel free to fork, customize, and make it your own.
