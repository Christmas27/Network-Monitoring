import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/network_dashboard.db')
    SNMP_COMMUNITY = os.environ.get('SNMP_COMMUNITY', 'public')
    SSH_TIMEOUT = int(os.environ.get('SSH_TIMEOUT', 30))