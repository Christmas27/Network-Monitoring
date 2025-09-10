#!/usr/bin/env python3
"""
Devices Page - Device Management and Inventory
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Import our modular components
from components.forms import (
    add_device_form, 
    device_selector
)
from components.tables import device_list_table
from components.metrics import device_metrics_row
from utils.shared_utils import (
    PerformanceMonitor,
    notification_manager,
    show_loading_spinner
)
from utils.data_processing import DataProcessor
from utils.lab_helpers import (
    get_lab_devices,
    ensure_default_lab_devices,
    validate_lab_environment
)

logger = logging.getLogger(__name__)

class DevicesPage:
    """Device management page with CRUD operations"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the devices page"""
        # Page header
        st.markdown("# 📱 Device Management")
        st.markdown("Manage your network device inventory and monitor device status")
        st.markdown("---")
        
        # Get device manager from session state
        device_manager = st.session_state.get('device_manager')
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Action tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Device List", 
            "➕ Add Device", 
            "📊 Device Details", 
            "🛠️ Bulk Operations"
        ])
        
        with tab1:
            self._render_device_list(device_manager)
        
        with tab2:
            self._render_add_device(device_manager)
        
        with tab3:
            self._render_device_details(device_manager)
        
        with tab4:
            self._render_bulk_operations(device_manager)
    
    def _render_device_list(self, device_manager):
        """Render device list and management"""
        st.markdown("### 📋 Device Inventory")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh List", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🧪 Setup Lab Devices", use_container_width=True):
                self._setup_lab_devices(device_manager)
        
        with col3:
            if st.button("🏥 Health Check All", use_container_width=True):
                self._run_health_check_all(device_manager)
        
        with col4:
            if st.button("📤 Export CSV", use_container_width=True):
                self._export_devices_csv(device_manager)
        
        # Get all devices
        try:
            devices = device_manager.get_all_devices()
            
            # Device metrics overview
            device_metrics_row(devices)
            
            # Filters
            st.markdown("#### 🔍 Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                device_types = ['All'] + list(set([d.get('device_type', 'unknown') for d in devices]))
                selected_type = st.selectbox("Device Type", device_types)
            
            with col2:
                statuses = ['All'] + list(set([d.get('status', 'unknown') for d in devices]))
                selected_status = st.selectbox("Status", statuses)
            
            with col3:
                search_term = st.text_input("🔍 Search", placeholder="Search hostname or IP...")
            
            # Filter devices
            filtered_devices = self._filter_devices(
                devices, selected_type, selected_status, search_term
            )
            
            # Display device table
            if filtered_devices:
                device_list_table(filtered_devices, device_manager)
            else:
                st.info("No devices found matching the filters")
            
        except Exception as e:
            logger.error(f"❌ Error loading devices: {e}")
            st.error("Error loading device list")
    
    def _render_add_device(self, device_manager):
        """Render add device form"""
        st.markdown("### ➕ Add New Device")
        
        # Device form tabs
        form_tab1, form_tab2 = st.tabs(["📝 Manual Entry", "🧪 Lab Templates"])
        
        with form_tab1:
            # Manual device entry
            if add_device_form(device_manager):
                st.success("✅ Device added successfully!")
                notification_manager.add_notification(
                    "New device added to inventory", 
                    "success"
                )
                st.rerun()
        
        with form_tab2:
            # Lab device templates
            self._render_lab_templates(device_manager)
    
    def _render_device_details(self, device_manager):
        """Render device details and actions"""
        st.markdown("### 📊 Device Details & Actions")
        
        # Device selector
        devices = device_manager.get_all_devices()
        if not devices:
            st.info("No devices available. Add some devices first.")
            return
        
        selected_device = device_selector(devices, key="device_details")
        
        if not selected_device:
            st.info("Please select a device to view details")
            return
        
        # Device details tabs
        details_tab1, details_tab2, details_tab3 = st.tabs([
            "ℹ️ Information", 
            "🔧 Actions", 
            "📈 Monitoring"
        ])
        
        with details_tab1:
            self._render_device_info(selected_device, device_manager)
        
        with details_tab2:
            self._render_device_actions(selected_device, device_manager)
        
        with details_tab3:
            self._render_device_monitoring(selected_device)
    
    def _render_bulk_operations(self, device_manager):
        """Render bulk operations"""
        st.markdown("### 🛠️ Bulk Operations")
        
        # Bulk operation tabs
        bulk_tab1, bulk_tab2, bulk_tab3 = st.tabs([
            "📤 Import/Export", 
            "🏥 Health Checks", 
            "🗑️ Cleanup"
        ])
        
        with bulk_tab1:
            self._render_import_export(device_manager)
        
        with bulk_tab2:
            self._render_bulk_health_checks(device_manager)
        
        with bulk_tab3:
            self._render_cleanup_operations(device_manager)
    
    def _render_device_info(self, device: Dict[str, Any], device_manager):
        """Render detailed device information"""
        try:
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Information:**")
                st.write(f"**Hostname:** {device.get('hostname', 'N/A')}")
                st.write(f"**IP Address:** {device.get('ip_address', 'N/A')}")
                st.write(f"**Device Type:** {device.get('device_type', 'N/A')}")
                st.write(f"**Status:** {device.get('status', 'N/A')}")
            
            with col2:
                st.markdown("**Technical Details:**")
                st.write(f"**Manufacturer:** {device.get('manufacturer', 'N/A')}")
                st.write(f"**Model:** {device.get('model', 'N/A')}")
                st.write(f"**SSH Port:** {device.get('ssh_port', 22)}")
                st.write(f"**Tags:** {device.get('tags', 'None')}")
            
            # Timestamps
            st.markdown("**Timestamps:**")
            st.write(f"**Created:** {device.get('created_at', 'N/A')}")
            st.write(f"**Last Updated:** {device.get('updated_at', 'N/A')}")
            st.write(f"**Last Seen:** {device.get('last_seen', 'N/A')}")
            
            # Edit device button
            if st.button("✏️ Edit Device", use_container_width=True):
                st.info("Edit functionality coming soon...")
                # self._edit_device(device, device_manager)
            
        except Exception as e:
            logger.error(f"❌ Error rendering device info: {e}")
            st.error("Error loading device information")
    
    def _render_device_actions(self, device: Dict[str, Any], device_manager):
        """Render device action buttons"""
        try:
            st.markdown("**Available Actions:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔗 Test Connectivity", use_container_width=True):
                    self._test_device_connectivity(device)
                
                if st.button("📊 Get System Info", use_container_width=True):
                    self._get_device_system_info(device)
                
                if st.button("🛡️ Security Scan", use_container_width=True):
                    self._run_security_scan(device)
            
            with col2:
                if st.button("💾 Backup Config", use_container_width=True):
                    self._backup_device_config(device)
                
                if st.button("🔄 Update Status", use_container_width=True):
                    self._update_device_status(device, device_manager)
                
                if st.button("🗑️ Delete Device", use_container_width=True, type="secondary"):
                    self._delete_device(device, device_manager)
            
        except Exception as e:
            logger.error(f"❌ Error rendering device actions: {e}")
            st.error("Error loading device actions")
    
    def _render_device_monitoring(self, device: Dict[str, Any]):
        """Render device monitoring information"""
        try:
            st.markdown("**Monitoring Data:**")
            
            # Get monitoring data for this device
            network_monitor = st.session_state.get('network_monitor')
            if not network_monitor:
                st.info("Network monitor not available")
                return
            
            # This would be implemented based on your monitoring system
            st.info("Monitoring integration coming soon...")
            
            # Placeholder for monitoring charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Performance Metrics:**")
                st.metric("Response Time", "125ms", "↓ 15ms")
                st.metric("Uptime", "99.5%", "↑ 0.2%")
            
            with col2:
                st.markdown("**Resource Usage:**")
                st.metric("CPU Usage", "45%", "↑ 5%")
                st.metric("Memory Usage", "67%", "↓ 3%")
            
        except Exception as e:
            logger.error(f"❌ Error rendering device monitoring: {e}")
            st.error("Error loading monitoring data")
    
    def _render_lab_templates(self, device_manager):
        """Render lab device templates"""
        st.markdown("#### 🧪 Lab Device Templates")
        
        lab_devices = get_lab_devices(device_manager)
        
        if not lab_devices:
            st.info("No lab device templates available")
            return
        
        st.markdown("**Quick Add Lab Devices:**")
        
        for device in lab_devices:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{device['hostname']}** ({device['device_type']}) - {device['ip_address']}")
            
            with col2:
                if st.button(f"➕ Add", key=f"add_lab_{device['hostname']}"):
                    try:
                        device_manager.add_device(device)
                        st.success(f"✅ {device['hostname']} added")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding {device['hostname']}: {e}")
            
            with col3:
                if st.button(f"🔗 Test", key=f"test_lab_{device['hostname']}"):
                    self._test_lab_device_connectivity(device)
    
    def _render_import_export(self, device_manager):
        """Render import/export functionality"""
        st.markdown("#### 📤 Import/Export Devices")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export Devices:**")
            if st.button("📤 Export to CSV", use_container_width=True):
                self._export_devices_csv(device_manager)
            
            if st.button("📤 Export to JSON", use_container_width=True):
                self._export_devices_json(device_manager)
        
        with col2:
            st.markdown("**Import Devices:**")
            uploaded_file = st.file_uploader(
                "Choose CSV file", 
                type=['csv'],
                help="Upload a CSV file with device information"
            )
            
            if uploaded_file and st.button("📥 Import CSV"):
                self._import_devices_csv(uploaded_file, device_manager)
    
    def _render_bulk_health_checks(self, device_manager):
        """Render bulk health check operations"""
        st.markdown("#### 🏥 Bulk Health Checks")
        
        devices = device_manager.get_all_devices()
        
        if not devices:
            st.info("No devices available for health checks")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔗 Test All Connectivity", use_container_width=True):
                self._run_bulk_connectivity_test(devices)
        
        with col2:
            if st.button("🛡️ Scan All Security", use_container_width=True):
                self._run_bulk_security_scan(devices)
        
        # Health check results
        if 'bulk_health_results' in st.session_state:
            st.markdown("**Health Check Results:**")
            results = st.session_state.bulk_health_results
            
            for result in results:
                status_icon = "✅" if result['success'] else "❌"
                st.write(f"{status_icon} **{result['hostname']}**: {result['message']}")
    
    def _render_cleanup_operations(self, device_manager):
        """Render cleanup operations"""
        st.markdown("#### 🗑️ Cleanup Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Remove Offline Devices", use_container_width=True):
                self._cleanup_offline_devices(device_manager)
        
        with col2:
            if st.button("🧹 Clean Duplicate Entries", use_container_width=True):
                self._cleanup_duplicate_devices(device_manager)
        
        st.warning("⚠️ **Warning:** Cleanup operations cannot be undone!")
    
    def _filter_devices(self, devices: List[Dict], device_type: str, status: str, search: str) -> List[Dict]:
        """Filter devices based on criteria"""
        filtered = devices
        
        # Filter by device type
        if device_type != 'All':
            filtered = [d for d in filtered if d.get('device_type') == device_type]
        
        # Filter by status
        if status != 'All':
            filtered = [d for d in filtered if d.get('status') == status]
        
        # Filter by search term
        if search:
            search = search.lower()
            filtered = [d for d in filtered 
                       if search in d.get('hostname', '').lower() 
                       or search in d.get('ip_address', '').lower()]
        
        return filtered
    
    def _setup_lab_devices(self, device_manager):
        """Setup default lab devices"""
        try:
            with show_loading_spinner("Setting up lab devices..."):
                ensure_default_lab_devices(device_manager)
            
            st.success("✅ Lab devices setup completed!")
            notification_manager.add_notification(
                "Lab environment setup completed", 
                "success"
            )
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error setting up lab devices: {e}")
            st.error(f"Error setting up lab devices: {e}")
    
    def _test_device_connectivity(self, device: Dict[str, Any]):
        """Test connectivity to a specific device"""
        try:
            host = device.get('ip_address', '').split(':')[0]
            port = int(device.get('ssh_port', 22))
            
            with show_loading_spinner(f"Testing connectivity to {device['hostname']}..."):
                result = self.performance_monitor.check_port_availability(host, port)
            
            if result:
                st.success(f"✅ {device['hostname']} is reachable")
            else:
                st.error(f"❌ {device['hostname']} is not reachable")
            
        except Exception as e:
            logger.error(f"❌ Error testing connectivity: {e}")
            st.error(f"Error testing connectivity: {e}")
    
    def _run_health_check_all(self, device_manager):
        """Run health check on all devices"""
        try:
            devices = device_manager.get_all_devices()
            
            with show_loading_spinner("Running health checks on all devices..."):
                results = []
                for device in devices:
                    host = device.get('ip_address', '').split(':')[0]
                    port = int(device.get('ssh_port', 22))
                    
                    is_reachable = self.performance_monitor.check_port_availability(host, port, timeout=2)
                    
                    results.append({
                        'hostname': device['hostname'],
                        'success': is_reachable,
                        'message': 'Reachable' if is_reachable else 'Not reachable'
                    })
                
                st.session_state.bulk_health_results = results
            
            st.success("✅ Health check completed for all devices")
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error running health check: {e}")
            st.error(f"Error running health check: {e}")
    
    def _export_devices_csv(self, device_manager):
        """Export devices to CSV"""
        try:
            devices = device_manager.get_all_devices()
            if not devices:
                st.warning("No devices to export")
                return
            
            df = pd.DataFrame(devices)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"devices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            logger.error(f"❌ Error exporting CSV: {e}")
            st.error(f"Error exporting CSV: {e}")
    
    def _update_device_status(self, device: Dict[str, Any], device_manager):
        """Update device status"""
        try:
            host = device.get('ip_address', '').split(':')[0]
            port = int(device.get('ssh_port', 22))
            
            with show_loading_spinner("Updating device status..."):
                is_reachable = self.performance_monitor.check_port_availability(host, port)
                new_status = 'online' if is_reachable else 'offline'
                
                device_manager.update_device_status(device['id'], new_status)
            
            st.success(f"✅ Device status updated to: {new_status}")
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error updating device status: {e}")
            st.error(f"Error updating device status: {e}")

def render_devices_page():
    """Main function to render devices page"""
    devices_page = DevicesPage()
    devices_page.render()
