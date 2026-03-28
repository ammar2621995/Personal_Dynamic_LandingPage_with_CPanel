import sys
import os
from dotenv import load_dotenv

# --- CONFIGURATION ---
# The absolute path to the project directory
project_folder = os.path.dirname(os.path.abspath(__file__))

# Link your project directory to sys.path
if project_folder not in sys.path:
    sys.path.append(project_folder)

# Move into the project directory
os.chdir(project_folder)

# Load environment variables from .env
load_dotenv(os.path.join(project_folder, '.env'))

# Import the Flask application object
from app import app as application
