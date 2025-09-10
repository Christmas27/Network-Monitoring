import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')  # Changed for container compatibility
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/network_dashboard.db')
    
    # Network settings
    SNMP_COMMUNITY = os.environ.get('SNMP_COMMUNITY', 'public')
    SSH_TIMEOUT = int(os.environ.get('SSH_TIMEOUT', 30))
    
    # Cloud deployment settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Catalyst Center (if available)
    CATALYST_CENTER_HOST = os.environ.get('CATALYST_CENTER_HOST')
    CATALYST_CENTER_USERNAME = os.environ.get('CATALYST_CENTER_USERNAME')
    CATALYST_CENTER_PASSWORD = os.environ.get('CATALYST_CENTER_PASSWORD')