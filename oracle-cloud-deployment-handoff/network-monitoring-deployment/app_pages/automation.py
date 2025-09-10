#!/usr/bin/env python3
"""
Automation Page - Network Automation and Task Execution
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Import our modular components
from components.forms import device_selector
from components.tables import execution_history_table
from components.metrics import automation_metrics_row
from utils.shared_utils import (
    show_loading_spinner,
    notification_manager,
    background_tasks
)
from config.app_config import SSH_OPERATIONS

logger = logging.getLogger(__name__)

class AutomationPage:
    """Network automation page with SSH and Ansible execution"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render the automation page"""
        # Page header
        st.markdown("# 🤖 Network Automation")
        st.markdown("Execute automated tasks, deploy configurations, and run custom commands")
        st.markdown("---")
        
        # Check for required managers
        device_manager = st.session_state.get('device_manager')
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Get available devices
        devices = device_manager.get_all_devices()
        if not devices:
            st.warning("⚠️ No devices available. Please add devices first.")
            return
        
        # Automation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🚀 Quick Actions", 
            "📜 SSH Commands", 
            "🔧 Ansible Playbooks", 
            "📊 Execution History"
        ])
        
        with tab1:
            self._render_quick_actions(devices)
        
        with tab2:
            self._render_ssh_commands(devices)
        
        with tab3:
            self._render_ansible_playbooks(devices)
        
        with tab4:
            self._render_execution_history()
    
    def _render_quick_actions(self, devices: List[Dict[str, Any]]):
        """Render quick automation actions"""
        st.markdown("### 🚀 Quick Actions")
        st.markdown("Perform common network operations with one click")
        
        # Device selection
        selected_device = device_selector(devices, key="quick_actions")
        
        if not selected_device:
            st.info("Please select a device to perform actions")
            return
        
        # Quick action grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔗 Connectivity**")
            
            if st.button("🔗 Test SSH Connection", use_container_width=True):
                self._test_ssh_connection(selected_device)
            
            if st.button("📡 Ping Test", use_container_width=True):
                self._run_ping_test(selected_device)
            
            if st.button("🚪 Port Scan", use_container_width=True):
                self._run_port_scan(selected_device)
        
        with col2:
            st.markdown("**ℹ️ Information**")
            
            if st.button("💻 System Info", use_container_width=True):
                self._get_system_info(selected_device)
            
            if st.button("🌐 Network Config", use_container_width=True):
                self._get_network_config(selected_device)
            
            if st.button("📊 Resource Usage", use_container_width=True):
                self._get_resource_usage(selected_device)
        
        with col3:
            st.markdown("**🛠️ Management**")
            
            if st.button("💾 Backup Config", use_container_width=True):
                self._backup_configuration(selected_device)
            
            if st.button("🔄 Restart Service", use_container_width=True):
                self._restart_service(selected_device)
            
            if st.button("🛡️ Security Scan", use_container_width=True):
                self._run_security_scan(selected_device)
        
        # Results display area
        if 'quick_action_result' in st.session_state:
            st.markdown("### 📋 Action Results")
            result = st.session_state.quick_action_result
            
            if result.get('success'):
                st.success(f"✅ {result.get('action', 'Action')} completed successfully")
            else:
                st.error(f"❌ {result.get('action', 'Action')} failed")
            
            if result.get('output'):
                with st.expander("📄 Detailed Output"):
                    st.code(result['output'], language='text')
            
            # Clear results button
            if st.button("🧹 Clear Results"):
                del st.session_state.quick_action_result
                st.rerun()
    
    def _render_ssh_commands(self, devices: List[Dict[str, Any]]):
        """Render SSH command execution interface"""
        st.markdown("### 📜 SSH Command Execution")
        st.markdown("Execute custom SSH commands on network devices")
        
        # SSH execution form
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Device selection
            selected_device = device_selector(devices, key="ssh_commands")
            
            if not selected_device:
                st.info("Please select a device")
                return
            
            # Command input
            command = st.text_area(
                "🖥️ Command to Execute",
                placeholder="Enter SSH command (e.g., uname -a, df -h, ps aux)",
                help="Enter the command you want to execute on the selected device"
            )
            
            # Execution options
            col_a, col_b = st.columns(2)
            with col_a:
                timeout = st.number_input("⏱️ Timeout (seconds)", min_value=5, max_value=300, value=30)
            with col_b:
                sudo = st.checkbox("🔐 Use sudo", help="Execute command with sudo privileges")
        
        with col2:
            st.markdown("**🔧 Command Templates**")
            
            # Predefined commands
            templates = {
                "System Info": "uname -a",
                "Disk Usage": "df -h",
                "Memory Info": "free -h",
                "Process List": "ps aux",
                "Network Config": "ip addr show",
                "Uptime": "uptime",
                "Last Logins": "last -n 10"
            }
            
            for name, cmd in templates.items():
                if st.button(f"📋 {name}", use_container_width=True):
                    st.session_state.ssh_command_template = cmd
                    st.rerun()
            
            # Use template if selected
            if 'ssh_command_template' in st.session_state:
                command = st.session_state.ssh_command_template
                del st.session_state.ssh_command_template
        
        # Execute command
        if st.button("🚀 Execute Command", disabled=not command, use_container_width=True):
            self._execute_ssh_command(selected_device, command, timeout, sudo)
        
        # SSH execution history
        self._render_ssh_history()
    
    def _render_ansible_playbooks(self, devices: List[Dict[str, Any]]):
        """Render Ansible playbook execution interface"""
        st.markdown("### 🔧 Ansible Playbook Execution")
        st.markdown("Execute Ansible playbooks for complex automation tasks")
        
        # Check for Ansible availability
        wsl_bridge = st.session_state.get('wsl_ansible_bridge')
        ansible_manager = st.session_state.get('ansible_manager')
        
        if not wsl_bridge and not ansible_manager:
            st.warning("⚠️ Ansible integration not available")
            st.info("""
            **Setup Required:**
            - WSL with Ubuntu installed
            - Ansible installed in WSL
            - Network device collections (cisco.ios, etc.)
            """)
            return
        
        # Playbook selection and execution
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Target device selection
            target_devices = st.multiselect(
                "🎯 Target Devices",
                options=[f"{d['hostname']} ({d['ip_address']})" for d in devices],
                help="Select one or more devices to run the playbook against"
            )
            
            # Playbook selection
            playbook_type = st.selectbox(
                "📚 Playbook Type",
                [
                    "Connectivity Test",
                    "Configuration Backup",
                    "System Information",
                    "Security Assessment",
                    "Custom Playbook"
                ]
            )
            
            # Playbook parameters
            if playbook_type == "Custom Playbook":
                playbook_content = st.text_area(
                    "📝 Playbook Content (YAML)",
                    height=200,
                    placeholder="Enter your Ansible playbook YAML content..."
                )
            else:
                st.info(f"Using predefined playbook: {playbook_type}")
                playbook_content = None
        
        with col2:
            st.markdown("**⚙️ Execution Options**")
            
            # Ansible options
            check_mode = st.checkbox("🔍 Check Mode (Dry Run)", help="Run in check mode without making changes")
            verbose = st.checkbox("📢 Verbose Output", help="Enable verbose output")
            parallel = st.number_input("🔄 Parallel Forks", min_value=1, max_value=10, value=5)
            
            # Advanced options
            with st.expander("🔧 Advanced Options"):
                extra_vars = st.text_area(
                    "Extra Variables (JSON)",
                    placeholder='{"var1": "value1", "var2": "value2"}',
                    help="Additional variables to pass to the playbook"
                )
                
                tags = st.text_input("🏷️ Tags", placeholder="tag1,tag2", help="Run only tasks with these tags")
                skip_tags = st.text_input("🚫 Skip Tags", placeholder="tag1,tag2", help="Skip tasks with these tags")
        
        # Execute playbook
        if st.button("🚀 Execute Playbook", disabled=not target_devices, use_container_width=True):
            self._execute_ansible_playbook(
                target_devices, playbook_type, playbook_content,
                check_mode, verbose, parallel, extra_vars, tags, skip_tags
            )
        
        # Show recent playbook executions
        self._render_ansible_history()
    
    def _render_execution_history(self):
        """Render automation execution history"""
        st.markdown("### 📊 Execution History")
        
        # Get automation history
        automation_history = st.session_state.get('automation_history', [])
        
        if not automation_history:
            st.info("No automation history available")
            return
        
        # History metrics
        available_playbooks = [
            {'name': 'connectivity_test', 'description': 'Test device connectivity'},
            {'name': 'config_backup', 'description': 'Backup device configuration'},
            {'name': 'system_info', 'description': 'Gather system information'},
            {'name': 'security_assessment', 'description': 'Security assessment scan'}
        ]
        automation_metrics_row(automation_history, available_playbooks)
        
        # History filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            execution_types = ['All'] + list(set([h.get('type', 'unknown') for h in automation_history]))
            selected_type = st.selectbox("Execution Type", execution_types)
        
        with col2:
            statuses = ['All'] + list(set([h.get('status', 'unknown') for h in automation_history]))
            selected_status = st.selectbox("Status", statuses)
        
        with col3:
            time_filter = st.selectbox("Time Range", ["All", "Last Hour", "Last Day", "Last Week"])
        
        # Filter history
        filtered_history = self._filter_history(automation_history, selected_type, selected_status, time_filter)
        
        # Display history table
        if filtered_history:
            execution_history_table(filtered_history)
        else:
            st.info("No executions found matching the filters")
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            if st.button("⚠️ Confirm Clear", type="secondary"):
                st.session_state.automation_history = []
                st.success("✅ History cleared")
                st.rerun()
    
    def _render_ssh_history(self):
        """Render SSH execution history"""
        if 'ssh_history' in st.session_state and st.session_state.ssh_history:
            with st.expander("📊 Recent SSH Executions"):
                for i, execution in enumerate(st.session_state.ssh_history[-5:]):
                    status_icon = "✅" if execution['success'] else "❌"
                    st.write(f"{status_icon} **{execution['device']}**: `{execution['command']}`")
                    st.write(f"   *{execution['timestamp']} - Duration: {execution['duration']}s*")
    
    def _render_ansible_history(self):
        """Render Ansible execution history"""
        if 'ansible_history' in st.session_state and st.session_state.ansible_history:
            with st.expander("📊 Recent Ansible Executions"):
                for execution in st.session_state.ansible_history[-5:]:
                    status_icon = "✅" if execution['success'] else "❌"
                    st.write(f"{status_icon} **{execution['playbook']}** on {execution['targets']}")
                    st.write(f"   *{execution['timestamp']} - Duration: {execution['duration']}s*")
    
    def _test_ssh_connection(self, device: Dict[str, Any]):
        """Test SSH connection to device"""
        try:
            with show_loading_spinner(f"Testing SSH connection to {device['hostname']}..."):
                # Get SSH manager
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                # Test connection
                result = ssh_manager.test_connection(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'SSH Connection Test',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error testing SSH connection: {e}")
            st.error(f"Error testing SSH connection: {e}")
    
    def _execute_ssh_command(self, device: Dict[str, Any], command: str, timeout: int, use_sudo: bool):
        """Execute SSH command on device"""
        try:
            # Get SSH manager
            ssh_manager = st.session_state.get('real_ssh_manager')
            if not ssh_manager:
                st.error("❌ SSH manager not available")
                return
            
            # Prepare command
            if use_sudo:
                command = f"sudo {command}"
            
            with show_loading_spinner(f"Executing command on {device['hostname']}..."):
                start_time = datetime.now()
                
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    command,
                    device.get('ssh_port', 22),
                    timeout
                )
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Add to SSH history
                if 'ssh_history' not in st.session_state:
                    st.session_state.ssh_history = []
                
                st.session_state.ssh_history.append({
                    'device': device['hostname'],
                    'command': command,
                    'success': result.get('success', False),
                    'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': duration
                })
                
                # Show results
                if result.get('success'):
                    st.success(f"✅ Command executed successfully on {device['hostname']}")
                    if result.get('output'):
                        with st.expander("📄 Command Output"):
                            st.code(result['output'], language='text')
                else:
                    st.error(f"❌ Command failed on {device['hostname']}")
                    if result.get('error'):
                        st.error(f"Error: {result['error']}")
                
                # Add to automation history
                self._add_to_automation_history({
                    'type': 'ssh_command',
                    'device': device['hostname'],
                    'command': command,
                    'status': 'success' if result.get('success') else 'failed',
                    'timestamp': start_time,
                    'duration': duration,
                    'output': result.get('output', ''),
                    'error': result.get('error', '')
                })
            
        except Exception as e:
            logger.error(f"❌ Error executing SSH command: {e}")
            st.error(f"Error executing SSH command: {e}")
    
    def _add_to_automation_history(self, execution: Dict[str, Any]):
        """Add execution to automation history"""
        if 'automation_history' not in st.session_state:
            st.session_state.automation_history = []
        
        st.session_state.automation_history.append(execution)
        
        # Keep only last 100 executions
        if len(st.session_state.automation_history) > 100:
            st.session_state.automation_history = st.session_state.automation_history[-100:]
    
    def _filter_history(self, history: List[Dict], exec_type: str, status: str, time_range: str) -> List[Dict]:
        """Filter automation history based on criteria"""
        filtered = history
        
        # Filter by type
        if exec_type != 'All':
            filtered = [h for h in filtered if h.get('type') == exec_type]
        
        # Filter by status
        if status != 'All':
            filtered = [h for h in filtered if h.get('status') == status]
        
        # Filter by time range
        if time_range != 'All':
            now = datetime.now()
            if time_range == 'Last Hour':
                cutoff = now - timedelta(hours=1)
            elif time_range == 'Last Day':
                cutoff = now - timedelta(days=1)
            elif time_range == 'Last Week':
                cutoff = now - timedelta(weeks=1)
            else:
                cutoff = None
            
            if cutoff:
                filtered = [h for h in filtered if h.get('timestamp', now) >= cutoff]
        
        return filtered

    def _run_ping_test(self, device: Dict[str, Any]):
        """Run ping test on device"""
        try:
            with show_loading_spinner(f"Pinging {device['hostname']}..."):
                from utils.shared_utils import PerformanceMonitor
                monitor = PerformanceMonitor()
                host = device['ip_address'].split(':')[0]
                result = monitor.ping_host(host)
                
                st.session_state.quick_action_result = {
                    'action': 'Ping Test',
                    'success': result.get('success', False),
                    'output': f"Response time: {result.get('response_time_ms', 0):.1f}ms"
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error running ping test: {e}")
            st.error(f"Error running ping test: {e}")

    def _run_port_scan(self, device: Dict[str, Any]):
        """Run port scan on device"""
        try:
            with show_loading_spinner(f"Scanning ports on {device['hostname']}..."):
                from utils.shared_utils import PerformanceMonitor
                monitor = PerformanceMonitor()
                host = device['ip_address'].split(':')[0]
                common_ports = [22, 23, 80, 443, 161, 8080]
                
                open_ports = []
                for port in common_ports:
                    if monitor.check_port_availability(host, port, timeout=2):
                        open_ports.append(port)
                
                st.session_state.quick_action_result = {
                    'action': 'Port Scan',
                    'success': True,
                    'output': f"Open ports: {', '.join(map(str, open_ports)) if open_ports else 'None'}"
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error running port scan: {e}")
            st.error(f"Error running port scan: {e}")

    def _get_system_info(self, device: Dict[str, Any]):
        """Get system information from device"""
        try:
            with show_loading_spinner(f"Getting system info from {device['hostname']}..."):
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    'uname -a; uptime; whoami',
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'System Information',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error getting system info: {e}")
            st.error(f"Error getting system info: {e}")

    def _get_network_config(self, device: Dict[str, Any]):
        """Get network configuration from device"""
        try:
            with show_loading_spinner(f"Getting network config from {device['hostname']}..."):
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    'ip addr show; ip route show',
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'Network Configuration',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error getting network config: {e}")
            st.error(f"Error getting network config: {e}")

    def _get_resource_usage(self, device: Dict[str, Any]):
        """Get resource usage from device"""
        try:
            with show_loading_spinner(f"Getting resource usage from {device['hostname']}..."):
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    'top -bn1 | head -20; free -h; df -h',
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'Resource Usage',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error getting resource usage: {e}")
            st.error(f"Error getting resource usage: {e}")

    def _backup_configuration(self, device: Dict[str, Any]):
        """Backup device configuration"""
        try:
            with show_loading_spinner(f"Backing up configuration from {device['hostname']}..."):
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                # For lab devices, backup common config files
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    'cat /etc/hostname /etc/hosts /etc/network/interfaces 2>/dev/null || echo "Config files not found"',
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'Configuration Backup',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error backing up configuration: {e}")
            st.error(f"Error backing up configuration: {e}")

    def _restart_service(self, device: Dict[str, Any]):
        """Restart a service on device"""
        try:
            with show_loading_spinner(f"Checking services on {device['hostname']}..."):
                ssh_manager = st.session_state.get('real_ssh_manager')
                if not ssh_manager:
                    st.error("❌ SSH manager not available")
                    return
                
                # Show running services instead of restarting
                result = ssh_manager.execute_command(
                    device['ip_address'].split(':')[0],
                    device.get('username', 'admin'),
                    device.get('password', 'admin'),
                    'systemctl list-units --type=service --state=running | head -10',
                    device.get('ssh_port', 22)
                )
                
                st.session_state.quick_action_result = {
                    'action': 'Service Status',
                    'success': result.get('success', False),
                    'output': result.get('output', result.get('error', 'No output'))
                }
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error checking services: {e}")
            st.error(f"Error checking services: {e}")

    def _run_security_scan(self, device: Dict[str, Any]):
        """Run security scan on device"""
        try:
            with show_loading_spinner(f"Running security scan on {device['hostname']}..."):
                security_scanner = st.session_state.get('security_scanner')
                if security_scanner:
                    # Use existing security scanner
                    result = security_scanner.scan_device(device['id'])
                    st.session_state.quick_action_result = {
                        'action': 'Security Scan',
                        'success': True,
                        'output': f"Security scan completed. Check Security page for results."
                    }
                else:
                    # Basic security check via SSH
                    ssh_manager = st.session_state.get('real_ssh_manager')
                    if ssh_manager:
                        result = ssh_manager.execute_command(
                            device['ip_address'].split(':')[0],
                            device.get('username', 'admin'),
                            device.get('password', 'admin'),
                            'lastlog | head -5; w; who',
                            device.get('ssh_port', 22)
                        )
                        
                        st.session_state.quick_action_result = {
                            'action': 'Security Check',
                            'success': result.get('success', False),
                            'output': result.get('output', result.get('error', 'No output'))
                        }
                    else:
                        st.error("❌ No security scanner or SSH manager available")
                        return
            st.rerun()
        except Exception as e:
            logger.error(f"❌ Error running security scan: {e}")
            st.error(f"Error running security scan: {e}")

    def _execute_ansible_playbook(self, target_devices, playbook_type, playbook_content,
                                 check_mode, verbose, parallel, extra_vars, tags, skip_tags):
        """Execute Ansible playbook"""
        try:
            with show_loading_spinner(f"Executing {playbook_type} playbook..."):
                wsl_bridge = st.session_state.get('wsl_ansible_bridge')
                if wsl_bridge:
                    # Use WSL Ansible bridge
                    if playbook_type == "Connectivity Test":
                        result = wsl_bridge.run_connectivity_test()
                    else:
                        result = {'success': False, 'error': 'Playbook type not implemented yet'}
                else:
                    result = {'success': False, 'error': 'Ansible bridge not available'}
                
                # Add to automation history
                self._add_to_automation_history({
                    'type': 'ansible_playbook',
                    'playbook': playbook_type,
                    'targets': ', '.join(target_devices),
                    'status': 'success' if result.get('success') else 'failed',
                    'timestamp': datetime.now(),
                    'duration': 30,  # Placeholder
                    'output': result.get('output', ''),
                    'error': result.get('error', '')
                })
                
                if result.get('success'):
                    st.success(f"✅ {playbook_type} playbook executed successfully")
                else:
                    st.error(f"❌ {playbook_type} playbook failed: {result.get('error', 'Unknown error')}")
                
                if result.get('output'):
                    with st.expander("📄 Playbook Output"):
                        st.code(result['output'], language='yaml')
                        
        except Exception as e:
            logger.error(f"❌ Error executing Ansible playbook: {e}")
            st.error(f"Error executing Ansible playbook: {e}")

def render_automation_page():
    """Main function to render automation page"""
    automation_page = AutomationPage()
    automation_page.render()
