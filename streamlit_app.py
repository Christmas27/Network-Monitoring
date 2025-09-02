#!/usr/bin/env python3
"""
Network Monitoring Dashboard - 100% Python Frontend
Modular Streamlit Application with Professional Architecture

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the modules path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration and utilities
from config.app_config import apply_page_config, PAGES, SESSION_KEYS
from config.styling import apply_custom_css
from utils.auth_helpers import (
    init_session_auth, 
    check_authentication, 
    show_login_form, 
    show_user_info,
    can_access_page,
    show_access_denied,
    enable_dev_auth
)
from utils.shared_utils import (
    show_debug_info,
    notification_manager
)

# Import backend modules
from modules.device_manager import DeviceManager
from modules.network_monitor import NetworkMonitor
from modules.security_scanner import SecurityScanner
from modules.config_manager import ConfigManager
from modules.ansible_manager_simple import AnsibleManager
from modules.real_ssh_manager import get_ssh_manager, RealSSHLabManager
from modules.catalyst_center_integration import CatalystCenterManager
from modules.wsl_ansible_bridge import get_wsl_ansible_bridge

# Import page modules
from app_pages.dashboard import render_dashboard_page
from app_pages.devices import render_devices_page
from app_pages.automation import render_automation_page
from app_pages.security import render_security_page
from app_pages.configuration import render_configuration_page
from app_pages.monitoring import render_monitoring_page
from app_pages.topology import render_topology_page

# Apply page configuration
apply_page_config()


class NetworkDashboardApp:
    """Main application class for Network Monitoring Dashboard"""
    
    def __init__(self):
        """Initialize the dashboard application"""
        self.initialize_session_state()
        self.initialize_managers()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        # Initialize authentication
        init_session_auth()
        
        # Initialize timestamps
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        
        # Initialize automation history
        if 'automation_history' not in st.session_state:
            st.session_state.automation_history = []
        
        # Initialize cached playbooks
        if 'cached_playbooks' not in st.session_state:
            st.session_state.cached_playbooks = []
    
    def initialize_managers(self):
        """Initialize and cache backend managers"""
        try:
            # Device Manager
            if SESSION_KEYS['device_manager'] not in st.session_state:
                st.session_state[SESSION_KEYS['device_manager']] = DeviceManager()
            
            # Network Monitor
            if SESSION_KEYS['network_monitor'] not in st.session_state:
                st.session_state[SESSION_KEYS['network_monitor']] = NetworkMonitor()
            
            # Security Scanner
            if SESSION_KEYS['security_scanner'] not in st.session_state:
                st.session_state[SESSION_KEYS['security_scanner']] = SecurityScanner()
            
            # Config Manager
            if SESSION_KEYS['config_manager'] not in st.session_state:
                st.session_state[SESSION_KEYS['config_manager']] = ConfigManager()
            
            # SSH Manager
            if SESSION_KEYS['real_ssh_manager'] not in st.session_state:
                st.session_state[SESSION_KEYS['real_ssh_manager']] = get_ssh_manager()
            
            # WSL Ansible Bridge
            if SESSION_KEYS['wsl_ansible_bridge'] not in st.session_state:
                try:
                    st.session_state[SESSION_KEYS['wsl_ansible_bridge']] = get_wsl_ansible_bridge()
                except Exception as e:
                    logger.warning(f"WSL Ansible bridge not available: {e}")
                    st.session_state[SESSION_KEYS['wsl_ansible_bridge']] = None
            
            # Ansible Manager (fallback)
            if SESSION_KEYS['ansible_manager'] not in st.session_state:
                st.session_state[SESSION_KEYS['ansible_manager']] = AnsibleManager()
            
            # Catalyst Center Manager
            if SESSION_KEYS['catalyst_manager'] not in st.session_state:
                st.session_state[SESSION_KEYS['catalyst_manager']] = CatalystCenterManager()
            
            logger.info("✅ All managers initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing managers: {e}")
            st.error(f"Error initializing backend managers: {e}")
    
    def render_sidebar(self):
        """Render sidebar navigation and quick stats"""
        with st.sidebar:
            # App title
            st.markdown("# 🌐 Network Dashboard")
            
            # Authentication status
            if check_authentication():
                st.markdown("### 👤 Authentication")
                auth_status = "🟢 Authenticated"
                st.markdown(f"**Status:** {auth_status}")
                show_user_info()
            else:
                st.markdown("### 🔐 Authentication")
                st.markdown("**Status:** 🔴 Not Authenticated")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            
            # Page selection
            page_index = 0
            if 'current_page' in st.session_state:
                try:
                    page_index = PAGES.index(st.session_state.current_page)
                except ValueError:
                    page_index = 0
            
            selected_page = st.selectbox(
                "Choose a page",
                PAGES,
                index=page_index,
                key="page_selector"
            )
            
            # Store current page
            st.session_state.current_page = selected_page
            
            st.markdown("---")
            
            # Quick stats
            self.render_quick_stats()
            
            # Quick actions
            self.render_quick_actions()
            
            # Debug info (optional)
            show_debug_info()
    
    def render_quick_stats(self):
        """Render quick statistics in sidebar"""
        st.markdown("### 📊 Quick Stats")
        
        try:
            device_manager = st.session_state.get(SESSION_KEYS['device_manager'])
            if device_manager:
                devices = device_manager.get_all_devices()
                device_count = len(devices)
                online_devices = len([d for d in devices if d.get('status') == 'online'])
                st.metric("Devices", device_count, f"{online_devices} online")
            else:
                st.metric("Devices", "0", "Loading...")
        except Exception as e:
            st.metric("Devices", "Error", str(e)[:20])
        
        try:
            playbooks = st.session_state.get('cached_playbooks', [])
            st.metric("Playbooks", len(playbooks), "Available")
        except:
            st.metric("Playbooks", "0", "Loading...")
        
        # System status
        try:
            from utils.shared_utils import PerformanceMonitor
            monitor = PerformanceMonitor()
            metrics = monitor.get_system_metrics()
            cpu_percent = metrics.get('cpu', {}).get('percent', 0)
            cpu_status = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 85 else "🔴"
            st.metric("System CPU", f"{cpu_status} {cpu_percent:.1f}%", "Real-time")
        except:
            st.metric("System", "🟢 Ready", "Monitoring")
    
    def render_quick_actions(self):
        """Render quick action buttons in sidebar"""
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.last_refresh = datetime.now()
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache cleared!")
        
        # Show last refresh time
        refresh_time = st.session_state.last_refresh.strftime('%H:%M:%S')
        st.markdown(f"**Last Refresh:** {refresh_time}")
    
    def render_main_content(self):
        """Render main content area based on selected page"""
        # Apply custom styling
        apply_custom_css()
        
        # Get current page
        current_page = st.session_state.get('current_page', PAGES[0])
        
        # Check authentication and access control
        if not check_authentication():
            # Development mode bypass (optional)
            if not enable_dev_auth():
                show_login_form()
                return
        
        # Check page access permissions
        page_name = current_page.split(' ')[-1].lower()  # Extract page name
        if not can_access_page(page_name):
            show_access_denied()
            return
        
        # Show notifications
        notification_manager.show_notifications()
        
        # Route to appropriate page
        try:
            if current_page == "🏠 Dashboard":
                render_dashboard_page()
            elif current_page == "📱 Devices":
                render_devices_page()
            elif current_page == "🤖 Automation":
                render_automation_page()
            elif current_page == "🛡️ Security":
                render_security_page()
            elif current_page == "⚙️ Configuration":
                render_configuration_page()
            elif current_page == "🔍 Monitoring":
                render_monitoring_page()
            elif current_page == "🌐 Topology":
                render_topology_page()
            else:
                st.error(f"Page not implemented: {current_page}")
                
        except Exception as e:
            logger.error(f"❌ Error rendering page {current_page}: {e}")
            st.error(f"Error loading page: {e}")
            
            # Show error details in expander
            with st.expander("🐛 Error Details"):
                st.code(str(e))
    
    def run(self):
        """Main application entry point"""
        try:
            # Render sidebar
            self.render_sidebar()
            
            # Render main content
            self.render_main_content()
            
        except Exception as e:
            logger.error(f"❌ Critical application error: {e}")
            st.error("Critical application error. Please refresh the page.")
            
            # Show error details for debugging
            with st.expander("🐛 Critical Error Details"):
                st.code(str(e))


def main():
    """Main function to run the dashboard"""
    try:
        # Only initialize once using session state check
        if 'app_initialized' not in st.session_state:
            # Initialize cached playbooks
            if 'cached_playbooks' not in st.session_state:
                try:
                    # Try to get playbooks from ansible manager
                    ansible_manager = st.session_state.get('ansible_manager')
                    if ansible_manager and hasattr(ansible_manager, 'get_available_playbooks'):
                        st.session_state.cached_playbooks = ansible_manager.get_available_playbooks()
                    else:
                        # Fallback: scan playbook directories directly
                        import os
                        import glob
                        playbook_dirs = ['ansible_playbooks', 'ansible_projects/playbooks']
                        playbooks = []
                        for directory in playbook_dirs:
                            if os.path.exists(directory):
                                yml_files = glob.glob(f"{directory}/*.yml") + glob.glob(f"{directory}/*.yaml")
                                for file in yml_files:
                                    playbooks.append({
                                        'name': os.path.basename(file).replace('.yml', '').replace('.yaml', ''),
                                        'path': file,
                                        'description': f"Playbook: {os.path.basename(file)}"
                                    })
                        st.session_state.cached_playbooks = playbooks
                except Exception as e:
                    logger.error(f"❌ Error loading playbooks: {e}")
                    st.session_state.cached_playbooks = []
            
            # Mark as initialized
            st.session_state.app_initialized = True
        
        # Create and run the dashboard app (only once)
        if 'dashboard_app' not in st.session_state:
            st.session_state.dashboard_app = NetworkDashboardApp()
        
        # Run the app
        st.session_state.dashboard_app.run()
        
    except Exception as e:
        logger.error(f"❌ Fatal error starting application: {e}")
        st.error("Fatal error starting application. Please check the logs.")
        
        # Show error details
        with st.expander("🐛 Fatal Error Details"):
            st.code(str(e))


if __name__ == "__main__":
    main()
