#!/usr/bin/env python3
"""
Monitoring Page - Real-time Network Performance and Availability Monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import our modular components
from components.forms import device_selector
from components.tables import monitoring_alerts_table, performance_metrics_table
from components.metrics import monitoring_metrics_row
from utils.shared_utils import (
    PerformanceMonitor,
    notification_manager,
    show_loading_spinner
)
from utils.data_processing import DataProcessor

logger = logging.getLogger(__name__)

class MonitoringPage:
    """Real-time network monitoring and performance analysis page"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the monitoring page"""
        # Page header
        st.markdown("# 🔍 Network Monitoring")
        st.markdown("Real-time network performance monitoring, alerting, and historical analysis")
        st.markdown("---")
        
        # Get managers from session state
        network_monitor = st.session_state.get('network_monitor')
        device_manager = st.session_state.get('device_manager')
        
        if not network_monitor:
            st.error("❌ Network monitor not initialized")
            return
        
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Monitoring tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Real-time Dashboard", 
            "📈 Performance Analysis", 
            "🚨 Alerts & Thresholds",
            "📋 Reports"
        ])
        
        with tab1:
            self._render_realtime_dashboard(network_monitor, device_manager)
        
        with tab2:
            self._render_performance_analysis(network_monitor, device_manager)
        
        with tab3:
            self._render_alerts_thresholds(network_monitor, device_manager)
        
        with tab4:
            self._render_reports(network_monitor, device_manager)
    
    def _render_realtime_dashboard(self, network_monitor, device_manager):
        """Render real-time monitoring dashboard"""
        st.markdown("### 📊 Real-time Network Status")
        
        # Auto-refresh controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
        
        with col2:
            refresh_interval = st.selectbox("Interval:", ["5s", "15s", "30s", "1m"], index=2)
        
        with col3:
            if st.button("🔄 Refresh Now", type="primary"):
                st.rerun()
        
        with col4:
            # Show last update time
            current_time = datetime.now().strftime('%H:%M:%S')
            st.caption(f"Last Update: {current_time}")
        
        # Network overview metrics
        try:
            devices = device_manager.get_all_devices()
            monitoring_data = self._get_monitoring_data(network_monitor, devices)
            
            # Overview metrics
            monitoring_metrics_row(monitoring_data)
            
            # Network topology status
            st.markdown("### 🌐 Network Status Map")
            self._render_network_status_map(monitoring_data)
            
            # Real-time metrics charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Response Times")
                self._render_response_time_chart(monitoring_data)
            
            with col2:
                st.markdown("### 📊 Availability Status")
                self._render_availability_chart(monitoring_data)
            
            # Device status table
            st.markdown("### 📋 Device Status Details")
            if monitoring_data:
                df = pd.DataFrame(monitoring_data)
                
                # Color-code status
                def style_status(val):
                    if val == 'online':
                        return 'background-color: #d4edda; color: #155724'
                    elif val == 'offline':
                        return 'background-color: #f8d7da; color: #721c24'
                    else:
                        return 'background-color: #fff3cd; color: #856404'
                
                styled_df = df.style.applymap(style_status, subset=['status'])
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.info("No monitoring data available")
            
        except Exception as e:
            logger.error(f"❌ Error loading monitoring dashboard: {e}")
            st.error("Error loading monitoring dashboard")
        
        # Auto-refresh implementation
        if auto_refresh:
            import time
            refresh_seconds = {"5s": 5, "15s": 15, "30s": 30, "1m": 60}[refresh_interval]
            time.sleep(refresh_seconds)
            st.rerun()
    
    def _render_performance_analysis(self, network_monitor, device_manager):
        """Render performance analysis interface"""
        st.markdown("### 📈 Performance Analysis")
        st.markdown("Historical performance data and trend analysis")
        
        # Analysis controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            time_range = st.selectbox(
                "Time Range:",
                ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
            )
        
        with col2:
            metric_type = st.selectbox(
                "Metric:",
                ["Response Time", "Packet Loss", "Uptime", "Bandwidth", "CPU Usage", "Memory Usage"]
            )
        
        with col3:
            devices = device_manager.get_all_devices()
            if devices:
                device_filter = st.selectbox(
                    "Device:",
                    ["All Devices"] + [d['hostname'] for d in devices]
                )
            else:
                device_filter = "All Devices"
        
        with col4:
            if st.button("📊 Generate Analysis", type="primary"):
                self._generate_performance_analysis(network_monitor, time_range, metric_type, device_filter)
        
        # Performance trends
        st.markdown("### 📈 Performance Trends")
        self._render_performance_trends(network_monitor, time_range, metric_type, device_filter)
        
        # Statistical analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Statistics Summary")
            self._render_performance_statistics(network_monitor, metric_type, device_filter)
        
        with col2:
            st.markdown("### 🎯 SLA Compliance")
            self._render_sla_compliance(network_monitor, device_filter)
        
        # Anomaly detection
        st.markdown("### 🔍 Anomaly Detection")
        self._render_anomaly_detection(network_monitor, metric_type, device_filter)
    
    def _render_alerts_thresholds(self, network_monitor, device_manager):
        """Render alerts and threshold management"""
        st.markdown("### 🚨 Alerts & Thresholds")
        st.markdown("Configure monitoring thresholds and manage alerts")
        
        # Alert controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ New Alert Rule", type="primary", use_container_width=True):
                st.session_state.show_alert_editor = True
        
        with col2:
            if st.button("🔄 Refresh Alerts", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("🔕 Mute All", use_container_width=True):
                self._mute_all_alerts(network_monitor)
        
        with col4:
            if st.button("📤 Export Rules", use_container_width=True):
                self._export_alert_rules(network_monitor)
        
        # Alert rule editor
        if st.session_state.get('show_alert_editor', False):
            self._render_alert_rule_editor(network_monitor, device_manager)
        
        # Active alerts
        st.markdown("### 🚨 Active Alerts")
        try:
            active_alerts = network_monitor.get_active_alerts()
            
            if active_alerts:
                # Alert summary
                alert_counts = self._count_alerts_by_severity(active_alerts)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Critical", alert_counts.get('critical', 0), delta_color="inverse")
                with col2:
                    st.metric("High", alert_counts.get('high', 0), delta_color="inverse")
                with col3:
                    st.metric("Medium", alert_counts.get('medium', 0))
                with col4:
                    st.metric("Low", alert_counts.get('low', 0))
                
                # Alert table
                monitoring_alerts_table(active_alerts, network_monitor)
            else:
                st.success("🎉 No active alerts - All systems normal!")
                
        except Exception as e:
            logger.error(f"❌ Error loading alerts: {e}")
            st.error("Error loading alerts")
        
        # Threshold configuration
        st.markdown("### ⚙️ Threshold Configuration")
        self._render_threshold_configuration(network_monitor, device_manager)
        
        # Alert history
        st.markdown("### 📋 Alert History")
        self._render_alert_history(network_monitor)
    
    def _render_reports(self, network_monitor, device_manager):
        """Render monitoring reports"""
        st.markdown("### 📋 Monitoring Reports")
        st.markdown("Generate and export network monitoring reports")
        
        # Report configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            report_type = st.selectbox(
                "Report Type:",
                ["Availability Report", "Performance Summary", "SLA Report", "Trend Analysis", "Custom Report"]
            )
            
            time_period = st.selectbox(
                "Time Period:",
                ["Daily", "Weekly", "Monthly", "Quarterly", "Custom Range"]
            )
            
            if time_period == "Custom Range":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input("Start Date:")
                with col_end:
                    end_date = st.date_input("End Date:")
        
        with col2:
            st.markdown("**Report Options:**")
            include_charts = st.checkbox("Include Charts", value=True)
            include_details = st.checkbox("Include Device Details", value=True)
            include_alerts = st.checkbox("Include Alert Summary", value=True)
            
            report_format = st.selectbox("Format:", ["PDF", "HTML", "CSV", "JSON"])
        
        # Generate report
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Report", type="primary", use_container_width=True):
                self._generate_monitoring_report(
                    network_monitor, report_type, time_period, 
                    include_charts, include_details, include_alerts, report_format
                )
        
        with col2:
            if st.button("👁️ Preview Report", use_container_width=True):
                self._preview_monitoring_report(network_monitor, report_type, time_period)
        
        with col3:
            if st.button("📅 Schedule Report", use_container_width=True):
                self._schedule_monitoring_report()
        
        # Report templates
        st.markdown("### 📄 Report Templates")
        self._render_report_templates(network_monitor)
        
        # Scheduled reports
        st.markdown("### 📅 Scheduled Reports")
        self._render_scheduled_reports(network_monitor)
    
    def _get_monitoring_data(self, network_monitor, devices):
        """Get current monitoring data for all devices"""
        try:
            monitoring_data = []
            
            for device in devices:
                # Get latest monitoring data
                status_data = network_monitor.get_device_status(device['id'])
                
                device_data = {
                    'hostname': device['hostname'],
                    'ip_address': device['ip_address'],
                    'device_type': device['device_type'],
                    'status': status_data.get('status', 'unknown'),
                    'response_time': status_data.get('response_time', 0),
                    'packet_loss': status_data.get('packet_loss', 0),
                    'uptime': status_data.get('uptime', 'Unknown'),
                    'last_seen': status_data.get('last_seen', 'Never')
                }
                monitoring_data.append(device_data)
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring data: {e}")
            return []
    
    def _render_network_status_map(self, monitoring_data):
        """Render network status visualization"""
        try:
            if not monitoring_data:
                st.info("No monitoring data available for network map")
                return
            
            # Create status summary
            status_counts = {}
            for device in monitoring_data:
                status = device['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Create pie chart
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Network Device Status Distribution",
                color_discrete_map={
                    'online': '#28a745',
                    'offline': '#dc3545',
                    'warning': '#ffc107',
                    'unknown': '#6c757d'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering network status map: {e}")
            st.error("Error rendering network status map")
    
    def _render_response_time_chart(self, monitoring_data):
        """Render response time chart"""
        try:
            if not monitoring_data:
                st.info("No response time data available")
                return
            
            # Create response time chart
            hostnames = [d['hostname'] for d in monitoring_data]
            response_times = [d['response_time'] for d in monitoring_data]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=hostnames,
                    y=response_times,
                    marker_color=['red' if rt > 100 else 'orange' if rt > 50 else 'green' for rt in response_times]
                )
            ])
            
            fig.update_layout(
                title="Device Response Times (ms)",
                xaxis_title="Device",
                yaxis_title="Response Time (ms)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering response time chart: {e}")
            st.error("Error rendering response time chart")
    
    def _render_availability_chart(self, monitoring_data):
        """Render availability status chart"""
        try:
            if not monitoring_data:
                st.info("No availability data available")
                return
            
            # Calculate availability percentages (simulated)
            availability_data = []
            for device in monitoring_data:
                # Simulate availability percentage based on status
                if device['status'] == 'online':
                    availability = np.random.uniform(95, 100)
                elif device['status'] == 'warning':
                    availability = np.random.uniform(85, 95)
                else:
                    availability = np.random.uniform(0, 85)
                
                availability_data.append({
                    'hostname': device['hostname'],
                    'availability': availability,
                    'status': device['status']
                })
            
            # Create availability chart
            fig = go.Figure()
            
            for status in ['online', 'warning', 'offline']:
                status_data = [d for d in availability_data if d['status'] == status]
                if status_data:
                    fig.add_trace(go.Bar(
                        x=[d['hostname'] for d in status_data],
                        y=[d['availability'] for d in status_data],
                        name=status.title(),
                        marker_color={'online': 'green', 'warning': 'orange', 'offline': 'red'}[status]
                    ))
            
            fig.update_layout(
                title="Device Availability (%)",
                xaxis_title="Device",
                yaxis_title="Availability (%)",
                yaxis=dict(range=[0, 100]),
                height=400,
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering availability chart: {e}")
            st.error("Error rendering availability chart")
    
    def _render_performance_trends(self, network_monitor, time_range, metric_type, device_filter):
        """Render performance trend analysis"""
        try:
            # Generate sample trend data
            time_periods = {
                "Last Hour": 60,
                "Last 6 Hours": 360,
                "Last 24 Hours": 1440,
                "Last 7 Days": 10080,
                "Last 30 Days": 43200
            }
            
            minutes = time_periods.get(time_range, 1440)
            intervals = min(100, minutes // 5)  # Max 100 data points
            
            # Generate time series
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes)
            time_range_data = pd.date_range(start=start_time, end=end_time, periods=intervals)
            
            # Generate sample data based on metric type
            if metric_type == "Response Time":
                values = np.random.normal(50, 15, intervals)  # Average 50ms with variance
                values = np.clip(values, 0, None)  # No negative response times
                unit = "ms"
            elif metric_type == "Packet Loss":
                values = np.random.exponential(0.5, intervals)  # Exponential distribution
                values = np.clip(values, 0, 100)  # 0-100%
                unit = "%"
            elif metric_type == "Uptime":
                values = np.random.uniform(95, 100, intervals)  # High uptime
                unit = "%"
            else:
                values = np.random.normal(50, 20, intervals)
                unit = "%"
            
            # Create trend chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=time_range_data,
                y=values,
                mode='lines+markers',
                name=f"{metric_type} ({device_filter})",
                line=dict(width=2)
            ))
            
            fig.update_layout(
                title=f"{metric_type} Trend - {time_range}",
                xaxis_title="Time",
                yaxis_title=f"{metric_type} ({unit})",
                height=400,
                hovermode='x'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering performance trends: {e}")
            st.error("Error rendering performance trends")
    
    def _render_performance_statistics(self, network_monitor, metric_type, device_filter):
        """Render performance statistics summary"""
        try:
            # Generate sample statistics
            stats = {
                'Average': np.random.uniform(45, 55),
                'Minimum': np.random.uniform(10, 30),
                'Maximum': np.random.uniform(80, 120),
                'Std Dev': np.random.uniform(5, 15),
                '95th Percentile': np.random.uniform(70, 90)
            }
            
            for stat_name, value in stats.items():
                unit = "ms" if metric_type == "Response Time" else "%"
                st.metric(stat_name, f"{value:.1f} {unit}")
                
        except Exception as e:
            st.info("Performance statistics not available")
    
    def _render_sla_compliance(self, network_monitor, device_filter):
        """Render SLA compliance metrics"""
        try:
            # Sample SLA data
            sla_targets = {
                'Availability': {'target': 99.9, 'current': 99.5},
                'Response Time': {'target': 100, 'current': 85},
                'Packet Loss': {'target': 1.0, 'current': 0.3}
            }
            
            for sla_name, data in sla_targets.items():
                target = data['target']
                current = data['current']
                compliance = (current / target * 100) if target > 0 else 100
                
                delta = current - target
                delta_color = "normal" if delta <= 0 else "inverse"
                
                st.metric(
                    f"{sla_name} SLA",
                    f"{compliance:.1f}%",
                    delta=f"{delta:+.1f}",
                    delta_color=delta_color
                )
                
        except Exception as e:
            st.info("SLA compliance data not available")
    
    def _render_anomaly_detection(self, network_monitor, metric_type, device_filter):
        """Render anomaly detection results"""
        try:
            # Sample anomaly data
            anomalies = [
                {
                    'timestamp': datetime.now() - timedelta(hours=2),
                    'device': 'Router-01',
                    'metric': 'Response Time',
                    'value': 250,
                    'threshold': 100,
                    'severity': 'High'
                },
                {
                    'timestamp': datetime.now() - timedelta(minutes=30),
                    'device': 'Switch-02',
                    'metric': 'Packet Loss',
                    'value': 5.2,
                    'threshold': 1.0,
                    'severity': 'Critical'
                }
            ]
            
            if anomalies:
                st.markdown("**Recent Anomalies Detected:**")
                for anomaly in anomalies:
                    severity_color = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }.get(anomaly['severity'], '⚪')
                    
                    st.write(f"{severity_color} **{anomaly['device']}** - {anomaly['metric']}: {anomaly['value']} (threshold: {anomaly['threshold']})")
                    st.caption(f"Detected: {anomaly['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            else:
                st.success("No anomalies detected in the selected time range")
                
        except Exception as e:
            st.info("Anomaly detection not available")
    
    def _render_alert_rule_editor(self, network_monitor, device_manager):
        """Render alert rule editor"""
        st.markdown("### ➕ Create Alert Rule")
        
        with st.form("alert_rule_editor"):
            col1, col2 = st.columns(2)
            
            with col1:
                rule_name = st.text_input("Rule Name:", placeholder="High Response Time Alert")
                metric = st.selectbox("Metric:", ["Response Time", "Packet Loss", "Uptime", "CPU Usage", "Memory Usage"])
                condition = st.selectbox("Condition:", ["Greater than", "Less than", "Equal to", "Not equal to"])
                threshold = st.number_input("Threshold:", min_value=0.0, step=0.1)
            
            with col2:
                severity = st.selectbox("Severity:", ["Critical", "High", "Medium", "Low"])
                notification_method = st.multiselect("Notifications:", ["Email", "SMS", "Webhook", "Dashboard"])
                
                devices = device_manager.get_all_devices()
                device_scope = st.selectbox(
                    "Apply to:",
                    ["All Devices"] + [d['hostname'] for d in devices] if devices else ["All Devices"]
                )
            
            description = st.text_area("Description:", placeholder="Alert description...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Rule", type="primary"):
                    self._save_alert_rule(network_monitor, rule_name, metric, condition, 
                                        threshold, severity, notification_method, device_scope, description)
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_alert_editor = False
                    st.rerun()
    
    def _render_threshold_configuration(self, network_monitor, device_manager):
        """Render threshold configuration interface"""
        try:
            devices = device_manager.get_all_devices()
            
            if devices:
                selected_device = device_selector(devices, key="threshold_device", label="Configure thresholds for:")
                
                if selected_device:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Performance Thresholds:**")
                        response_time_threshold = st.number_input("Response Time (ms):", value=100, min_value=1)
                        packet_loss_threshold = st.number_input("Packet Loss (%):", value=1.0, min_value=0.0, step=0.1)
                        
                    with col2:
                        st.markdown("**Availability Thresholds:**")
                        uptime_threshold = st.number_input("Minimum Uptime (%):", value=99.0, min_value=0.0, max_value=100.0)
                        check_interval = st.number_input("Check Interval (seconds):", value=60, min_value=10)
                    
                    if st.button("💾 Save Thresholds"):
                        self._save_device_thresholds(
                            network_monitor, selected_device['id'],
                            response_time_threshold, packet_loss_threshold, uptime_threshold, check_interval
                        )
            else:
                st.info("No devices available for threshold configuration")
                
        except Exception as e:
            logger.error(f"❌ Error rendering threshold configuration: {e}")
            st.error("Error loading threshold configuration")
    
    def _render_alert_history(self, network_monitor):
        """Render alert history"""
        try:
            # Sample alert history
            history = [
                {
                    'timestamp': datetime.now() - timedelta(hours=1),
                    'device': 'Router-01',
                    'alert': 'High Response Time',
                    'severity': 'High',
                    'status': 'Resolved',
                    'duration': '15 minutes'
                },
                {
                    'timestamp': datetime.now() - timedelta(hours=3),
                    'device': 'Switch-02',
                    'alert': 'Device Offline',
                    'severity': 'Critical',
                    'status': 'Resolved',
                    'duration': '5 minutes'
                }
            ]
            
            if history:
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No alert history available")
                
        except Exception as e:
            st.info("Alert history not available")
    
    def _count_alerts_by_severity(self, alerts):
        """Count alerts by severity level"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for alert in alerts:
            severity = alert.get('severity', 'low').lower()
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _save_alert_rule(self, network_monitor, name, metric, condition, threshold, 
                        severity, notifications, device_scope, description):
        """Save new alert rule"""
        try:
            rule_data = {
                'name': name,
                'metric': metric,
                'condition': condition,
                'threshold': threshold,
                'severity': severity,
                'notifications': notifications,
                'device_scope': device_scope,
                'description': description,
                'created_at': datetime.now()
            }
            
            network_monitor.save_alert_rule(rule_data)
            st.success(f"✅ Alert rule '{name}' created successfully")
            st.session_state.show_alert_editor = False
            
            notification_manager.add_notification(
                f"Alert rule '{name}' created",
                "success"
            )
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"❌ Error saving alert rule: {e}")
            st.error(f"Error saving alert rule: {e}")
    
    def _save_device_thresholds(self, network_monitor, device_id, response_time, 
                              packet_loss, uptime, check_interval):
        """Save device monitoring thresholds"""
        try:
            thresholds = {
                'response_time': response_time,
                'packet_loss': packet_loss,
                'uptime': uptime,
                'check_interval': check_interval
            }
            
            network_monitor.save_device_thresholds(device_id, thresholds)
            st.success("✅ Thresholds saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Error saving thresholds: {e}")
            st.error(f"Error saving thresholds: {e}")
    
    def _generate_performance_analysis(self, network_monitor, time_range, metric_type, device_filter):
        """Generate performance analysis report"""
        try:
            with show_loading_spinner("Generating performance analysis..."):
                # Simulate analysis generation
                import time
                time.sleep(2)
            
            st.success("✅ Performance analysis generated successfully")
            
            # Show sample analysis results
            st.markdown("### 📊 Analysis Results")
            st.info(f"Analysis for {metric_type} over {time_range} for {device_filter}")
            
        except Exception as e:
            logger.error(f"❌ Error generating performance analysis: {e}")
            st.error("Error generating performance analysis")
    
    def _mute_all_alerts(self, network_monitor):
        """Mute all active alerts"""
        try:
            network_monitor.mute_all_alerts()
            st.success("✅ All alerts muted for 1 hour")
            
        except Exception as e:
            logger.error(f"❌ Error muting alerts: {e}")
            st.error("Error muting alerts")
    
    def _export_alert_rules(self, network_monitor):
        """Export alert rules configuration"""
        try:
            rules = network_monitor.get_alert_rules()
            
            if rules:
                import json
                rules_json = json.dumps(rules, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download Alert Rules",
                    data=rules_json,
                    file_name=f"alert_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No alert rules available for export")
                
        except Exception as e:
            logger.error(f"❌ Error exporting alert rules: {e}")
            st.error("Error exporting alert rules")
    
    def _generate_monitoring_report(self, network_monitor, report_type, time_period, 
                                  include_charts, include_details, include_alerts, report_format):
        """Generate monitoring report"""
        try:
            with show_loading_spinner(f"Generating {report_type}..."):
                # Simulate report generation
                import time
                time.sleep(3)
            
            st.success(f"✅ {report_type} generated successfully")
            
            # Provide download button
            sample_data = f"Sample {report_type} data for {time_period}"
            st.download_button(
                label=f"📥 Download {report_type}",
                data=sample_data,
                file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                mime="application/octet-stream"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            st.error("Error generating monitoring report")
    
    def _preview_monitoring_report(self, network_monitor, report_type, time_period):
        """Preview monitoring report"""
        st.markdown(f"### 👁️ {report_type} Preview")
        st.info(f"Report preview for {time_period}")
        
        # Sample report content
        st.markdown("""
        **Executive Summary:**
        - Network availability: 99.5%
        - Average response time: 45ms
        - Total alerts: 12 (2 critical, 5 high, 5 medium)
        
        **Key Findings:**
        - Router-01 experienced intermittent connectivity issues
        - Switch-02 performance improved after maintenance
        - Overall network performance within SLA targets
        """)
    
    def _schedule_monitoring_report(self):
        """Schedule automated monitoring reports"""
        st.info("🚧 Scheduled reporting feature coming soon...")
        
        with st.expander("Report Schedule Configuration"):
            frequency = st.selectbox("Frequency:", ["Daily", "Weekly", "Monthly"])
            recipients = st.text_input("Email Recipients:", placeholder="admin@company.com, ops@company.com")
            report_types = st.multiselect("Report Types:", ["Availability", "Performance", "SLA", "Alerts"])
            
            if st.button("Save Schedule"):
                st.success("Report schedule saved!")
    
    def _render_report_templates(self, network_monitor):
        """Render report templates management"""
        templates = [
            "Executive Summary Report",
            "Technical Performance Report", 
            "SLA Compliance Report",
            "Incident Summary Report"
        ]
        
        for template in templates:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"📄 {template}")
            
            with col2:
                if st.button("👁️ Preview", key=f"preview_{template}"):
                    st.info(f"Preview of {template}")
            
            with col3:
                if st.button("📊 Generate", key=f"generate_{template}"):
                    st.success(f"{template} queued for generation")
    
    def _render_scheduled_reports(self, network_monitor):
        """Render scheduled reports list"""
        scheduled = [
            {"name": "Daily Availability Report", "frequency": "Daily", "next_run": "Tomorrow 06:00"},
            {"name": "Weekly SLA Report", "frequency": "Weekly", "next_run": "Monday 08:00"}
        ]
        
        if scheduled:
            df = pd.DataFrame(scheduled)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No scheduled reports configured")


def render_monitoring_page():
    """Main function to render monitoring page"""
    monitoring_page = MonitoringPage()
    monitoring_page.render()
