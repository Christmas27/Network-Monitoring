#!/usr/bin/env python3
"""
Security Scanner Module - Clean Working Implementation

Provides real security monitoring for the network dashboard.
"""

import json
import logging
import sqlite3
import hashlib
import socket
import paramiko
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    id: str
    severity: str
    category: str
    title: str
    description: str
    device_id: str
    timestamp: datetime
    status: str = "open"

@dataclass
class PortScanResult:
    """Port scan result data structure"""
    host: str
    port: int
    status: str
    service: str
    version: str = ""

class SecurityScanner:
    """Real security scanner for lab devices"""
    
    def __init__(self):
        self.db_path = "data/security.db"
        self._init_database()
        logger.info("🛡️ Security Scanner initialized")
    
    def _init_database(self):
        """Initialize security database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS port_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    service TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ssh_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            ''')
            
            conn.commit()
            logger.info("🔒 Security database initialized")
    
    def scan_ports(self, host: str, port_range: Optional[List[int]] = None, timeout: int = 3) -> List[PortScanResult]:
        """Perform port scanning on target host"""
        if port_range is None:
            port_range = [21, 22, 23, 53, 80, 443, 8080, 8443]
        
        results = []
        
        def scan_port(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    result = sock.connect_ex((host, port))
                    
                    if result == 0:
                        service = self._get_service_name(port)
                        scan_result = PortScanResult(
                            host=host,
                            port=port,
                            status='open',
                            service=service
                        )
                        self._store_port_result(scan_result)
                        return scan_result
            except Exception:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scan_port, port) for port in port_range]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        logger.info(f"🔍 Port scan completed: {len(results)} open ports on {host}")
        return results
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
            443: 'https', 993: 'imaps', 995: 'pop3s',
            8080: 'http-proxy', 8443: 'https-alt'
        }
        return services.get(port, f'port-{port}')
    
    def _store_port_result(self, result: PortScanResult):
        """Store port scan result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO port_scan_results (host, port, status, service)
                    VALUES (?, ?, ?, ?)
                ''', (result.host, result.port, result.status, result.service))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store port result: {e}")
    
    def analyze_ssh_security(self, host: str, port: int = 22) -> Dict[str, Any]:
        """Analyze SSH security"""
        analysis = {
            'host': host,
            'port': port,
            'accessible': False,
            'version': '',
            'security_issues': [],
            'risk_level': 'low'
        }
        
        try:
            # Test SSH connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            analysis['accessible'] = True
            analysis['version'] = banner
            
            # Check for weak credentials
            weak_creds = self._test_weak_credentials(host, port)
            if weak_creds['found']:
                analysis['security_issues'].append({
                    'type': 'weak_credentials',
                    'severity': 'critical',
                    'description': 'Default credentials detected'
                })
                analysis['risk_level'] = 'critical'
            
            # Log security event
            self._log_ssh_event(host, 'security_scan', analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _test_weak_credentials(self, host: str, port: int) -> Dict[str, Any]:
        """Test for weak SSH credentials"""
        weak_creds = [('admin', 'admin'), ('root', 'root')]
        result = {'found': False, 'credentials': []}
        
        for username, password in weak_creds:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=host, port=port, username=username, 
                           password=password, timeout=3)
                
                result['found'] = True
                result['credentials'].append(f"{username}:{password}")
                ssh.close()
                break
                
            except paramiko.AuthenticationException:
                pass
            except Exception:
                break
                
        return result
    
    def _log_ssh_event(self, device_id: str, event_type: str, details: Dict):
        """Log SSH security event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO ssh_events (device_id, event_type, details)
                    VALUES (?, ?, ?)
                ''', (device_id, event_type, json.dumps(details)))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log SSH event: {e}")
    
    def create_alert(self, severity: str, category: str, title: str, 
                    description: str, device_id: str) -> str:
        """Create security alert"""
        alert_id = hashlib.md5(f"{device_id}_{title}_{datetime.now()}".encode()).hexdigest()[:12]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO security_alerts 
                    (id, severity, category, title, description, device_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (alert_id, severity, category, title, description, device_id))
                conn.commit()
                logger.warning(f"🚨 Security alert: {title}")
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
        
        return alert_id
    
    def get_security_overview(self) -> Dict[str, Any]:
        """Get security overview"""
        overview = {
            'total_alerts': 0,
            'critical_alerts': 0,
            'high_alerts': 0,
            'medium_alerts': 0,
            'low_alerts': 0,
            'open_ports': 0,
            'devices_scanned': 0,
            'security_score': 85
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count alerts by severity
                cursor = conn.execute('''
                    SELECT severity, COUNT(*) FROM security_alerts 
                    WHERE status = 'open' GROUP BY severity
                ''')
                
                for row in cursor.fetchall():
                    severity, count = row
                    overview[f'{severity}_alerts'] = count
                    overview['total_alerts'] += count
                
                # Count open ports
                cursor = conn.execute('''
                    SELECT COUNT(DISTINCT host || ':' || port) FROM port_scan_results 
                    WHERE status = 'open'
                ''')
                overview['open_ports'] = cursor.fetchone()[0] or 0
                
                # Count scanned devices
                cursor = conn.execute('''
                    SELECT COUNT(DISTINCT host) FROM port_scan_results
                ''')
                overview['devices_scanned'] = cursor.fetchone()[0] or 0
        
        except Exception as e:
            logger.error(f"Error getting security overview: {e}")
        
        return overview
    
    def comprehensive_scan(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive security scan"""
        scan_results = {
            'scan_id': hashlib.md5(f"scan_{datetime.now()}".encode()).hexdigest()[:8],
            'start_time': datetime.now(),
            'devices_scanned': 0,
            'total_devices': len(devices),
            'alerts_created': 0,
            'issues_found': []
        }
        
        logger.info(f"🔍 Starting security scan of {len(devices)} devices")
        
        for device in devices:
            device_name = device.get('hostname', 'unknown')
            ip_address = device.get('ip_address', '')
            
            if ':' in ip_address:
                host, ssh_port = ip_address.split(':')
                ssh_port = int(ssh_port)
            else:
                host = ip_address
                ssh_port = 22
            
            try:
                # Port scan
                port_results = self.scan_ports(host)
                
                # SSH analysis
                ssh_analysis = self.analyze_ssh_security(host, ssh_port)
                
                # Create alerts for issues
                for issue in ssh_analysis.get('security_issues', []):
                    alert_id = self.create_alert(
                        severity=issue['severity'],
                        category='vulnerability',
                        title=f"SSH Security Issue: {device_name}",
                        description=issue['description'],
                        device_id=device_name
                    )
                    
                    if alert_id:
                        scan_results['alerts_created'] += 1
                        scan_results['issues_found'].append({
                            'device': device_name,
                            'issue': issue['type'],
                            'severity': issue['severity']
                        })
                
                scan_results['devices_scanned'] += 1
                
            except Exception as e:
                logger.error(f"Error scanning {device_name}: {e}")
        
        scan_results['end_time'] = datetime.now()
        scan_results['duration'] = (scan_results['end_time'] - scan_results['start_time']).total_seconds()
        
        logger.info(f"✅ Security scan completed: {scan_results['devices_scanned']} devices, {scan_results['alerts_created']} alerts")
        return scan_results
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent security alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM security_alerts 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_security_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get security alerts for Streamlit dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        id,
                        severity,
                        category as alert_type,
                        title,
                        description,
                        device_id,
                        device_name,
                        timestamp,
                        status,
                        recommendation
                    FROM security_alerts 
                    WHERE status = 'open'
                    ORDER BY 
                        CASE severity 
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                            ELSE 5
                        END,
                        timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                logger.info(f"📊 Retrieved {len(alerts)} security alerts")
                return alerts
                
        except Exception as e:
            logger.error(f"❌ Error getting security alerts: {e}")
            return []

    def get_port_scan_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get port scan results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM port_scan_results 
                    WHERE status = 'open'
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting port scan results: {e}")
            return []
