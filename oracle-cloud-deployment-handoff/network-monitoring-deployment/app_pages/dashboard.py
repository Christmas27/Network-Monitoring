#!/usr/bin/env python3
"""
Dashboard Page - Network Monitoring Overview
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import logging

# Import our modular components
from components.metrics import (
    device_metrics_row, 
    monitoring_metrics_row, 
    security_metrics_row,
    automation_metrics_row
)
from utils.shared_utils import (
    PerformanceMonitor, 
    dashboard_cache, 
    format_timestamp,
    get_time_ago
)
from utils.data_processing import DataProcessor

logger = logging.getLogger(__name__)

class DashboardPage:
    """Main dashboard page with network overview"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the dashboard page"""
        # Page header
        st.markdown("# 🏠 Network Monitoring Dashboard")
        st.markdown("---")
        
        # Quick refresh button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                self._clear_cache()
                st.rerun()
        
        with col2:
            auto_refresh = st.checkbox("⚡ Auto-refresh", value=False)
        
        if auto_refresh:
            st.rerun()
        
        # Main metrics overview
        self._render_metrics_overview()
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_device_status_chart()
            self._render_performance_chart()
        
        with col2:
            self._render_security_overview()
            self._render_recent_activities()
        
        # System information
        self._render_system_status()
    
    def _render_metrics_overview(self):
        """Render main metrics overview"""
        st.markdown("### 📊 System Overview")
        
        # Get managers from session state
        device_manager = st.session_state.get('device_manager')
        network_monitor = st.session_state.get('network_monitor')
        security_scanner = st.session_state.get('security_scanner')
        
        # Device metrics
        if device_manager:
            devices = device_manager.get_all_devices()
            device_metrics_row(devices)
        else:
            st.warning("⚠️ Device manager not initialized")
        
        # Security metrics
        if security_scanner:
            try:
                # Get security alerts
                alerts = security_scanner.get_security_alerts()
                # Transform list to dict for metrics function
                security_data = {
                    'total_alerts': len(alerts),
                    'critical_alerts': len([a for a in alerts if a.get('severity') == 'critical']),
                    'high_alerts': len([a for a in alerts if a.get('severity') == 'high']),
                    'medium_alerts': len([a for a in alerts if a.get('severity') == 'medium']),
                    'low_alerts': len([a for a in alerts if a.get('severity') == 'low']),
                    'recent_alerts': alerts[:5] if alerts else []
                }
                security_metrics_row(security_data)
            except Exception as e:
                logger.error(f"❌ Error getting security metrics: {e}")
                st.error("Error loading security metrics")
        
        # Monitoring metrics
        if network_monitor:
            try:
                # Get recent monitoring data
                monitoring_list = self._get_monitoring_metrics()
                # Transform list to dict for metrics function
                if monitoring_list:
                    latest = monitoring_list[0] if monitoring_list else {}
                    monitoring_data = {
                        'total_devices': len(monitoring_list),
                        'avg_cpu_usage': sum(d.get('cpu_usage', 0) for d in monitoring_list) / len(monitoring_list) if monitoring_list else 0,
                        'avg_memory_usage': sum(d.get('memory_usage', 0) for d in monitoring_list) / len(monitoring_list) if monitoring_list else 0,
                        'avg_response_time': sum(d.get('response_time', 0) for d in monitoring_list) / len(monitoring_list) if monitoring_list else 0,
                        'uptime_percentage': latest.get('uptime', 0),
                        'last_update': latest.get('timestamp', datetime.now())
                    }
                else:
                    monitoring_data = {
                        'total_devices': 0,
                        'avg_cpu_usage': 0,
                        'avg_memory_usage': 0,
                        'avg_response_time': 0,
                        'uptime_percentage': 0,
                        'last_update': datetime.now()
                    }
                monitoring_metrics_row(monitoring_data)
            except Exception as e:
                logger.error(f"❌ Error getting monitoring metrics: {e}")
                st.error("Error loading monitoring metrics")
        
        # Automation metrics (if available)
        automation_data = self._get_automation_metrics()
        available_playbooks = st.session_state.get('cached_playbooks', [])
        automation_history = st.session_state.get('automation_history', [])
        automation_metrics_row(automation_history, available_playbooks)
    
    def _render_device_status_chart(self):
        """Render device status distribution chart"""
        st.markdown("#### 📱 Device Status Distribution")
        
        device_manager = st.session_state.get('device_manager')
        if not device_manager:
            st.info("No device data available")
            return
        
        try:
            devices = device_manager.get_all_devices()
            if not devices:
                st.info("No devices configured")
                return
            
            # Process device data
            df = self.data_processor.clean_device_data(devices)
            if df.empty:
                st.info("No device data to display")
                return
            
            # Count devices by status
            status_counts = df['status'].value_counts()
            
            # Create pie chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=status_counts.index,
                    values=status_counts.values,
                    hole=0.4,
                    marker_colors=['#28a745', '#dc3545', '#ffc107', '#6c757d']
                )
            ])
            
            fig.update_layout(
                title="Device Status Distribution",
                height=300,
                showlegend=True,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering device status chart: {e}")
            st.error("Error loading device status chart")
    
    def _render_performance_chart(self):
        """Render system performance chart"""
        st.markdown("#### ⚡ System Performance")
        
        try:
            # Get cached performance data or fetch new
            cache_key = "performance_data"
            perf_data = dashboard_cache.get(cache_key)
            
            if not perf_data:
                perf_data = []
                # Generate sample performance data for last 24 hours
                for i in range(24):
                    timestamp = datetime.now() - timedelta(hours=23-i)
                    metrics = self.performance_monitor.get_system_metrics()
                    if metrics:
                        metrics['timestamp'] = timestamp
                        perf_data.append(metrics)
                
                dashboard_cache.set(cache_key, perf_data, ttl=300)  # 5 min cache
            
            if not perf_data:
                st.info("No performance data available")
                return
            
            # Create DataFrame
            df = pd.DataFrame(perf_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Extract CPU and memory data
            cpu_data = [item['cpu']['percent'] for item in perf_data if 'cpu' in item]
            memory_data = [item['memory']['percent'] for item in perf_data if 'memory' in item]
            timestamps = df['timestamp']
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=cpu_data,
                mode='lines',
                name='CPU Usage (%)',
                line=dict(color='#007bff')
            ))
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=memory_data,
                mode='lines',
                name='Memory Usage (%)',
                line=dict(color='#28a745')
            ))
            
            fig.update_layout(
                title="System Performance (24h)",
                xaxis_title="Time",
                yaxis_title="Usage (%)",
                height=300,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering performance chart: {e}")
            st.error("Error loading performance chart")
    
    def _render_security_overview(self):
        """Render security overview"""
        st.markdown("#### 🛡️ Security Overview")
        
        security_scanner = st.session_state.get('security_scanner')
        if not security_scanner:
            st.info("Security scanner not available")
            return
        
        try:
            # Get security alerts
            alerts = security_scanner.get_security_alerts()
            
            if not alerts:
                st.success("✅ No security alerts")
                return
            
            # Process alerts data
            df = self.data_processor.process_security_alerts(alerts)
            
            # Count alerts by severity
            severity_counts = df['severity'].value_counts()
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            colors = {
                'critical': '#dc3545',
                'high': '#fd7e14', 
                'medium': '#ffc107',
                'low': '#20c997',
                'info': '#17a2b8'
            }
            
            for severity in severity_counts.index:
                fig.add_trace(go.Bar(
                    y=[severity],
                    x=[severity_counts[severity]],
                    orientation='h',
                    name=severity.title(),
                    marker_color=colors.get(severity, '#6c757d')
                ))
            
            fig.update_layout(
                title="Security Alerts by Severity",
                xaxis_title="Number of Alerts",
                height=300,
                showlegend=False,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent critical alerts
            critical_alerts = df[df['severity'] == 'critical'].head(3)
            if not critical_alerts.empty:
                st.markdown("**🚨 Critical Alerts:**")
                for _, alert in critical_alerts.iterrows():
                    st.error(f"**{alert['device_id']}**: {alert['message']}")
            
        except Exception as e:
            logger.error(f"❌ Error rendering security overview: {e}")
            st.error("Error loading security overview")
    
    def _render_recent_activities(self):
        """Render recent activities"""
        st.markdown("#### 📝 Recent Activities")
        
        try:
            # Get recent activities from various sources
            activities = []
            
            # Device activities
            device_manager = st.session_state.get('device_manager')
            if device_manager:
                devices = device_manager.get_all_devices()
                for device in devices[-5:]:  # Last 5 devices
                    activities.append({
                        'timestamp': device.get('updated_at', datetime.now()),
                        'type': 'device',
                        'message': f"Device {device['hostname']} updated",
                        'icon': '📱'
                    })
            
            # Security activities
            security_scanner = st.session_state.get('security_scanner')
            if security_scanner:
                alerts = security_scanner.get_security_alerts()
                for alert in alerts[-3:]:  # Last 3 alerts
                    activities.append({
                        'timestamp': alert.get('timestamp', datetime.now()),
                        'type': 'security',
                        'message': f"Security alert on {alert['device_id']}",
                        'icon': '🛡️'
                    })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            if not activities:
                st.info("No recent activities")
                return
            
            # Display activities
            for activity in activities[:10]:  # Show top 10
                timestamp = activity['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                time_ago = get_time_ago(timestamp)
                
                st.markdown(f"""
                <div style="padding: 0.5rem; border-left: 3px solid #007bff; margin: 0.5rem 0; background: #f8f9fa;">
                    {activity['icon']} **{activity['message']}**<br>
                    <small style="color: #6c757d;">{time_ago}</small>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering recent activities: {e}")
            st.error("Error loading recent activities")
    
    def _render_system_status(self):
        """Render system status information"""
        st.markdown("---")
        st.markdown("### 🖥️ System Status")
        
        try:
            # Get system metrics
            metrics = self.performance_monitor.get_system_metrics()
            
            if not metrics:
                st.error("Unable to get system metrics")
                return
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cpu_percent = metrics['cpu']['percent']
                cpu_color = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 85 else "🔴"
                st.metric(
                    label=f"{cpu_color} CPU Usage",
                    value=f"{cpu_percent:.1f}%",
                    delta=None
                )
            
            with col2:
                memory_percent = metrics['memory']['percent']
                memory_color = "🟢" if memory_percent < 80 else "🟡" if memory_percent < 90 else "🔴"
                st.metric(
                    label=f"{memory_color} Memory Usage",
                    value=f"{memory_percent:.1f}%",
                    delta=f"{metrics['memory']['used_gb']:.1f}GB used"
                )
            
            with col3:
                disk_percent = metrics['disk']['percent']
                disk_color = "🟢" if disk_percent < 80 else "🟡" if disk_percent < 90 else "🔴"
                st.metric(
                    label=f"{disk_color} Disk Usage",
                    value=f"{disk_percent:.1f}%",
                    delta=f"{metrics['disk']['free_gb']:.1f}GB free"
                )
            
            with col4:
                st.metric(
                    label="🌐 Network I/O",
                    value=f"{metrics['network']['bytes_sent'] / (1024**2):.1f}MB sent",
                    delta=f"{metrics['network']['bytes_recv'] / (1024**2):.1f}MB received"
                )
            
            # System information
            with st.expander("📋 Detailed System Information"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Hardware:**")
                    st.write(f"• CPU Cores: {metrics['cpu']['count']}")
                    st.write(f"• Total Memory: {metrics['memory']['total_gb']:.1f} GB")
                    st.write(f"• Total Disk: {metrics['disk']['total_gb']:.1f} GB")
                
                with col2:
                    st.markdown("**Network:**")
                    st.write(f"• Packets Sent: {metrics['network']['packets_sent']:,}")
                    st.write(f"• Packets Received: {metrics['network']['packets_recv']:,}")
                    st.write(f"• Last Updated: {format_timestamp()}")
            
        except Exception as e:
            logger.error(f"❌ Error rendering system status: {e}")
            st.error("Error loading system status")
    
    def _get_monitoring_metrics(self) -> List[Dict[str, Any]]:
        """Get monitoring metrics data"""
        try:
            network_monitor = st.session_state.get('network_monitor')
            if not network_monitor:
                return []
            
            # This would be implemented based on your network_monitor structure
            # For now, return sample data
            return [
                {
                    'device_id': 'sample_device',
                    'cpu_usage': 45.2,
                    'memory_usage': 67.8,
                    'response_time': 125,
                    'uptime': 99.5,
                    'timestamp': datetime.now()
                }
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring metrics: {e}")
            return []
    
    def _get_automation_metrics(self) -> Dict[str, Any]:
        """Get automation metrics data"""
        try:
            # Get automation history from session state
            automation_history = st.session_state.get('automation_history', [])
            
            total_executions = len(automation_history)
            successful = len([h for h in automation_history if h.get('status') == 'success'])
            failed = total_executions - successful
            
            return {
                'total_executions': total_executions,
                'successful_executions': successful,
                'failed_executions': failed,
                'success_rate': (successful / total_executions * 100) if total_executions > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting automation metrics: {e}")
            return {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0
            }
    
    def _clear_cache(self):
        """Clear dashboard cache"""
        dashboard_cache.clear()
        st.success("🔄 Cache cleared and data refreshed")

def render_dashboard_page():
    """Main function to render dashboard page"""
    dashboard = DashboardPage()
    dashboard.render()
