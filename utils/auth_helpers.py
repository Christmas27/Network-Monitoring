#!/usr/bin/env python3
"""
Authentication Helper Functions for Network Monitoring Dashboard
"""

import streamlit as st
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Simple authentication manager for dashboard access"""
    
    def __init__(self, db_path: str = "data/auth.db"):
        self.db_path = db_path
        self.init_auth_db()
    
    def init_auth_db(self):
        """Initialize authentication database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create default admin user if none exists
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                admin_password = self.hash_password("admin123")
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role) 
                    VALUES (?, ?, ?)
                """, ("admin", admin_password, "admin"))
                logger.info("🔑 Created default admin user (admin/admin123)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error initializing auth database: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute("""
                SELECT username, role, is_active FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'role': result[1],
                    'is_active': bool(result[2])
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error verifying credentials: {e}")
            return None
    
    def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (username,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error updating last login: {e}")

def check_authentication() -> bool:
    """Check if user is authenticated"""
    return 'authenticated' in st.session_state and st.session_state.authenticated

def get_current_user() -> Optional[str]:
    """Get current authenticated user"""
    if check_authentication():
        return st.session_state.get('username')
    return None

def get_user_role() -> str:
    """Get current user's role"""
    if check_authentication():
        return st.session_state.get('user_role', 'user')
    return 'guest'

def requires_auth(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            show_login_form()
            return None
        return func(*args, **kwargs)
    return wrapper

def requires_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            show_login_form()
            return None
        
        if get_user_role() != 'admin':
            st.error("❌ Admin access required")
            return None
            
        return func(*args, **kwargs)
    return wrapper

def show_login_form():
    """Display login form"""
    st.markdown("### 🔐 Authentication Required")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("🔑 Login", use_container_width=True)
        
        if submit:
            if username and password:
                auth_manager = AuthManager()
                user_info = auth_manager.verify_credentials(username, password)
                
                if user_info:
                    st.session_state.authenticated = True
                    st.session_state.username = user_info['username']
                    st.session_state.user_role = user_info['role']
                    
                    auth_manager.update_last_login(username)
                    st.success(f"✅ Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
            else:
                st.warning("⚠️ Please enter both username and password")
    
    # Show default credentials info
    with st.expander("🔧 Default Credentials", expanded=False):
        st.info("""
        **Default Admin Account:**
        - Username: `admin`
        - Password: `admin123`
        
        ⚠️ **Security Note:** Change default credentials in production!
        """)

def logout():
    """Logout current user"""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'username' in st.session_state:
        del st.session_state.username
    if 'user_role' in st.session_state:
        del st.session_state.user_role
    
    st.success("👋 Logged out successfully")
    st.rerun()

def show_user_info():
    """Display current user information in sidebar"""
    if check_authentication():
        # Don't create nested sidebar context - caller should already be in sidebar
        st.markdown("---")
        st.markdown("### 👤 User Information")
        
        user = get_current_user()
        role = get_user_role()
        
        st.markdown(f"**User:** {user}")
        st.markdown(f"**Role:** {role.title()}")
        
        if st.button("🔓 Logout", use_container_width=True):
                logout()

def get_access_control() -> Dict[str, List[str]]:
    """Get access control configuration"""
    return {
        'admin': [
            'dashboard', 'devices', 'automation', 
            'security', 'configuration', 'monitoring', 
            'topology', 'user_management'
        ],
        'user': [
            'dashboard', 'devices', 'monitoring', 
            'topology'
        ],
        'readonly': [
            'dashboard', 'monitoring', 'topology'
        ]
    }

def can_access_page(page: str) -> bool:
    """Check if current user can access a page"""
    if not check_authentication():
        return False
    
    role = get_user_role()
    access_control = get_access_control()
    
    allowed_pages = access_control.get(role, [])
    return page.lower() in allowed_pages

def show_access_denied():
    """Show access denied message"""
    st.error("🚫 Access Denied")
    st.info(f"Your role ({get_user_role()}) doesn't have access to this page.")

def init_session_auth():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'guest'

def get_auth_status_indicator() -> str:
    """Get authentication status indicator for UI"""
    if check_authentication():
        user = get_current_user()
        role = get_user_role()
        return f"🟢 {user} ({role})"
    else:
        return "🔴 Not Authenticated"

# Authentication bypass for development (optional)
def enable_dev_auth():
    """Enable development authentication bypass"""
    if st.checkbox("🚧 Development Mode (Skip Auth)"):
        st.session_state.authenticated = True
        st.session_state.username = "dev_user"
        st.session_state.user_role = "admin"
        st.warning("⚠️ Development authentication enabled")
        return True
    return False
