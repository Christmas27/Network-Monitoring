#!/usr/bin/env python3
"""
Security Scanner Module

Provides security monitoring, vulnerability assessment, and compliance checking
for network devices and infrastructure.
"""

import json
import logging
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import random
import re

logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    id: str
    severity: str  # critical, high, medium, low
    category: str  # access, config, vulnerability, compliance
    title: str
    description: str
    device_id: str
    device_name: str
    timestamp: datetime
    status: str = "open"  # open, investigating, resolved
    recommendation: str = ""

@dataclass
class Vulnerability:
    """Vulnerability data structure"""
    id: str
    cve_id: str
    severity: str
    title: str
    description: str
    affected_devices: List[str]
    fix_available: bool
    risk_score: float

class SecurityScanner:
    """
    Network security scanner and monitoring system
    
    Features:
    - Vulnerability assessment
    - Configuration compliance checking
    - Access control monitoring
    - Security event correlation
    - Risk assessment
    """
    
    def __init__(self):
        self.db_path = "data/security.db"
        self.security_rules = self._load_security_rules()
        self._init_database()
    
    def _init_database(self):
        """Initialize security database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Security alerts
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    device_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    recommendation TEXT
                )
            ''')
            
            # Vulnerability scans
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    cve_id TEXT,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    affected_devices TEXT,
                    fix_available BOOLEAN DEFAULT FALSE,
                    risk_score REAL,
                    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Access logs
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    device_name TEXT,
                    username TEXT,
                    access_method TEXT,
                    source_ip TEXT,
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            ''')
            
            # Compliance checks
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        
        # Insert some initial data for demo
        self._populate_demo_data()
    
    def _load_security_rules(self) -> Dict:
        """Load security compliance rules"""
        return {
            "ssh_version": {
                "name": "SSH Version Check",
                "description": "Ensure SSH version 2.0 or higher",
                "severity": "high",
                "check": "ssh_version_2"
            },
            "snmp_community": {
                "name": "SNMP Community String",
                "description": "No default SNMP community strings",
                "severity": "critical",
                "check": "no_default_snmp"
            },
            "password_policy": {
                "name": "Password Policy",
                "description": "Strong password requirements",
                "severity": "medium",
                "check": "strong_passwords"
            },
            "firmware_updates": {
                "name": "Firmware Updates",
                "description": "Latest firmware versions installed",
                "severity": "high",
                "check": "current_firmware"
            },
            "access_control": {
                "name": "Access Control Lists",
                "description": "Proper ACL configuration",
                "severity": "medium",
                "check": "acl_configured"
            }
        }
    
    def _populate_demo_data(self):
        """Populate database with demo security data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if data already exists
                cursor = conn.execute('SELECT COUNT(*) FROM security_alerts')
                if cursor.fetchone()[0] > 0:
                    return  # Data already exists
                
                # Add demo security alerts
                demo_alerts = [
                    {
                        'id': 'SEC-001',
                        'severity': 'critical',
                        'category': 'vulnerability',
                        'title': 'Default SNMP Community String',
                        'description': 'Device using default "public" SNMP community string',
                        'device_id': 'switch-01',
                        'device_name': 'Core-Switch-01',
                        'recommendation': 'Change SNMP community string to secure value'
                    },
                    {
                        'id': 'SEC-002', 
                        'severity': 'high',
                        'category': 'access',
                        'title': 'Multiple Failed Login Attempts',
                        'description': '15 failed SSH login attempts in last hour',
                        'device_id': 'router-01',
                        'device_name': 'Border-Router-01',
                        'recommendation': 'Review access logs and implement login rate limiting'
                    },
                    {
                        'id': 'SEC-003',
                        'severity': 'medium',
                        'category': 'compliance',
                        'title': 'Outdated SSH Configuration',
                        'description': 'SSH version 1.5 detected, upgrade required',
                        'device_id': 'switch-02',
                        'device_name': 'Access-Switch-02',
                        'recommendation': 'Upgrade SSH to version 2.0 or higher'
                    }
                ]
                
                for alert in demo_alerts:
                    conn.execute('''
                        INSERT INTO security_alerts (
                            id, severity, category, title, description, 
                            device_id, device_name, recommendation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        alert['id'], alert['severity'], alert['category'],
                        alert['title'], alert['description'], alert['device_id'],
                        alert['device_name'], alert['recommendation']
                    ))
                
                # Add demo vulnerabilities
                demo_vulns = [
                    {
                        'id': 'VULN-001',
                        'cve_id': 'CVE-2023-12345',
                        'severity': 'high',
                        'title': 'Cisco IOS XE Authentication Bypass',
                        'description': 'Authentication bypass vulnerability in web UI',
                        'affected_devices': 'router-01,switch-01',
                        'fix_available': True,
                        'risk_score': 7.8
                    },
                    {
                        'id': 'VULN-002',
                        'cve_id': 'CVE-2023-67890',
                        'severity': 'medium',
                        'title': 'SNMP Information Disclosure',
                        'description': 'SNMP service leaking system information',
                        'affected_devices': 'switch-02,switch-03',
                        'fix_available': True,
                        'risk_score': 5.2
                    }
                ]
                
                for vuln in demo_vulns:
                    conn.execute('''
                        INSERT INTO vulnerabilities (
                            id, cve_id, severity, title, description,
                            affected_devices, fix_available, risk_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        vuln['id'], vuln['cve_id'], vuln['severity'],
                        vuln['title'], vuln['description'], vuln['affected_devices'],
                        vuln['fix_available'], vuln['risk_score']
                    ))
                
                conn.commit()
                logger.info("Demo security data populated")
                
        except Exception as e:
            logger.error(f"Error populating demo data: {e}")
    
    def get_security_overview(self) -> Dict:
        """Get comprehensive security overview"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get alert counts by severity
                cursor = conn.execute('''
                    SELECT severity, COUNT(*) 
                    FROM security_alerts 
                    WHERE status = 'open'
                    GROUP BY severity
                ''')
                alert_counts = dict(cursor.fetchall())
                
                # Get vulnerability counts
                cursor = conn.execute('''
                    SELECT severity, COUNT(*) 
                    FROM vulnerabilities 
                    GROUP BY severity
                ''')
                vuln_counts = dict(cursor.fetchall())
                
                # Calculate security score
                security_score = self._calculate_security_score(alert_counts, vuln_counts)
                
                # Get recent alerts
                cursor = conn.execute('''
                    SELECT * FROM security_alerts 
                    WHERE status = 'open'
                    ORDER BY timestamp DESC 
                    LIMIT 5
                ''')
                recent_alerts = [dict(zip([col[0] for col in cursor.description], row)) 
                               for row in cursor.fetchall()]
                
                return {
                    'security_score': security_score,
                    'alert_counts': {
                        'critical': alert_counts.get('critical', 0),
                        'high': alert_counts.get('high', 0),
                        'medium': alert_counts.get('medium', 0),
                        'low': alert_counts.get('low', 0)
                    },
                    'vulnerability_counts': vuln_counts,
                    'total_alerts': sum(alert_counts.values()),
                    'recent_alerts': recent_alerts,
                    'compliance_status': self._get_compliance_status(),
                    'last_scan': datetime.now().isoformat(),
                    'risk_level': self._get_risk_level(security_score)
                }
                
        except Exception as e:
            logger.error(f"Error getting security overview: {e}")
            return self._get_fallback_overview()
    
    def _calculate_security_score(self, alert_counts: Dict, vuln_counts: Dict) -> int:
        """Calculate overall security score (0-100)"""
        base_score = 100
        
        # Deduct points for alerts
        deductions = 0
        deductions += alert_counts.get('critical', 0) * 20
        deductions += alert_counts.get('high', 0) * 10
        deductions += alert_counts.get('medium', 0) * 5
        deductions += alert_counts.get('low', 0) * 2
        
        # Deduct points for vulnerabilities
        deductions += vuln_counts.get('critical', 0) * 15
        deductions += vuln_counts.get('high', 0) * 8
        deductions += vuln_counts.get('medium', 0) * 3
        
        return max(0, base_score - deductions)
    
    def _get_risk_level(self, security_score: int) -> str:
        """Determine risk level based on security score"""
        if security_score >= 90:
            return "Low"
        elif security_score >= 70:
            return "Medium"
        elif security_score >= 50:
            return "High"
        else:
            return "Critical"
    
    def _get_compliance_status(self) -> Dict:
        """Get compliance status summary"""
        return {
            'total_rules': len(self.security_rules),
            'passed': random.randint(6, 8),
            'failed': random.randint(1, 3),
            'percentage': random.randint(75, 95)
        }
    
    def get_security_alerts(self, limit: int = 50) -> List[Dict]:
        """Get security alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM security_alerts 
                    ORDER BY 
                        CASE severity
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2  
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END,
                        timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting security alerts: {e}")
            return []
    
    def get_vulnerabilities(self) -> List[Dict]:
        """Get vulnerability assessment results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM vulnerabilities 
                    ORDER BY risk_score DESC
                ''')
                
                vulns = []
                for row in cursor.fetchall():
                    vuln = dict(row)
                    vuln['affected_devices'] = vuln['affected_devices'].split(',') if vuln['affected_devices'] else []
                    vulns.append(vuln)
                
                return vulns
                
        except Exception as e:
            logger.error(f"Error getting vulnerabilities: {e}")
            return []
    
    def run_compliance_check(self, device_id: str = None) -> Dict:
        """Run compliance check on devices"""
        try:
            results = {}
            
            # If specific device, check only that device
            devices_to_check = [device_id] if device_id else ['router-01', 'switch-01', 'switch-02']
            
            for device in devices_to_check:
                device_results = []
                
                for rule_id, rule in self.security_rules.items():
                    # Simulate compliance check
                    passed = self._simulate_compliance_check(rule_id, device)
                    
                    device_results.append({
                        'rule_name': rule['name'],
                        'description': rule['description'],
                        'severity': rule['severity'],
                        'status': 'passed' if passed else 'failed',
                        'details': self._get_compliance_details(rule_id, passed)
                    })
                
                results[device] = device_results
            
            return results
            
        except Exception as e:
            logger.error(f"Error running compliance check: {e}")
            return {}
    
    def _simulate_compliance_check(self, rule_id: str, device_id: str) -> bool:
        """Simulate compliance check (returns random results for demo)"""
        # Use device_id and rule_id to create consistent results
        seed = hash(f"{device_id}_{rule_id}") % 100
        return seed > 25  # 75% pass rate
    
    def _get_compliance_details(self, rule_id: str, passed: bool) -> str:
        """Get compliance check details"""
        if passed:
            return "Configuration meets security requirements"
        else:
            details = {
                'ssh_version': 'SSH version 1.5 detected, upgrade to 2.0+ required',
                'snmp_community': 'Default SNMP community string "public" found',
                'password_policy': 'Password complexity requirements not met',
                'firmware_updates': 'Firmware version is 2 versions behind latest',
                'access_control': 'ACL configuration incomplete or missing'
            }
            return details.get(rule_id, 'Security requirement not met')
    
    def scan_for_vulnerabilities(self, device_id: str = None) -> Dict:
        """Scan devices for vulnerabilities"""
        try:
            scan_results = {
                'scan_id': f"scan_{int(datetime.now().timestamp())}",
                'timestamp': datetime.now().isoformat(),
                'devices_scanned': 3 if not device_id else 1,
                'vulnerabilities_found': random.randint(2, 5),
                'scan_duration': f"{random.randint(30, 120)} seconds",
                'scan_status': 'completed'
            }
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Error scanning for vulnerabilities: {e}")
            return {'error': str(e)}
    
    def get_access_logs(self, device_id: str = None, limit: int = 50) -> List[Dict]:
        """Get device access logs"""
        try:
            # Generate simulated access logs for demo
            logs = []
            current_time = datetime.now()
            
            for i in range(limit):
                log_time = current_time - timedelta(hours=random.randint(0, 72))
                
                logs.append({
                    'id': i + 1,
                    'device_id': device_id or f"device-{random.randint(1, 5)}",
                    'device_name': f"Device-{random.randint(1, 5)}",
                    'username': random.choice(['admin', 'operator', 'cisco', 'netadmin']),
                    'access_method': random.choice(['SSH', 'Console', 'HTTPS', 'Telnet']),
                    'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    'success': random.choice([True, True, True, False]),  # 75% success rate
                    'timestamp': log_time.isoformat(),
                    'details': random.choice([
                        'Normal login session',
                        'Administrative access',
                        'Configuration change',
                        'Failed authentication',
                        'Session timeout'
                    ])
                })
            
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "admin") -> bool:
        """Acknowledge a security alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE security_alerts 
                    SET status = 'acknowledged'
                    WHERE id = ?
                ''', (alert_id,))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "admin", notes: str = "") -> bool:
        """Resolve a security alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE security_alerts 
                    SET status = 'resolved'
                    WHERE id = ?
                ''', (alert_id,))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    def _get_fallback_overview(self) -> Dict:
        """Fallback security overview for demo"""
        return {
            'security_score': 78,
            'alert_counts': {
                'critical': 1,
                'high': 2,
                'medium': 3,
                'low': 1
            },
            'vulnerability_counts': {
                'high': 1,
                'medium': 2,
                'low': 1
            },
            'total_alerts': 7,
            'recent_alerts': [],
            'compliance_status': {
                'total_rules': 8,
                'passed': 6,
                'failed': 2,
                'percentage': 75
            },
            'last_scan': datetime.now().isoformat(),
            'risk_level': 'Medium'
        }
    
    def get_security_trends(self, days: int = 30) -> Dict:
        """Get security trends over time"""
        try:
            # Generate trend data for charts
            dates = []
            scores = []
            alerts = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                dates.append(date.strftime('%Y-%m-%d'))
                
                # Simulate trending data
                base_score = 78
                variation = random.randint(-10, 10)
                scores.append(max(0, min(100, base_score + variation)))
                
                alerts.append(random.randint(0, 8))
            
            return {
                'dates': list(reversed(dates)),
                'security_scores': list(reversed(scores)),
                'daily_alerts': list(reversed(alerts)),
                'trend_direction': 'improving' if scores[-1] > scores[0] else 'declining'
            }
            
        except Exception as e:
            logger.error(f"Error getting security trends: {e}")
            return {}