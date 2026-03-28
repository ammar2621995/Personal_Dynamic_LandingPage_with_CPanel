# 🚀 Deploying to PythonAnywhere (SQLite Setup)

This guide walks you through the steps to successfully host your Flask project on [PythonAnywhere](https://www.pythonanywhere.com/). This setup is pre-configured to use **SQLite** as the database.

## 1. Prepare your Files
Ensure your project files are uploaded to PythonAnywhere. You can do this by:
- Using `git clone` from your repository in the PythonAnywhere console.
- Uploading a ZIP file via the "Files" tab.

Your project structure on PythonAnywhere should look like this:
```text
/home/yourusername/ba_portfolio/
├── app.py
├── requirements.txt
├── .env
├── static/
├── templates/
├── ...
```

## 2. Create a Virtual Environment
Open a **Bash Console** in PythonAnywhere and run the following:
```bash
# Navigate to your project folder
cd /home/yourusername/ba_portfolio

# Create a virtualenv (replace 3.x with your desired version, e.g., 3.10)
mkvirtualenv --python=/usr/bin/python3.10 ba_env

# Install the project requirements
pip install -r requirements.txt
```

## 3. Configure `.env` for Production
Update your `.env` file on PythonAnywhere to ensure it's secure for production:
- **`SECRET_KEY`**: Set a unique, strong value.
- **`DATABASE_URL`**: Keep it as `sqlite:///portfolio.db`. The app automatically converts this to an absolute path.
- **`FLASK_ENV`**: Change to `production`.
- **`FLASK_DEBUG`**: Change to `False`.

## 4. Set up the Web App
1. Go to the **Web** tab on PythonAnywhere.
2. Click **"Add a new web app"**.
3. Choose **Manual Configuration** (do NOT choose the Flask quick setup).
4. Select the **Python version** matching your virtualenv (e.g., 3.10).
5. After it's created:
    - **Code Section**: Set "Source code" to `/home/yourusername/ba_portfolio`.
    - **Virtualenv Section**: Set "Virtualenv" to `/home/yourusername/.virtualenvs/ba_env`.
    - **WSGI configuration file**: Click the link to open the file and replace its contents with the logic from `wsgi_pa.py` (adjust the `project_folder` path as needed).

## 5. WSGI Configuration Logic
Your PythonAnywhere WSGI file should look like this (replace `yourusername`!):
```python
import sys
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
project_folder = '/home/yourusername/ba_portfolio'

if project_folder not in sys.path:
    sys.path.append(project_folder)

os.chdir(project_folder)
load_dotenv(os.path.join(project_folder, '.env'))

from app import app as application
```

## 6. Reload!
Click the green "Reload" button on the **Web** tab. Your app should now be live! 🚀

## 7. Static Files Configuration (Optional but Recommended)
For better performance, you can map your static files in the **Web** tab under the **Static files** section:
- **URL**: `/static/`
- **Path**: `/home/yourusername/ba_portfolio/static`

> [!TIP]
> Since we're using SQLite, your database file `portfolio.db` will be created automatically on the first run inside your project directory.

