#!/usr/bin/env python3
"""
Reusable Table Components for Network Monitoring Dashboard
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

def device_list_table(devices: List[Dict[str, Any]], actions: bool = True, key_prefix: str = "device_table"):
    """
    Reusable device list table component
    
    Args:
        devices: List of device dictionaries
        actions: Whether to show action buttons
        key_prefix: Prefix for component keys
    """
    if not devices:
        st.info("📝 No devices found. Add devices to get started.")
        return
    
    # Prepare data for display
    display_data = []
    for i, device in enumerate(devices):
        # Status emoji
        status_emoji = {
            'online': '🟢',
            'offline': '🔴', 
            'unknown': '⚪',
            'maintenance': '🟡'
        }.get(device.get('status', 'unknown'), '⚪')
        
        # Device type emoji
        type_emoji = {
            'router': '🔀',
            'switch': '🔗',
            'firewall': '🛡️',
            'server': '🖥️',
            'access_point': '📡'
        }.get(device.get('device_type', 'unknown'), '📱')
        
        row_data = {
            'Status': f"{status_emoji} {device.get('status', 'unknown').title()}",
            'Device': f"{type_emoji} {device.get('hostname', 'Unknown')}",
            'IP Address': device.get('ip_address', 'N/A'),
            'Type': device.get('device_type', 'unknown').title(),
            'Manufacturer': device.get('manufacturer', 'N/A'),
            'Model': device.get('model', 'N/A'),
            'Tags': device.get('tags', ''),
            'Last Seen': device.get('last_seen', 'Never')
        }
        
        if actions:
            row_data['Actions'] = i  # Store index for action buttons
        
        display_data.append(row_data)
    
    # Create DataFrame
    df = pd.DataFrame(display_data)
    
    if actions:
        # Show table without actions column
        display_df = df.drop('Actions', axis=1)
        st.dataframe(display_df, use_container_width=True)
        
        # Action buttons
        st.markdown("#### 🔧 Device Actions")
        
        # Create columns for action buttons
        cols = st.columns(min(len(devices), 4))
        
        for i, device in enumerate(devices):
            col_idx = i % 4
            with cols[col_idx]:
                if st.button(f"🧪 Test {device.get('hostname', 'Device')}", key=f"{key_prefix}_test_{i}"):
                    with st.spinner(f"Testing connection to {device.get('hostname')}..."):
                        # Add your connection test logic here
                        st.success(f"✅ {device.get('hostname')} is reachable")
                
                if st.button(f"✏️ Edit {device.get('hostname', 'Device')}", key=f"{key_prefix}_edit_{i}"):
                    st.session_state[f'edit_device_{i}'] = device
                    st.rerun()
                
                if st.button(f"🗑️ Delete {device.get('hostname', 'Device')}", key=f"{key_prefix}_delete_{i}"):
                    st.session_state[f'delete_device_{i}'] = device
                    st.rerun()
    else:
        st.dataframe(df, use_container_width=True)

def security_alerts_table(alerts: List[Dict[str, Any]], limit: int = 10, key_prefix: str = "alerts_table"):
    """
    Reusable security alerts table component
    
    Args:
        alerts: List of security alert dictionaries
        limit: Maximum number of alerts to display
        key_prefix: Prefix for component keys
    """
    if not alerts:
        st.info("🛡️ No security alerts found. System is secure!")
        return
    
    # Limit alerts displayed
    display_alerts = alerts[:limit]
    
    for i, alert in enumerate(display_alerts):
        severity = alert.get('severity', 'unknown').lower()
        
        # Severity emoji and color
        severity_config = {
            'critical': {'emoji': '🔴', 'color': '#dc3545'},
            'high': {'emoji': '🟠', 'color': '#fd7e14'},
            'medium': {'emoji': '🟡', 'color': '#ffc107'},
            'low': {'emoji': '🟢', 'color': '#20c997'},
            'info': {'emoji': '🔵', 'color': '#17a2b8'}
        }
        
        config = severity_config.get(severity, {'emoji': '⚪', 'color': '#6c757d'})
        
        # Create expandable alert
        with st.expander(
            f"{config['emoji']} **{alert.get('severity', 'Unknown').title()}** - {alert.get('title', alert.get('alert_type', 'Security Alert'))}",
            expanded=severity in ['critical', 'high']
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {alert.get('description', 'No description available')}")
                if alert.get('device_id'):
                    st.markdown(f"**Affected Device:** {alert.get('device_id')} ({alert.get('device_name', 'Unknown')})")
                if alert.get('recommendation'):
                    st.markdown(f"**Recommendation:** {alert.get('recommendation')}")
            
            with col2:
                st.markdown(f"**Timestamp:** {alert.get('timestamp', 'Unknown')}")
                st.markdown(f"**Status:** {alert.get('status', 'Unknown')}")
                
                # Action buttons
                if st.button(f"✅ Mark Resolved", key=f"{key_prefix}_resolve_{i}"):
                    st.success("Alert marked as resolved")
                
                if st.button(f"🔕 Dismiss", key=f"{key_prefix}_dismiss_{i}"):
                    st.success("Alert dismissed")

def execution_history_table(history: List[Dict[str, Any]], limit: int = 10, key_prefix: str = "history_table"):
    """
    Reusable execution history table component
    
    Args:
        history: List of execution history dictionaries
        limit: Maximum number of executions to display
        key_prefix: Prefix for component keys
    """
    if not history:
        st.info("📝 No execution history available")
        return
    
    # Limit history displayed
    display_history = history[-limit:]  # Show most recent
    
    for i, execution in enumerate(reversed(display_history)):
        # Status emoji
        status_emoji = {
            'success': '✅',
            'completed': '✅',
            'failed': '❌',
            'error': '❌',
            'running': '🔄',
            'pending': '⏳'
        }.get(execution.get('status', 'unknown'), '❓')
        
        # Create expandable execution
        with st.expander(
            f"{status_emoji} **{execution.get('playbook', 'Unknown Operation')}** - {execution.get('start_time', 'Unknown time')}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if execution.get('description'):
                    st.markdown(f"**Description:** {execution.get('description')}")
                
                if execution.get('target_devices'):
                    st.markdown(f"**Target Devices:** {', '.join(execution.get('target_devices', []))}")
                
                if execution.get('output'):
                    st.markdown("**Output:**")
                    st.code(execution.get('output', 'No output available'), language='text')
            
            with col2:
                st.markdown(f"**Status:** {execution.get('status', 'Unknown')}")
                st.markdown(f"**Duration:** {execution.get('duration', 'Unknown')}")
                
                if execution.get('end_time'):
                    st.markdown(f"**Completed:** {execution.get('end_time')}")
                
                # Action buttons
                if st.button(f"📋 View Details", key=f"{key_prefix}_details_{i}"):
                    st.session_state[f'view_execution_{i}'] = execution
                    st.rerun()
                
                if execution.get('status') in ['failed', 'error']:
                    if st.button(f"🔄 Retry", key=f"{key_prefix}_retry_{i}"):
                        st.info("Retry functionality would be implemented here")

def monitoring_metrics_table(metrics: Dict[str, Any], key_prefix: str = "metrics_table"):
    """
    Reusable monitoring metrics table component
    
    Args:
        metrics: Dictionary of device metrics
        key_prefix: Prefix for component keys
    """
    if not metrics:
        st.info("📊 No monitoring data available. Click 'Refresh Metrics' to collect data.")
        return
    
    # Prepare data for display
    display_data = []
    for device_name, device_metrics in metrics.items():
        # Status emoji
        status = device_metrics.get('status', 'unknown')
        status_emoji = '🟢' if status == 'active' else '🔴'
        
        # Response time color coding
        response_time = device_metrics.get('ssh_response_time', 0)
        if response_time < 100:
            response_status = '🟢 Excellent'
        elif response_time < 500:
            response_status = '🟡 Good'
        else:
            response_status = '🔴 Poor'
        
        row_data = {
            'Device': device_name,
            'Status': f'{status_emoji} {status.title()}',
            'CPU %': f"{device_metrics.get('cpu_usage', 0):.1f}%",
            'Memory %': f"{device_metrics.get('memory_usage', 0):.1f}%",
            'SSH Response': f"{response_time:.0f}ms",
            'Response Status': response_status,
            'Last Updated': datetime.now().strftime('%H:%M:%S')
        }
        
        # Add ping data if available
        if device_metrics.get('ping_response_time'):
            row_data['Ping Response'] = f"{device_metrics.get('ping_response_time', 0):.0f}ms"
        
        display_data.append(row_data)
    
    # Create and display DataFrame
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)
    
    # Export option
    if st.button("📥 Export Monitoring Data", key=f"{key_prefix}_export"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"{key_prefix}_download"
        )

def topology_details_table(topology_data: Dict[str, Any], table_type: str = "devices", key_prefix: str = "topology_table"):
    """
    Reusable topology details table component
    
    Args:
        topology_data: Topology data dictionary
        table_type: Type of table ("devices" or "connections")
        key_prefix: Prefix for component keys
    """
    if table_type == "devices":
        if not topology_data.get('nodes'):
            st.info("🔍 No devices found in topology")
            return
        
        # Prepare device data
        devices_data = []
        for node in topology_data['nodes']:
            device_data = {
                'Device': node.get('label', node.get('id', 'Unknown')),
                'Type': node.get('type', 'Unknown').title(),
                'IP Address': node.get('ip', 'N/A'),
                'Status': node.get('status', 'Unknown').title(),
                'Model': node.get('model', 'N/A'),
                'Location': node.get('location', 'N/A')
            }
            devices_data.append(device_data)
        
        df = pd.DataFrame(devices_data)
        st.dataframe(df, use_container_width=True)
    
    elif table_type == "connections":
        if not topology_data.get('edges'):
            st.info("🔍 No connections found in topology")
            return
        
        # Prepare connection data
        connections_data = []
        for edge in topology_data['edges']:
            connection_data = {
                'From': edge.get('from', 'Unknown'),
                'To': edge.get('to', 'Unknown'),
                'Interface': edge.get('interface', 'N/A'),
                'Status': edge.get('status', 'Unknown').title(),
                'Bandwidth': edge.get('bandwidth', 'N/A'),
                'Type': edge.get('type', 'N/A')
            }
            connections_data.append(connection_data)
        
        df = pd.DataFrame(connections_data)
        st.dataframe(df, use_container_width=True)


def vulnerability_table(vulnerabilities: List[Dict[str, Any]], security_scanner=None):
    """Display vulnerability scan results table"""
    if not vulnerabilities:
        st.info("No vulnerabilities found")
        return
    
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'unknown')
        severity_color = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
        
        with st.container():
            st.write(f"{severity_color} **{vuln.get('name', 'Unknown Vulnerability')}**")
            st.caption(f"Severity: {severity.title()} | Device: {vuln.get('device', 'Unknown')}")
            
            if vuln.get('description'):
                st.write(vuln['description'])


def compliance_table(compliance_results: List[Dict[str, Any]]):
    """Display compliance check results table"""
    if not compliance_results:
        st.info("No compliance results available")
        return
    
    df = pd.DataFrame(compliance_results)
    
    # Style the dataframe
    def style_compliance_status(val):
        if val == 'passed':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'failed':
            return 'background-color: #f8d7da; color: #721c24'
        else:
            return 'background-color: #fff3cd; color: #856404'
    
    if 'status' in df.columns:
        styled_df = df.style.map(style_compliance_status, subset=['status'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


def config_template_table(templates: List[Dict[str, Any]], config_manager=None):
    """Display configuration templates table"""
    if not templates:
        st.info("No configuration templates found")
        return
    
    for template in templates:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"📄 **{template.get('name', 'Unknown Template')}**")
                st.caption(f"Type: {template.get('device_type', 'Unknown')} | {template.get('description', 'No description')}")
            
            with col2:
                if st.button("👁️ View", key=f"view_template_{template.get('id', 'unknown')}"):
                    st.code(template.get('content', 'No content'), language='bash')
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_template_{template.get('id', 'unknown')}"):
                    st.info("Template editing coming soon...")


def config_history_table(history: List[Dict[str, Any]]):
    """Display configuration history table"""
    if not history:
        st.info("No configuration history available")
        return
    
    df = pd.DataFrame(history)
    st.dataframe(df, use_container_width=True)


def monitoring_alerts_table(alerts: List[Dict[str, Any]], network_monitor=None):
    """Display monitoring alerts table"""
    if not alerts:
        st.success("No active alerts")
        return
    
    for alert in alerts:
        severity = alert.get('severity', 'unknown')
        severity_color = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"{severity_color} **{alert.get('title', 'Unknown Alert')}**")
                st.caption(f"Device: {alert.get('device', 'Unknown')} | {alert.get('description', 'No description')}")
            
            with col2:
                st.write(f"Status: {alert.get('status', 'unknown').title()}")
            
            with col3:
                if st.button("🔕 Acknowledge", key=f"ack_alert_{alert.get('id', 'unknown')}"):
                    st.success("Alert acknowledged")


def performance_metrics_table(metrics: List[Dict[str, Any]]):
    """Display performance metrics table"""
    if not metrics:
        st.info("No performance metrics available")
        return
    
    df = pd.DataFrame(metrics)
    st.dataframe(df, use_container_width=True)


def topology_table(devices: List[Dict[str, Any]], device_manager=None):
    """Display topology devices table"""
    if not devices:
        st.info("No devices in topology")
        return
    
    # Simplified device table for topology view
    for device in devices:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            device_type = device.get('device_type', 'unknown')
            type_emoji = {
                'router': '🔀',
                'switch': '🔗',
                'firewall': '🛡️',
                'server': '🖥️'
            }.get(device_type, '📱')
            
            st.write(f"{type_emoji} **{device.get('hostname', 'Unknown')}**")
            st.caption(f"IP: {device.get('ip_address', 'Unknown')}")
        
        with col2:
            status = device.get('status', 'unknown')
            status_color = {
                'online': '🟢',
                'offline': '🔴',
                'unknown': '⚪'
            }.get(status, '⚪')
            st.write(f"{status_color} {status.title()}")
        
        with col3:
            if st.button("ℹ️ Details", key=f"topology_details_{device.get('id', 'unknown')}"):
                st.info("Device details coming soon...")


def connection_table(connections: List[Dict[str, Any]]):
    """Display network connections table"""
    if not connections:
        st.info("No connections found")
        return
    
    df = pd.DataFrame(connections)
    st.dataframe(df, use_container_width=True)
