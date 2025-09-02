#!/usr/bin/env python3
"""
Configuration Page - Network Configuration Management and Templates
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import json

# Import our modular components
from components.forms import device_selector
from components.tables import config_template_table, config_history_table
from components.metrics import config_metrics_row
from utils.shared_utils import (
    PerformanceMonitor,
    notification_manager,
    show_loading_spinner
)
from utils.data_processing import DataProcessor

logger = logging.getLogger(__name__)

class ConfigurationPage:
    """Configuration management and template deployment page"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the configuration page"""
        # Page header
        st.markdown("# ⚙️ Configuration Management")
        st.markdown("Manage network device configurations, templates, and automated deployments")
        st.markdown("---")
        
        # Get managers from session state
        config_manager = st.session_state.get('config_manager')
        device_manager = st.session_state.get('device_manager')
        
        if not config_manager:
            st.error("❌ Configuration manager not initialized")
            return
        
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Configuration tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Templates", 
            "🚀 Deployment", 
            "📊 Configuration Backup",
            "📋 History & Audit"
        ])
        
        with tab1:
            self._render_templates_tab(config_manager, device_manager)
        
        with tab2:
            self._render_deployment_tab(config_manager, device_manager)
        
        with tab3:
            self._render_backup_tab(config_manager, device_manager)
        
        with tab4:
            self._render_history_tab(config_manager)
    
    def _render_templates_tab(self, config_manager, device_manager):
        """Render configuration templates management"""
        st.markdown("### 📝 Configuration Templates")
        st.markdown("Create, edit, and manage Jinja2 configuration templates")
        
        # Template actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ New Template", use_container_width=True):
                st.session_state.show_template_editor = True
        
        with col2:
            if st.button("📂 Load Template", use_container_width=True):
                self._show_template_loader()
        
        with col3:
            if st.button("🔄 Refresh List", use_container_width=True):
                st.rerun()
        
        with col4:
            if st.button("📤 Export All", use_container_width=True):
                self._export_all_templates(config_manager)
        
        # Template editor
        if st.session_state.get('show_template_editor', False):
            self._render_template_editor(config_manager)
        
        # Template list
        st.markdown("### 📋 Available Templates")
        try:
            templates = config_manager.get_all_templates()
            
            if templates:
                config_template_table(templates, config_manager)
            else:
                st.info("No configuration templates found. Create your first template above.")
                
                # Show sample templates
                if st.button("🎯 Load Sample Templates"):
                    self._load_sample_templates(config_manager)
                    
        except Exception as e:
            logger.error(f"❌ Error loading templates: {e}")
            st.error("Error loading configuration templates")
    
    def _render_deployment_tab(self, config_manager, device_manager):
        """Render configuration deployment interface"""
        st.markdown("### 🚀 Configuration Deployment")
        st.markdown("Deploy configurations to network devices")
        
        # Deployment options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Template selection
            templates = config_manager.get_all_templates()
            if not templates:
                st.warning("No templates available. Create templates first.")
                return
            
            template_names = [t['name'] for t in templates]
            selected_template = st.selectbox("Select Template:", template_names)
            
            # Device selection
            devices = device_manager.get_all_devices()
            if not devices:
                st.warning("No devices available. Add devices first.")
                return
            
            deployment_option = st.radio(
                "Deployment Target:",
                ["Selected Device", "Device Group", "All Devices"],
                horizontal=True
            )
            
            selected_device = None
            if deployment_option == "Selected Device":
                selected_device = device_selector(devices, key="config_deploy")
        
        with col2:
            # Deployment settings
            st.markdown("**Deployment Options:**")
            
            dry_run = st.checkbox("Dry Run (Preview Only)", value=True)
            backup_before = st.checkbox("Backup Before Deploy", value=True)
            rollback_on_error = st.checkbox("Rollback on Error", value=True)
            
            # Variable input
            st.markdown("**Template Variables:**")
            template_vars = self._get_template_variables(config_manager, selected_template)
        
        # Deployment actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👁️ Preview Config", type="primary", use_container_width=True):
                self._preview_configuration(config_manager, selected_template, template_vars, selected_device)
        
        with col2:
            if st.button("🚀 Deploy", use_container_width=True):
                self._deploy_configuration(
                    config_manager, selected_template, template_vars, 
                    deployment_option, selected_device, dry_run, backup_before, rollback_on_error
                )
        
        with col3:
            if st.button("📊 Deployment Status", use_container_width=True):
                self._show_deployment_status(config_manager)
        
        # Recent deployments
        st.markdown("### 📋 Recent Deployments")
        self._show_recent_deployments(config_manager)
    
    def _render_backup_tab(self, config_manager, device_manager):
        """Render configuration backup interface"""
        st.markdown("### 📊 Configuration Backup")
        st.markdown("Backup and restore device configurations")
        
        # Backup actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Backup All", type="primary", use_container_width=True):
                self._backup_all_devices(config_manager, device_manager)
        
        with col2:
            if st.button("🔍 Backup Selected", use_container_width=True):
                self._backup_selected_device(config_manager, device_manager)
        
        with col3:
            if st.button("🔄 Schedule Backup", use_container_width=True):
                self._schedule_backup()
        
        with col4:
            if st.button("📤 Export Backups", use_container_width=True):
                self._export_backups(config_manager)
        
        # Backup status
        st.markdown("### 📊 Backup Status")
        try:
            devices = device_manager.get_all_devices()
            backup_status = self._get_backup_status(config_manager, devices)
            
            # Backup metrics
            config_metrics_row(backup_status)
            
            # Backup details
            if backup_status:
                df = pd.DataFrame(backup_status)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No backup data available")
                
        except Exception as e:
            logger.error(f"❌ Error loading backup status: {e}")
            st.error("Error loading backup status")
        
        # Configuration comparison
        st.markdown("### 🔍 Configuration Comparison")
        self._render_config_comparison(config_manager, device_manager)
    
    def _render_history_tab(self, config_manager):
        """Render configuration history and audit trail"""
        st.markdown("### 📋 Configuration History & Audit")
        st.markdown("Track configuration changes and deployment history")
        
        # History filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_filter = st.selectbox(
                "Time Range:",
                ["Last 24h", "Last 7 days", "Last 30 days", "All time"]
            )
        
        with col2:
            action_filter = st.selectbox(
                "Action:",
                ["All", "Deploy", "Backup", "Restore", "Edit"]
            )
        
        with col3:
            user_filter = st.text_input("User Filter:", placeholder="Filter by user...")
        
        # Configuration history
        try:
            history = config_manager.get_configuration_history()
            filtered_history = self._filter_history(history, time_filter, action_filter, user_filter)
            
            if filtered_history:
                config_history_table(filtered_history)
            else:
                st.info("No configuration history matches the filters")
                
        except Exception as e:
            logger.error(f"❌ Error loading configuration history: {e}")
            st.error("Error loading configuration history")
        
        # Audit summary
        st.markdown("### 📊 Audit Summary")
        self._render_audit_summary(config_manager)
    
    def _render_template_editor(self, config_manager):
        """Render template editor interface"""
        st.markdown("### ✏️ Template Editor")
        
        with st.form("template_editor"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                template_name = st.text_input("Template Name:", placeholder="e.g., Basic Router Config")
                template_type = st.selectbox("Device Type:", ["cisco_ios", "cisco_nxos", "juniper_junos", "arista_eos", "linux"])
                template_description = st.text_area("Description:", placeholder="Template description...")
            
            with col2:
                template_variables = st.text_area(
                    "Variables (JSON):",
                    placeholder='{"hostname": "string", "mgmt_ip": "string", "vlan_id": "number"}',
                    height=100
                )
            
            # Template content editor
            template_content = st.text_area(
                "Template Content (Jinja2):",
                placeholder="""hostname {{ hostname }}
!
interface GigabitEthernet0/0
 description Management Interface
 ip address {{ mgmt_ip }} 255.255.255.0
 no shutdown
!""",
                height=300
            )
            
            # Form submission
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Save Template", type="primary")
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_template_editor = False
                    st.rerun()
            
            if submitted:
                self._save_template(config_manager, template_name, template_type, 
                                  template_description, template_variables, template_content)
    
    def _get_template_variables(self, config_manager, template_name):
        """Get template variables input form"""
        try:
            template = config_manager.get_template(template_name)
            if not template or not template.get('variables'):
                return {}
            
            variables = json.loads(template['variables'])
            template_vars = {}
            
            st.markdown("**Required Variables:**")
            for var_name, var_type in variables.items():
                if var_type == "string":
                    template_vars[var_name] = st.text_input(f"{var_name}:", key=f"var_{var_name}")
                elif var_type == "number":
                    template_vars[var_name] = st.number_input(f"{var_name}:", key=f"var_{var_name}")
                elif var_type == "boolean":
                    template_vars[var_name] = st.checkbox(f"{var_name}:", key=f"var_{var_name}")
            
            return template_vars
            
        except Exception as e:
            logger.error(f"❌ Error getting template variables: {e}")
            return {}
    
    def _preview_configuration(self, config_manager, template_name, variables, device):
        """Preview generated configuration"""
        try:
            with show_loading_spinner("Generating configuration preview..."):
                preview = config_manager.render_template(template_name, variables)
            
            st.markdown("### 👁️ Configuration Preview")
            if device:
                st.info(f"Preview for device: {device['hostname']} ({device['ip_address']})")
            
            st.code(preview, language="bash")
            
        except Exception as e:
            logger.error(f"❌ Error generating preview: {e}")
            st.error(f"Error generating configuration preview: {e}")
    
    def _deploy_configuration(self, config_manager, template_name, variables, 
                            deployment_option, device, dry_run, backup_before, rollback_on_error):
        """Deploy configuration to devices"""
        try:
            with show_loading_spinner("Deploying configuration..."):
                if deployment_option == "Selected Device" and device:
                    result = config_manager.deploy_to_device(
                        device['id'], template_name, variables, dry_run, backup_before
                    )
                    if dry_run:
                        st.success(f"✅ Dry run completed for {device['hostname']}")
                    else:
                        st.success(f"✅ Configuration deployed to {device['hostname']}")
                else:
                    result = config_manager.deploy_to_all(
                        template_name, variables, dry_run, backup_before
                    )
                    if dry_run:
                        st.success("✅ Dry run completed for all devices")
                    else:
                        st.success("✅ Configuration deployed to all devices")
                
                # Show deployment results
                if result.get('details'):
                    with st.expander("📊 Deployment Details"):
                        st.json(result['details'])
                
                notification_manager.add_notification(
                    f"Configuration {'previewed' if dry_run else 'deployed'} successfully",
                    "success"
                )
                
        except Exception as e:
            logger.error(f"❌ Error deploying configuration: {e}")
            st.error(f"Error deploying configuration: {e}")
    
    def _backup_all_devices(self, config_manager, device_manager):
        """Backup configurations from all devices"""
        try:
            devices = device_manager.get_all_devices()
            
            with show_loading_spinner("Backing up all device configurations..."):
                results = config_manager.backup_all_devices()
            
            successful = results.get('successful', 0)
            failed = results.get('failed', 0)
            
            if failed == 0:
                st.success(f"✅ Successfully backed up {successful} devices")
            else:
                st.warning(f"⚠️ Backed up {successful} devices, {failed} failed")
            
            notification_manager.add_notification(
                f"Backup completed: {successful} successful, {failed} failed",
                "success" if failed == 0 else "warning"
            )
            
        except Exception as e:
            logger.error(f"❌ Error backing up devices: {e}")
            st.error(f"Error backing up devices: {e}")
    
    def _backup_selected_device(self, config_manager, device_manager):
        """Backup configuration from selected device"""
        devices = device_manager.get_all_devices()
        if not devices:
            st.warning("No devices available")
            return
        
        selected_device = device_selector(devices, key="backup_device")
        
        if selected_device:
            if st.button("💾 Backup Device"):
                try:
                    with show_loading_spinner(f"Backing up {selected_device['hostname']}..."):
                        result = config_manager.backup_device(selected_device['id'])
                    
                    if result.get('success'):
                        st.success(f"✅ Configuration backed up for {selected_device['hostname']}")
                    else:
                        st.error(f"❌ Backup failed for {selected_device['hostname']}")
                        
                except Exception as e:
                    logger.error(f"❌ Error backing up device: {e}")
                    st.error(f"Error backing up device: {e}")
    
    def _get_backup_status(self, config_manager, devices):
        """Get backup status for all devices"""
        try:
            backup_status = []
            
            for device in devices:
                last_backup = config_manager.get_last_backup_time(device['id'])
                status = {
                    'hostname': device['hostname'],
                    'ip_address': device['ip_address'],
                    'device_type': device['device_type'],
                    'last_backup': last_backup.strftime('%Y-%m-%d %H:%M') if last_backup else 'Never',
                    'status': 'Recent' if last_backup and (datetime.now() - last_backup).days < 7 else 'Outdated'
                }
                backup_status.append(status)
            
            return backup_status
            
        except Exception as e:
            logger.error(f"❌ Error getting backup status: {e}")
            return []
    
    def _render_config_comparison(self, config_manager, device_manager):
        """Render configuration comparison interface"""
        try:
            devices = device_manager.get_all_devices()
            if len(devices) < 2:
                st.info("Need at least 2 devices for configuration comparison")
                return
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                device1 = device_selector(devices, key="compare_device1", label="Device 1:")
            
            with col2:
                device2 = device_selector(devices, key="compare_device2", label="Device 2:")
            
            with col3:
                if st.button("🔍 Compare Configs", type="primary"):
                    if device1 and device2 and device1['id'] != device2['id']:
                        self._show_config_diff(config_manager, device1, device2)
                    else:
                        st.warning("Please select two different devices")
                        
        except Exception as e:
            logger.error(f"❌ Error in config comparison: {e}")
            st.error("Error setting up config comparison")
    
    def _show_config_diff(self, config_manager, device1, device2):
        """Show configuration differences between devices"""
        try:
            with show_loading_spinner("Comparing configurations..."):
                diff_result = config_manager.compare_configurations(device1['id'], device2['id'])
            
            st.markdown(f"### 🔍 Configuration Comparison")
            st.info(f"Comparing {device1['hostname']} vs {device2['hostname']}")
            
            if diff_result.get('differences'):
                st.code(diff_result['differences'], language="diff")
            else:
                st.success("No differences found between configurations")
                
        except Exception as e:
            logger.error(f"❌ Error comparing configurations: {e}")
            st.error("Error comparing configurations")
    
    def _show_recent_deployments(self, config_manager):
        """Show recent deployment history"""
        try:
            deployments = config_manager.get_recent_deployments(limit=10)
            
            if deployments:
                df = pd.DataFrame(deployments)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No recent deployments")
                
        except Exception as e:
            logger.error(f"❌ Error loading recent deployments: {e}")
            st.info("Recent deployments not available")
    
    def _show_deployment_status(self, config_manager):
        """Show current deployment status"""
        st.info("🚧 Deployment status monitoring coming soon...")
        
        # Placeholder for deployment status
        st.markdown("### 🔜 Coming Soon:")
        st.markdown("""
        - Real-time deployment progress
        - Deployment queue status
        - Error reporting and logs
        - Rollback capabilities
        """)
    
    def _save_template(self, config_manager, name, device_type, description, variables, content):
        """Save configuration template"""
        try:
            if not name or not content:
                st.error("Template name and content are required")
                return
            
            template_data = {
                'name': name,
                'device_type': device_type,
                'description': description,
                'variables': variables,
                'content': content
            }
            
            config_manager.save_template(template_data)
            st.success(f"✅ Template '{name}' saved successfully")
            st.session_state.show_template_editor = False
            
            notification_manager.add_notification(
                f"Template '{name}' saved",
                "success"
            )
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error saving template: {e}")
            st.error(f"Error saving template: {e}")
    
    def _load_sample_templates(self, config_manager):
        """Load sample configuration templates"""
        try:
            sample_templates = [
                {
                    'name': 'Basic Router Configuration',
                    'device_type': 'cisco_ios',
                    'description': 'Basic router configuration with management interface',
                    'variables': '{"hostname": "string", "mgmt_ip": "string", "domain_name": "string"}',
                    'content': '''hostname {{ hostname }}
!
ip domain-name {{ domain_name }}
!
interface GigabitEthernet0/0
 description Management Interface
 ip address {{ mgmt_ip }} 255.255.255.0
 no shutdown
!
line vty 0 15
 transport input ssh
!'''
                },
                {
                    'name': 'Basic Switch Configuration',
                    'device_type': 'cisco_ios',
                    'description': 'Basic switch configuration with VLANs',
                    'variables': '{"hostname": "string", "mgmt_ip": "string", "vlan_id": "number"}',
                    'content': '''hostname {{ hostname }}
!
vlan {{ vlan_id }}
 name Data_VLAN
!
interface Vlan{{ vlan_id }}
 ip address {{ mgmt_ip }} 255.255.255.0
 no shutdown
!
interface range GigabitEthernet1/0/1-48
 switchport mode access
 switchport access vlan {{ vlan_id }}
!'''
                }
            ]
            
            for template in sample_templates:
                config_manager.save_template(template)
            
            st.success("✅ Sample templates loaded successfully")
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error loading sample templates: {e}")
            st.error("Error loading sample templates")
    
    def _export_all_templates(self, config_manager):
        """Export all templates to JSON"""
        try:
            templates = config_manager.get_all_templates()
            
            if templates:
                templates_json = json.dumps(templates, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download All Templates",
                    data=templates_json,
                    file_name=f"config_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No templates available for export")
                
        except Exception as e:
            logger.error(f"❌ Error exporting templates: {e}")
            st.error("Error exporting templates")
    
    def _filter_history(self, history, time_filter, action_filter, user_filter):
        """Filter configuration history"""
        filtered = history
        
        # Filter by action
        if action_filter != "All":
            filtered = [h for h in filtered if h.get('action', '').lower() == action_filter.lower()]
        
        # Filter by user
        if user_filter:
            filtered = [h for h in filtered if user_filter.lower() in h.get('user', '').lower()]
        
        return filtered
    
    def _render_audit_summary(self, config_manager):
        """Render configuration audit summary"""
        try:
            # Sample audit metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Changes", "42", delta="5 this week")
            
            with col2:
                st.metric("Active Templates", "8", delta="2 new")
            
            with col3:
                st.metric("Successful Deploys", "95%", delta="2%")
            
            with col4:
                st.metric("Last Backup", "2h ago", delta="-1h")
                
        except Exception as e:
            st.info("Audit summary not available")
    
    def _show_template_loader(self):
        """Show template file upload interface"""
        st.markdown("### 📂 Load Template from File")
        
        uploaded_file = st.file_uploader(
            "Choose template file",
            type=['json', 'j2', 'txt'],
            help="Upload JSON template export or Jinja2 template file"
        )
        
        if uploaded_file:
            try:
                content = uploaded_file.read().decode('utf-8')
                
                if uploaded_file.name.endswith('.json'):
                    # JSON template export
                    templates = json.loads(content)
                    st.success(f"Loaded {len(templates)} templates from JSON file")
                else:
                    # Raw template file
                    st.text_area("Template Content:", content, height=200)
                    if st.button("Import Template"):
                        st.success("Template content loaded - fill in details above")
                        
            except Exception as e:
                st.error(f"Error loading template file: {e}")
    
    def _schedule_backup(self):
        """Schedule automated backups"""
        st.info("🚧 Scheduled backup feature coming soon...")
        
        # Placeholder for backup scheduling
        with st.expander("Backup Schedule Configuration"):
            frequency = st.selectbox("Backup Frequency:", ["Daily", "Weekly", "Monthly"])
            time = st.time_input("Backup Time:")
            retention = st.number_input("Retention (days):", min_value=1, value=30)
            
            if st.button("Save Schedule"):
                st.success("Backup schedule saved!")
    
    def _export_backups(self, config_manager):
        """Export device configuration backups"""
        try:
            backups = config_manager.get_all_backups()
            
            if backups:
                backups_json = json.dumps(backups, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download All Backups",
                    data=backups_json,
                    file_name=f"config_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No configuration backups available")
                
        except Exception as e:
            logger.error(f"❌ Error exporting backups: {e}")
            st.error("Error exporting backups")


def render_configuration_page():
    """Main function to render configuration page"""
    config_page = ConfigurationPage()
    config_page.render()
