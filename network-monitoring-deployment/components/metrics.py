#!/usr/bin/env python3
"""
Reusable Metric Components for Network Monitoring Dashboard
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from config.styling import get_metric_card_style

def metric_card(title: str, value: str, subtitle: str = "", card_type: str = "default", icon: str = ""):
    """
    Create a reusable metric card component
    
    Args:
        title: Card title (e.g., "Total Devices")
        value: Main metric value (e.g., "12" or "85%")
        subtitle: Additional info (e.g., "5 online")
        card_type: Style type (default, success, warning, info, error)
        icon: Emoji icon for the card
    """
    card_class = get_metric_card_style(card_type)
    
    st.markdown(f"""
    <div class="{card_class}">
        <h3>{icon} {title}</h3>
        <h2>{value}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def device_metrics_row(devices: List[Dict[str, Any]], detailed: bool = False):
    """
    Create a row of device-related metrics
    
    Args:
        devices: List of device dictionaries
        detailed: Whether to show detailed metrics
    """
    if not detailed:
        # Simple 4-column layout
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
    else:
        # Detailed 6-column layout
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        cols = [col1, col2, col3, col4, col5, col6]
    
    total_devices = len(devices)
    online_devices = len([d for d in devices if d.get('status') == 'online'])
    offline_devices = total_devices - online_devices
    
    # Lab devices count
    lab_devices = len([d for d in devices if 'lab' in d.get('tags', '') or 
                      any(port in str(d.get('ip_address', '')) for port in ['2221', '2222', '2223'])])
    
    with cols[0]:
        metric_card(
            title="Total Devices", 
            value=str(total_devices),
            subtitle=f"{online_devices} online",
            card_type="info",
            icon="📱"
        )
    
    with cols[1]:
        metric_card(
            title="Online", 
            value=str(online_devices),
            subtitle="Active connections",
            card_type="success" if online_devices > 0 else "warning",
            icon="🟢"
        )
    
    with cols[2]:
        metric_card(
            title="Lab Devices", 
            value=str(lab_devices),
            subtitle="Ready for testing",
            card_type="info" if lab_devices > 0 else "warning",
            icon="🧪"
        )
    
    with cols[3]:
        uptime_percent = (online_devices / total_devices * 100) if total_devices > 0 else 0
        metric_card(
            title="Uptime", 
            value=f"{uptime_percent:.1f}%",
            subtitle="Network availability",
            card_type="success" if uptime_percent > 80 else "warning" if uptime_percent > 50 else "error",
            icon="⚡"
        )
    
    if detailed:
        with cols[4]:
            # Device type distribution
            routers = len([d for d in devices if d.get('device_type') == 'router'])
            metric_card(
                title="Routers", 
                value=str(routers),
                subtitle="Core devices",
                card_type="default",
                icon="🔀"
            )
        
        with cols[5]:
            switches = len([d for d in devices if d.get('device_type') == 'switch'])
            metric_card(
                title="Switches", 
                value=str(switches),
                subtitle="Access devices",
                card_type="default",
                icon="🔗"
            )

def security_metrics_simple(security_overview: Dict[str, Any]):
    """Create a simple row of security-related metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Vulnerabilities", security_overview.get('total_vulnerabilities', 0))
    with col2:
        st.metric("Critical", security_overview.get('critical_vulnerabilities', 0))
    with col3:
        st.metric("Security Score", f"{security_overview.get('security_score', 0)}%")
    with col4:
        st.metric("Last Scan", security_overview.get('last_scan', 'Never'))
    """
    Create a row of security-related metrics
    
    Args:
        security_overview: Security overview data from security scanner
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = security_overview.get('security_score', 0)
        score_change = f"+{score-80}%" if score > 80 else f"{score-80}%"
        metric_card(
            title="Security Score", 
            value=f"{score}%",
            subtitle=score_change,
            card_type="success" if score > 80 else "warning" if score > 60 else "error",
            icon="🛡️"
        )
    
    with col2:
        alerts = security_overview.get('total_alerts', 0)
        metric_card(
            title="Total Alerts", 
            value=str(alerts),
            subtitle="-1" if alerts < 5 else "+1",
            card_type="warning" if alerts > 0 else "success",
            icon="⚠️"
        )
    
    with col3:
        critical_alerts = security_overview.get('critical_alerts', 0)
        metric_card(
            title="Critical Alerts", 
            value=str(critical_alerts),
            subtitle="High priority",
            card_type="error" if critical_alerts > 0 else "success",
            icon="🚨"
        )
    
    with col4:
        open_ports = security_overview.get('open_ports', 0)
        metric_card(
            title="Open Ports", 
            value=str(open_ports),
            subtitle="Exposed services",
            card_type="warning" if open_ports > 10 else "info",
            icon="🚪"
        )

def automation_metrics_row(automation_history: List[Dict], available_playbooks: List[Dict]):
    """
    Create a row of automation-related metrics
    
    Args:
        automation_history: List of automation execution history
        available_playbooks: List of available playbooks
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            title="Playbooks Ready", 
            value=str(len(available_playbooks)),
            subtitle="Available for execution",
            card_type="info",
            icon="📚"
        )
    
    with col2:
        executions = len(automation_history)
        metric_card(
            title="Total Executions", 
            value=str(executions),
            subtitle="Automation runs",
            card_type="success" if executions > 0 else "info",
            icon="⚡"
        )
    
    with col3:
        # Success rate calculation
        if automation_history:
            successful = len([h for h in automation_history if h.get('status') in ['success', 'completed']])
            success_rate = (successful / len(automation_history) * 100)
        else:
            success_rate = 100
        
        metric_card(
            title="Success Rate", 
            value=f"{success_rate:.0f}%",
            subtitle=f"{successful if automation_history else 0} successful",
            card_type="success" if success_rate > 80 else "warning",
            icon="🎯"
        )
    
    with col4:
        # Recent activity
        recent_executions = len([h for h in automation_history[-5:] if automation_history])
        metric_card(
            title="Recent Activity", 
            value=str(recent_executions),
            subtitle="Last 5 executions",
            card_type="info",
            icon="📈"
        )

def monitoring_metrics_simple(current_metrics: Dict[str, Any]):
    """
    Create a row of monitoring-related metrics
    
    Args:
        current_metrics: Current monitoring metrics from network monitor
    """
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate averages from current metrics
    if current_metrics:
        avg_cpu = sum(m.get('cpu_usage', 0) for m in current_metrics.values()) / len(current_metrics)
        avg_memory = sum(m.get('memory_usage', 0) for m in current_metrics.values()) / len(current_metrics)
        avg_response = sum(m.get('ssh_response_time', 0) for m in current_metrics.values()) / len(current_metrics)
        active_devices = len([m for m in current_metrics.values() if m.get('status') == 'active'])
    else:
        avg_cpu = avg_memory = avg_response = active_devices = 0
    
    with col1:
        uptime_percent = (active_devices / len(current_metrics) * 100) if current_metrics else 0
        metric_card(
            title="Network Uptime", 
            value=f"{uptime_percent:.1f}%",
            subtitle=f"{active_devices}/{len(current_metrics)} devices active" if current_metrics else "No data",
            card_type="success" if uptime_percent > 80 else "warning",
            icon="🌐"
        )
    
    with col2:
        cpu_status = "Normal" if avg_cpu < 70 else "High" if avg_cpu < 90 else "Critical"
        metric_card(
            title="Average CPU", 
            value=f"{avg_cpu:.1f}%",
            subtitle=cpu_status,
            card_type="success" if avg_cpu < 70 else "warning" if avg_cpu < 90 else "error",
            icon="💻"
        )
    
    with col3:
        response_status = "Excellent" if avg_response < 100 else "Good" if avg_response < 500 else "Slow"
        metric_card(
            title="Avg Response", 
            value=f"{avg_response:.0f}ms",
            subtitle=response_status,
            card_type="success" if avg_response < 100 else "warning" if avg_response < 500 else "error",
            icon="⚡"
        )
    
    with col4:
        memory_status = "Normal" if avg_memory < 80 else "High" if avg_memory < 95 else "Critical"
        metric_card(
            title="Avg Memory", 
            value=f"{avg_memory:.1f}%",
            subtitle=memory_status,
            card_type="success" if avg_memory < 80 else "warning",
            icon="💾"
        )

def quick_stats_sidebar(devices: List[Dict], playbooks: List[Dict], automation_history: List[Dict]):
    """
    Create sidebar quick stats section
    
    Args:
        devices: List of devices
        playbooks: List of available playbooks  
        automation_history: Automation execution history
    """
    st.markdown("### 📊 Quick Stats")
    
    try:
        device_count = len(devices)
        online_devices = len([d for d in devices if d.get('status') == 'online'])
        st.metric("Devices", device_count, f"{online_devices} online")
    except:
        st.metric("Devices", "0", "Loading...")
    
    try:
        st.metric("Playbooks", len(playbooks), "Available")
    except:
        st.metric("Playbooks", "0", "Loading...")
    
    st.metric("Automation", "Ready", "Simplified Mode")


def security_metrics_row(security_data: Dict[str, Any]):
    """Create a row of security-related metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vulns = security_data.get('total_vulnerabilities', 0)
        st.metric("Vulnerabilities", total_vulns, delta_color="inverse")
    
    with col2:
        critical_vulns = security_data.get('critical_vulnerabilities', 0)
        st.metric("Critical", critical_vulns, delta_color="inverse")
    
    with col3:
        security_score = security_data.get('security_score', 0)
        st.metric("Security Score", f"{security_score}%")
    
    with col4:
        last_scan = security_data.get('last_scan', 'Never')
        st.metric("Last Scan", last_scan)


def config_metrics_row(config_data: Dict[str, Any]):
    """Create a row of configuration-related metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        backup_count = config_data.get('backup_count', 0)
        st.metric("Backups", backup_count)
    
    with col2:
        template_count = config_data.get('template_count', 0)
        st.metric("Templates", template_count)
    
    with col3:
        deploy_success = config_data.get('deployment_success_rate', 0)
        st.metric("Deploy Success", f"{deploy_success}%")
    
    with col4:
        last_backup = config_data.get('last_backup', 'Never')
        st.metric("Last Backup", last_backup)


def monitoring_metrics_row(monitoring_data: Dict[str, Any]):
    """Create a row of monitoring-related metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        monitored_devices = monitoring_data.get('monitored_devices', 0)
        st.metric("Monitored", monitored_devices)
    
    with col2:
        avg_response_time = monitoring_data.get('avg_response_time', 0)
        st.metric("Avg Response", f"{avg_response_time:.1f}ms")
    
    with col3:
        uptime_percent = monitoring_data.get('uptime_percent', 0)
        st.metric("Uptime", f"{uptime_percent:.1f}%")
    
    with col4:
        active_alerts = monitoring_data.get('active_alerts', 0)
        st.metric("Active Alerts", active_alerts, delta_color="inverse")


def topology_metrics_row(topology_data: Dict[str, Any]):
    """Create a row of topology-related metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = topology_data.get('metrics', {})
    
    with col1:
        total_nodes = metrics.get('total_nodes', 0)
        st.metric("Devices", total_nodes)
    
    with col2:
        total_edges = metrics.get('total_edges', 0)
        st.metric("Connections", total_edges)
    
    with col3:
        network_diameter = metrics.get('network_diameter', 0)
        st.metric("Diameter", network_diameter)
    
    with col4:
        avg_degree = metrics.get('average_degree', 0)
        st.metric("Avg Degree", f"{avg_degree:.1f}")
