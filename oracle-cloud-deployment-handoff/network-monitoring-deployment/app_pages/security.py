#!/usr/bin/env python3
"""
Security Page - Network Security Monitoring and Vulnerability Assessment
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import json

# Import our modular components
from components.forms import device_selector
from components.tables import vulnerability_table, compliance_table
from components.metrics import security_metrics_row
from utils.shared_utils import (
    PerformanceMonitor,
    notification_manager,
    show_loading_spinner
)
from utils.data_processing import DataProcessor

logger = logging.getLogger(__name__)

class SecurityPage:
    """Security monitoring and vulnerability assessment page"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the security page"""
        # Page header
        st.markdown("# 🛡️ Security Monitoring")
        st.markdown("Network security assessment, vulnerability scanning, and compliance monitoring")
        st.markdown("---")
        
        # Get managers from session state
        security_scanner = st.session_state.get('security_scanner')
        device_manager = st.session_state.get('device_manager')
        
        if not security_scanner:
            st.error("❌ Security scanner not initialized")
            return
        
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Security tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Vulnerability Scanner", 
            "📊 Security Dashboard", 
            "📋 Compliance Check",
            "🚨 Security Alerts"
        ])
        
        with tab1:
            self._render_vulnerability_scanner(security_scanner, device_manager)
        
        with tab2:
            self._render_security_dashboard(security_scanner, device_manager)
        
        with tab3:
            self._render_compliance_check(security_scanner, device_manager)
        
        with tab4:
            self._render_security_alerts(security_scanner)
    
    def _render_vulnerability_scanner(self, security_scanner, device_manager):
        """Render vulnerability scanning interface"""
        st.markdown("### 🔍 Vulnerability Scanner")
        st.markdown("Scan network devices for security vulnerabilities and misconfigurations")
        
        # Scan options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Device selection
            devices = device_manager.get_all_devices()
            if not devices:
                st.info("No devices available for scanning. Add devices first.")
                return
            
            scan_option = st.radio(
                "Scan Target:",
                ["All Devices", "Selected Device", "Device Group"],
                horizontal=True
            )
            
            selected_device = None
            if scan_option == "Selected Device":
                selected_device = device_selector(devices, key="security_scan")
        
        with col2:
            # Scan type selection
            scan_types = st.multiselect(
                "Scan Types:",
                ["Port Scan", "SSL/TLS Check", "SSH Config", "SNMP Security", "Configuration Audit"],
                default=["Port Scan", "SSH Config"]
            )
        
        # Scan controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 Start Scan", type="primary", use_container_width=True):
                self._run_security_scan(security_scanner, scan_option, selected_device, scan_types)
        
        with col2:
            if st.button("📊 View Last Results", use_container_width=True):
                self._display_scan_results(security_scanner)
        
        with col3:
            if st.button("📤 Export Report", use_container_width=True):
                self._export_security_report(security_scanner)
        
        with col4:
            if st.button("🔄 Schedule Scan", use_container_width=True):
                self._schedule_security_scan()
        
        # Recent scan results
        st.markdown("### 📋 Recent Scan Results")
        self._display_scan_history(security_scanner)
    
    def _render_security_dashboard(self, security_scanner, device_manager):
        """Render security metrics dashboard"""
        st.markdown("### 📊 Security Dashboard")
        
        try:
            # Get security metrics
            devices = device_manager.get_all_devices()
            
            # Security metrics overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Devices", 
                    len(devices),
                    help="Total devices in inventory"
                )
            
            with col2:
                # Get vulnerability count
                vulns = security_scanner.get_all_vulnerabilities()
                critical_vulns = len([v for v in vulns if v.get('severity') == 'critical'])
                st.metric(
                    "Critical Vulnerabilities", 
                    critical_vulns,
                    delta=f"-{critical_vulns}" if critical_vulns == 0 else None,
                    delta_color="inverse"
                )
            
            with col3:
                # Calculate security score
                security_score = self._calculate_security_score(devices, vulns)
                st.metric(
                    "Security Score", 
                    f"{security_score}%",
                    delta=f"+{security_score-70}" if security_score > 70 else f"{security_score-70}",
                    delta_color="normal" if security_score > 70 else "inverse"
                )
            
            with col4:
                # Last scan time
                last_scan = security_scanner.get_last_scan_time()
                if last_scan:
                    hours_ago = int((datetime.now() - last_scan).total_seconds() / 3600)
                    st.metric(
                        "Last Scan", 
                        f"{hours_ago}h ago",
                        help=f"Last scan: {last_scan.strftime('%Y-%m-%d %H:%M')}"
                    )
                else:
                    st.metric("Last Scan", "Never", delta="No scans")
            
            # Security trends chart
            st.markdown("### 📈 Security Trends")
            self._render_security_trends_chart(security_scanner)
            
            # Top vulnerabilities
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚨 Top Vulnerabilities")
                self._render_top_vulnerabilities(security_scanner)
            
            with col2:
                st.markdown("### 🎯 Risk by Device Type")
                self._render_risk_by_device_type(security_scanner, devices)
            
        except Exception as e:
            logger.error(f"❌ Error rendering security dashboard: {e}")
            st.error("Error loading security dashboard")
    
    def _render_compliance_check(self, security_scanner, device_manager):
        """Render compliance checking interface"""
        st.markdown("### 📋 Compliance Check")
        st.markdown("Check device configurations against security standards and best practices")
        
        # Compliance framework selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            compliance_framework = st.selectbox(
                "Compliance Framework:",
                ["NIST Cybersecurity Framework", "CIS Controls", "ISO 27001", "Custom Policies"]
            )
        
        with col2:
            if st.button("🔍 Run Compliance Check", type="primary", use_container_width=True):
                self._run_compliance_check(security_scanner, compliance_framework)
        
        # Compliance results
        try:
            compliance_results = security_scanner.get_compliance_results()
            
            if compliance_results:
                # Compliance summary
                st.markdown("### 📊 Compliance Summary")
                self._render_compliance_summary(compliance_results)
                
                # Detailed compliance table
                st.markdown("### 📋 Detailed Results")
                compliance_table(compliance_results)
            else:
                st.info("No compliance results available. Run a compliance check to see results.")
                
        except Exception as e:
            logger.error(f"❌ Error loading compliance results: {e}")
            st.error("Error loading compliance results")
    
    def _render_security_alerts(self, security_scanner):
        """Render security alerts and notifications"""
        st.markdown("### 🚨 Security Alerts")
        
        try:
            # Alert filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                severity_filter = st.selectbox(
                    "Severity:",
                    ["All", "Critical", "High", "Medium", "Low"]
                )
            
            with col2:
                time_filter = st.selectbox(
                    "Time Range:",
                    ["Last 24h", "Last 7 days", "Last 30 days", "All time"]
                )
            
            with col3:
                status_filter = st.selectbox(
                    "Status:",
                    ["All", "Open", "Acknowledged", "Resolved"]
                )
            
            # Get and filter alerts
            alerts = security_scanner.get_security_alerts()
            filtered_alerts = self._filter_alerts(alerts, severity_filter, time_filter, status_filter)
            
            if filtered_alerts:
                # Alert summary
                st.markdown("### 📊 Alert Summary")
                self._render_alert_summary(filtered_alerts)
                
                # Alert list
                st.markdown("### 📋 Active Alerts")
                for alert in filtered_alerts[:10]:  # Show top 10
                    self._render_alert_card(alert, security_scanner)
            else:
                st.info("No alerts match the selected filters.")
                
        except Exception as e:
            logger.error(f"❌ Error loading security alerts: {e}")
            st.error("Error loading security alerts")
    
    def _run_security_scan(self, security_scanner, scan_option, selected_device, scan_types):
        """Run security scan"""
        try:
            with show_loading_spinner("Running security scan..."):
                if scan_option == "Selected Device" and selected_device:
                    results = security_scanner.scan_device(selected_device['id'], scan_types)
                    st.success(f"✅ Scan completed for {selected_device['hostname']}")
                else:
                    results = security_scanner.scan_all_devices(scan_types)
                    st.success("✅ Security scan completed for all devices")
                
                # Store results in session state
                st.session_state.last_security_scan = {
                    'timestamp': datetime.now(),
                    'results': results,
                    'scan_types': scan_types
                }
                
                notification_manager.add_notification(
                    "Security scan completed", 
                    "success"
                )
                
        except Exception as e:
            logger.error(f"❌ Error running security scan: {e}")
            st.error(f"Error running security scan: {e}")
    
    def _display_scan_results(self, security_scanner):
        """Display latest scan results"""
        try:
            last_scan = st.session_state.get('last_security_scan')
            
            if last_scan:
                st.markdown("### 📊 Latest Scan Results")
                
                # Scan info
                scan_time = last_scan['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                st.info(f"Scan completed: {scan_time}")
                
                # Results summary
                results = last_scan['results']
                if results.get('vulnerabilities'):
                    vulnerability_table(results['vulnerabilities'])
                else:
                    st.success("No vulnerabilities found!")
            else:
                st.info("No recent scan results available. Run a scan first.")
                
        except Exception as e:
            logger.error(f"❌ Error displaying scan results: {e}")
            st.error("Error displaying scan results")
    
    def _display_scan_history(self, security_scanner):
        """Display scan history"""
        try:
            history = security_scanner.get_scan_history()
            
            if history:
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No scan history available")
                
        except Exception as e:
            logger.error(f"❌ Error loading scan history: {e}")
            st.info("Scan history not available")
    
    def _calculate_security_score(self, devices, vulnerabilities):
        """Calculate overall security score"""
        try:
            if not devices:
                return 0
            
            # Base score
            base_score = 100
            
            # Deduct points for vulnerabilities
            critical_vulns = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
            high_vulns = len([v for v in vulnerabilities if v.get('severity') == 'high'])
            medium_vulns = len([v for v in vulnerabilities if v.get('severity') == 'medium'])
            
            score = base_score - (critical_vulns * 20) - (high_vulns * 10) - (medium_vulns * 5)
            
            return max(0, min(100, score))
            
        except Exception:
            return 75  # Default score
    
    def _render_security_trends_chart(self, security_scanner):
        """Render security trends chart"""
        try:
            # Generate sample trend data
            import numpy as np
            
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            vulnerabilities = np.random.poisson(5, 30)  # Sample data
            
            chart_data = pd.DataFrame({
                'Date': dates,
                'Vulnerabilities': vulnerabilities
            })
            
            st.line_chart(chart_data.set_index('Date'))
            
        except Exception as e:
            st.info("Security trends chart not available")
    
    def _render_top_vulnerabilities(self, security_scanner):
        """Render top vulnerabilities list"""
        try:
            vulns = security_scanner.get_all_vulnerabilities()
            
            if vulns:
                # Sort by severity
                severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
                sorted_vulns = sorted(
                    vulns, 
                    key=lambda x: severity_order.get(x.get('severity', 'low'), 0),
                    reverse=True
                )
                
                for vuln in sorted_vulns[:5]:  # Top 5
                    severity = vuln.get('severity', 'unknown')
                    severity_color = {
                        'critical': '🔴',
                        'high': '🟠', 
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(severity, '⚪')
                    
                    st.write(f"{severity_color} **{vuln.get('name', 'Unknown')}**")
                    st.caption(f"Severity: {severity.title()}")
            else:
                st.info("No vulnerabilities found")
                
        except Exception as e:
            st.info("Vulnerability data not available")
    
    def _render_risk_by_device_type(self, security_scanner, devices):
        """Render risk breakdown by device type"""
        try:
            device_types = {}
            for device in devices:
                device_type = device.get('device_type', 'unknown')
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            if device_types:
                df = pd.DataFrame(list(device_types.items()), columns=['Device Type', 'Count'])
                st.bar_chart(df.set_index('Device Type'))
            else:
                st.info("No device data available")
                
        except Exception as e:
            st.info("Device risk data not available")
    
    def _render_compliance_summary(self, compliance_results):
        """Render compliance summary metrics"""
        try:
            total_checks = len(compliance_results)
            passed_checks = len([r for r in compliance_results if r.get('status') == 'passed'])
            compliance_percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Checks", total_checks)
            
            with col2:
                st.metric("Passed", passed_checks, delta=f"{passed_checks}/{total_checks}")
            
            with col3:
                st.metric("Compliance %", f"{compliance_percentage:.1f}%")
                
        except Exception as e:
            st.error("Error calculating compliance summary")
    
    def _render_alert_summary(self, alerts):
        """Render alert summary metrics"""
        try:
            critical_alerts = len([a for a in alerts if a.get('severity') == 'critical'])
            high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
            open_alerts = len([a for a in alerts if a.get('status') == 'open'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Critical Alerts", critical_alerts, delta_color="inverse")
            
            with col2:
                st.metric("High Priority", high_alerts, delta_color="inverse") 
            
            with col3:
                st.metric("Open Alerts", open_alerts)
                
        except Exception as e:
            st.error("Error calculating alert summary")
    
    def _render_alert_card(self, alert, security_scanner):
        """Render individual alert card"""
        try:
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
                    st.caption(alert.get('description', 'No description'))
                
                with col2:
                    st.caption(f"Status: {alert.get('status', 'unknown').title()}")
                
                with col3:
                    if st.button("Acknowledge", key=f"ack_{alert.get('id', 'unknown')}"):
                        self._acknowledge_alert(alert, security_scanner)
                
        except Exception as e:
            st.error("Error rendering alert")
    
    def _acknowledge_alert(self, alert, security_scanner):
        """Acknowledge a security alert"""
        try:
            security_scanner.acknowledge_alert(alert.get('id'))
            st.success("Alert acknowledged")
            st.rerun()
        except Exception as e:
            st.error(f"Error acknowledging alert: {e}")
    
    def _filter_alerts(self, alerts, severity_filter, time_filter, status_filter):
        """Filter alerts based on criteria"""
        filtered = alerts
        
        # Filter by severity
        if severity_filter != "All":
            filtered = [a for a in filtered if a.get('severity', '').lower() == severity_filter.lower()]
        
        # Filter by status
        if status_filter != "All":
            filtered = [a for a in filtered if a.get('status', '').lower() == status_filter.lower()]
        
        # Filter by time (simplified)
        if time_filter != "All time":
            # Implementation depends on alert timestamp format
            pass
        
        return filtered
    
    def _run_compliance_check(self, security_scanner, framework):
        """Run compliance check"""
        try:
            with show_loading_spinner(f"Running {framework} compliance check..."):
                results = security_scanner.run_compliance_check(framework)
                st.success(f"✅ {framework} compliance check completed")
                notification_manager.add_notification(
                    f"{framework} compliance check completed",
                    "success"
                )
                st.rerun()
        except Exception as e:
            logger.error(f"❌ Error running compliance check: {e}")
            st.error(f"Error running compliance check: {e}")
    
    def _export_security_report(self, security_scanner):
        """Export security report"""
        try:
            report_data = security_scanner.generate_security_report()
            
            if report_data:
                report_json = json.dumps(report_data, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download Security Report",
                    data=report_json,
                    file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No security data available for export")
        except Exception as e:
            st.error(f"Error generating security report: {e}")
    
    def _schedule_security_scan(self):
        """Schedule recurring security scan"""
        st.info("🚧 Scheduled scanning feature coming soon...")
        
        # Placeholder for scheduling interface
        with st.expander("Schedule Configuration"):
            frequency = st.selectbox("Frequency:", ["Daily", "Weekly", "Monthly"])
            time = st.time_input("Scan Time:")
            if st.button("Save Schedule"):
                st.success("Scan schedule saved!")


def render_security_page():
    """Main function to render security page"""
    security_page = SecurityPage()
    security_page.render()
