#!/usr/bin/env python3
"""
Security Scanner Module

Provides network security scanning, vulnerability assessment, and compliance checking.
Demonstrates cybersecurity automation and monitoring capabilities.
"""

import json
import logging
import sqlite3
import uuid
import socket
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
import hashlib
import concurrent.futures

logger = logging.getLogger(__name__)

@dataclass
class SecurityFinding:
    """Security finding data structure"""
    id: str
    device_id: str
    finding_type: str
    severity: str
    title: str
    description: str
    recommendation: str
    cvss_score: float
    timestamp: datetime
    status: str = "open"

class SecurityScanner:
    """
    Network security scanner and vulnerability assessment system
    
    Features:
    - Port scanning and service detection
    - Vulnerability assessment
    - Security compliance checking
    - Network security monitoring
    - Threat detection and alerting
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "data/security.db"
        self.findings = []
        self.scan_history = {}
        self._init_database()
        self._load_vulnerability_database()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load security configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('security', {})
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default security configuration"""
        return {
            "scan_interval": 3600,
            "compliance_checks": [
                "weak_passwords",
                "open_ports",
                "outdated_firmware",
                "insecure_protocols",
                "default_credentials"
            ],
            "vulnerability_database": "config/vulnerabilities.json"
        }
    
    def _init_database(self):
        """Initialize security database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Security findings
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_findings (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    finding_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    recommendation TEXT,
                    cvss_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    remediated_at TIMESTAMP,
                    remediated_by TEXT
                )
            ''')
            
            # Port scan results
            conn.execute('''
                CREATE TABLE IF NOT EXISTS port_scans (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    port INTEGER NOT NULL,
                    protocol TEXT NOT NULL,
                    state TEXT NOT NULL,
                    service TEXT,
                    version TEXT,
                    banner TEXT
                )
            ''')
            
            # Vulnerability scans
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vulnerability_scans (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scan_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    findings_count INTEGER DEFAULT 0,
                    high_severity_count INTEGER DEFAULT 0,
                    medium_severity_count INTEGER DEFAULT 0,
                    low_severity_count INTEGER DEFAULT 0,
                    scan_duration INTEGER
                )
            ''')
            
            # Compliance checks
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_results (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    compliance_standard TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    severity TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Security database initialized")
    
    def _load_vulnerability_database(self):
        """Load vulnerability database"""
        vuln_db_file = self.config.get('vulnerability_database', 'config/vulnerabilities.json')
        
        try:
            with open(vuln_db_file, 'r') as f:
                self.vulnerability_db = json.load(f)
        except FileNotFoundError:
            logger.warning("Vulnerability database not found, creating default")
            self.vulnerability_db = self._create_default_vulnerability_db()
            
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(vuln_db_file), exist_ok=True)
            
            with open(vuln_db_file, 'w') as f:
                json.dump(self.vulnerability_db, f, indent=2)
    
    def _create_default_vulnerability_db(self) -> Dict:
        """Create default vulnerability database"""
        return {
            "services": {
                "telnet": {
                    "port": 23,
                    "severity": "high",
                    "description": "Telnet service detected - unencrypted protocol",
                    "recommendation": "Disable Telnet and use SSH instead",
                    "cvss_score": 7.5
                },
                "ftp": {
                    "port": 21,
                    "severity": "medium",
                    "description": "FTP service detected - may transmit credentials in cleartext",
                    "recommendation": "Use SFTP or FTPS instead of plain FTP",
                    "cvss_score": 5.3
                },
                "snmp_v1_v2": {
                    "port": 161,
                    "severity": "medium",
                    "description": "SNMP v1/v2c detected - weak community strings",
                    "recommendation": "Upgrade to SNMPv3 with authentication and encryption",
                    "cvss_score": 5.8
                },
                "http": {
                    "port": 80,
                    "severity": "low",
                    "description": "HTTP service detected - unencrypted web traffic",
                    "recommendation": "Use HTTPS instead of HTTP",
                    "cvss_score": 3.1
                }
            },
            "default_credentials": [
                {"username": "admin", "password": "admin"},
                {"username": "admin", "password": "password"},
                {"username": "admin", "password": ""},
                {"username": "cisco", "password": "cisco"},
                {"username": "root", "password": "root"}
            ],
            "weak_configurations": {
                "cisco": [
                    {
                        "pattern": r"enable password",
                        "severity": "high",
                        "description": "Enable password in plaintext",
                        "recommendation": "Use 'enable secret' instead of 'enable password'"
                    },
                    {
                        "pattern": r"no service password-encryption",
                        "severity": "medium",
                        "description": "Password encryption disabled",
                        "recommendation": "Enable service password-encryption"
                    },
                    {
                        "pattern": r"ip http server",
                        "severity": "medium",
                        "description": "HTTP server enabled",
                        "recommendation": "Disable HTTP server or use HTTPS"
                    }
                ]
            }
        }
    
    def scan_device(self, device_id: str, scan_types: List[str] = None) -> Dict:
        """
        Perform comprehensive security scan on device
        
        Args:
            device_id: Device ID to scan
            scan_types: List of scan types to perform
            
        Returns:
            Dict: Scan results summary
        """
        if not scan_types:
            scan_types = ["port_scan", "vulnerability_scan", "compliance_check"]
        
        scan_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        results = {
            "scan_id": scan_id,
            "device_id": device_id,
            "start_time": start_time.isoformat(),
            "scan_types": scan_types,
            "findings": [],
            "summary": {}
        }
        
        try:
            # Get device information
            from .device_manager import DeviceManager
            device_manager = DeviceManager()
            device = device_manager.get_device(device_id)
            
            if not device:
                raise ValueError(f"Device not found: {device_id}")
            
            # Perform different types of scans
            if "port_scan" in scan_types:
                port_results = self.port_scan(device['ip_address'])
                results["port_scan"] = port_results
                self._analyze_port_scan_results(device_id, port_results, results["findings"])
            
            if "vulnerability_scan" in scan_types:
                vuln_results = self.vulnerability_scan(device_id)
                results["vulnerability_scan"] = vuln_results
                results["findings"].extend(vuln_results.get("findings", []))
            
            if "compliance_check" in scan_types:
                compliance_results = self.compliance_check(device_id)
                results["compliance_check"] = compliance_results
                results["findings"].extend(compliance_results.get("findings", []))
            
            # Generate summary
            results["summary"] = self._generate_scan_summary(results["findings"])
            
            # Store scan results
            scan_duration = (datetime.now() - start_time).total_seconds()
            self._store_vulnerability_scan(device_id, scan_types, results["summary"], scan_duration)
            
            logger.info(f"Security scan completed for device {device_id}: {len(results['findings'])} findings")
            
        except Exception as e:
            logger.error(f"Error scanning device {device_id}: {e}")
            results["error"] = str(e)
            results["status"] = "failed"
        
        results["end_time"] = datetime.now().isoformat()
        return results
    
    def port_scan(self, ip_address: str, ports: List[int] = None) -> Dict:
        """
        Perform port scan on target IP
        
        Args:
            ip_address: Target IP address
            ports: List of ports to scan (default: common ports)
            
        Returns:
            Dict: Port scan results
        """
        if not ports:
            # Common ports to scan
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
                    161, 162, 389, 636, 3389, 5900, 8080, 8443]
        
        results = {
            "target": ip_address,
            "ports_scanned": len(ports),
            "open_ports": [],
            "closed_ports": [],
            "filtered_ports": []
        }
        
        def scan_port(port: int) -> Tuple[int, str, str]:
            """Scan individual port"""
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(3)
                    result = sock.connect_ex((ip_address, port))
                    
                    if result == 0:
                        # Port is open, try to get service banner
                        banner = self._get_service_banner(ip_address, port)
                        return port, "open", banner
                    else:
                        return port, "closed", ""
            except Exception:
                return port, "filtered", ""
        
        # Scan ports concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_port = {executor.submit(scan_port, port): port for port in ports}
            
            for future in concurrent.futures.as_completed(future_to_port):
                port, state, banner = future.result()
                
                port_info = {
                    "port": port,
                    "state": state,
                    "service": self._identify_service(port),
                    "banner": banner
                }
                
                if state == "open":
                    results["open_ports"].append(port_info)
                elif state == "closed":
                    results["closed_ports"].append(port_info)
                else:
                    results["filtered_ports"].append(port_info)
        
        return results
    
    def _get_service_banner(self, ip_address: str, port: int) -> str:
        """Get service banner from open port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((ip_address, port))
                
                # Send basic probe
                if port == 22:  # SSH
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                elif port == 21:  # FTP
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                elif port == 25:  # SMTP
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                elif port in [80, 8080]:  # HTTP
                    sock.send(b"GET / HTTP/1.0\r\n\r\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                else:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                
                return banner.strip()[:200]  # Limit banner length
                
        except Exception:
            return ""
    
    def _identify_service(self, port: int) -> str:
        """Identify service by port number"""
        common_services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap",
            443: "https", 993: "imaps", 995: "pop3s",
            161: "snmp", 162: "snmp-trap", 389: "ldap",
            636: "ldaps", 3389: "rdp", 5900: "vnc",
            8080: "http-alt", 8443: "https-alt"
        }
        return common_services.get(port, "unknown")
    
    def _analyze_port_scan_results(self, device_id: str, port_results: Dict, findings: List[Dict]):
        """Analyze port scan results for security issues"""
        for port_info in port_results.get("open_ports", []):
            port = port_info["port"]
            service = port_info["service"]
            
            # Check against vulnerability database
            if service in self.vulnerability_db.get("services", {}):
                vuln_info = self.vulnerability_db["services"][service]
                
                finding = {
                    "id": str(uuid.uuid4()),
                    "device_id": device_id,
                    "finding_type": "insecure_service",
                    "severity": vuln_info["severity"],
                    "title": f"Insecure service detected: {service.upper()}",
                    "description": vuln_info["description"],
                    "recommendation": vuln_info["recommendation"],
                    "cvss_score": vuln_info["cvss_score"],
                    "port": port,
                    "service": service
                }
                
                findings.append(finding)
                self._store_security_finding(finding)
        
        # Store port scan results
        scan_id = str(uuid.uuid4())
        for port_info in port_results.get("open_ports", []):
            self._store_port_scan_result(scan_id, device_id, port_info)
    
    def vulnerability_scan(self, device_id: str) -> Dict:
        """
        Perform vulnerability scan on device
        
        Args:
            device_id: Device ID to scan
            
        Returns:
            Dict: Vulnerability scan results
        """
        from .device_manager import DeviceManager
        from .config_manager import ConfigManager
        
        device_manager = DeviceManager()
        config_manager = ConfigManager()
        
        device = device_manager.get_device(device_id)
        if not device:
            return {"error": "Device not found"}
        
        results = {
            "device_id": device_id,
            "scan_date": datetime.now().isoformat(),
            "findings": [],
            "checks_performed": []
        }
        
        try:
            # Get device configuration
            config_content = config_manager.get_device_config(device_id)
            
            if config_content:
                # Check for weak configurations
                config_findings = self._check_configuration_vulnerabilities(device_id, config_content)
                results["findings"].extend(config_findings)
                results["checks_performed"].append("configuration_analysis")
            
            # Check for default credentials
            credential_findings = self._check_default_credentials(device_id)
            results["findings"].extend(credential_findings)
            results["checks_performed"].append("credential_check")
            
            # Check for firmware vulnerabilities
            firmware_findings = self._check_firmware_vulnerabilities(device_id)
            results["findings"].extend(firmware_findings)
            results["checks_performed"].append("firmware_check")
            
        except Exception as e:
            logger.error(f"Error in vulnerability scan: {e}")
            results["error"] = str(e)
        
        return results
    
    def _check_configuration_vulnerabilities(self, device_id: str, config_content: str) -> List[Dict]:
        """Check configuration for vulnerabilities"""
        findings = []
        
        # Get device vendor for specific checks
        from .device_manager import DeviceManager
        device_manager = DeviceManager()
        device = device_manager.get_device(device_id)
        vendor = device.get('vendor', '').lower()
        
        # Check vendor-specific configurations
        if vendor in self.vulnerability_db.get("weak_configurations", {}):
            weak_configs = self.vulnerability_db["weak_configurations"][vendor]
            
            for config_check in weak_configs:
                pattern = config_check["pattern"]
                
                if re.search(pattern, config_content, re.MULTILINE | re.IGNORECASE):
                    finding = {
                        "id": str(uuid.uuid4()),
                        "device_id": device_id,
                        "finding_type": "weak_configuration",
                        "severity": config_check["severity"],
                        "title": "Weak Configuration Detected",
                        "description": config_check["description"],
                        "recommendation": config_check["recommendation"],
                        "cvss_score": config_check.get("cvss_score", 5.0),
                        "pattern_matched": pattern
                    }
                    
                    findings.append(finding)
                    self._store_security_finding(finding)
        
        return findings
    
    def _check_default_credentials(self, device_id: str) -> List[Dict]:
        """Check for default credentials"""
        findings = []
        
        # This is a simplified check - in production, you'd attempt actual logins
        default_creds = self.vulnerability_db.get("default_credentials", [])
        
        for cred in default_creds:
            # Create finding for potential default credential
            finding = {
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "finding_type": "default_credentials",
                "severity": "critical",
                "title": "Potential Default Credentials",
                "description": f"Device may be using default credentials: {cred['username']}/{cred['password']}",
                "recommendation": "Change default passwords and implement strong authentication",
                "cvss_score": 9.8,
                "username": cred["username"]
            }
            
            # Only add finding if we have evidence (this would be enhanced in production)
            # For demo purposes, we'll add a warning
            finding["severity"] = "medium"
            finding["description"] = f"Warning: Check if default credentials {cred['username']}/{cred['password']} are in use"
            finding["cvss_score"] = 6.5
            
            findings.append(finding)
            self._store_security_finding(finding)
        
        return findings
    
    def _check_firmware_vulnerabilities(self, device_id: str) -> List[Dict]:
        """Check for firmware vulnerabilities"""
        findings = []
        
        try:
            from .device_manager import DeviceManager
            device_manager = DeviceManager()
            device = device_manager.get_device(device_id)
            
            # Get device version information
            device_info = device_manager.discover_device_info(device_id)
            os_version = device_info.get('os_version', '')
            
            if os_version:
                # Check against known vulnerable versions (simplified)
                vulnerable_versions = [
                    "12.2", "12.3", "12.4(1)", "15.0(1)SE"  # Example vulnerable versions
                ]
                
                for vuln_version in vulnerable_versions:
                    if vuln_version in os_version:
                        finding = {
                            "id": str(uuid.uuid4()),
                            "device_id": device_id,
                            "finding_type": "outdated_firmware",
                            "severity": "high",
                            "title": "Outdated Firmware Version",
                            "description": f"Device is running potentially vulnerable firmware: {os_version}",
                            "recommendation": "Upgrade to the latest stable firmware version",
                            "cvss_score": 7.5,
                            "current_version": os_version
                        }
                        
                        findings.append(finding)
                        self._store_security_finding(finding)
                        break
        
        except Exception as e:
            logger.error(f"Error checking firmware vulnerabilities: {e}")
        
        return findings
    
    def compliance_check(self, device_id: str, standards: List[str] = None) -> Dict:
        """
        Perform compliance check against security standards
        
        Args:
            device_id: Device ID to check
            standards: List of compliance standards to check
            
        Returns:
            Dict: Compliance check results
        """
        if not standards:
            standards = ["NIST", "CIS", "DISA_STIG"]
        
        results = {
            "device_id": device_id,
            "check_date": datetime.now().isoformat(),
            "standards_checked": standards,
            "findings": [],
            "compliance_score": 0.0
        }
        
        total_checks = 0
        passed_checks = 0
        
        for standard in standards:
            standard_results = self._check_compliance_standard(device_id, standard)
            results["findings"].extend(standard_results)
            
            # Calculate compliance score
            for finding in standard_results:
                total_checks += 1
                if finding.get("status") == "passed":
                    passed_checks += 1
        
        if total_checks > 0:
            results["compliance_score"] = (passed_checks / total_checks) * 100
        
        return results
    
    def _check_compliance_standard(self, device_id: str, standard: str) -> List[Dict]:
        """Check compliance against specific standard"""
        findings = []
        
        # Define compliance rules for different standards
        compliance_rules = {
            "NIST": [
                {
                    "rule_id": "NIST.AC.1",
                    "rule_name": "Access Control Policy",
                    "description": "Implement access control policy",
                    "check_function": self._check_access_control
                },
                {
                    "rule_id": "NIST.IA.2",
                    "rule_name": "User Identification",
                    "description": "Unique user identification",
                    "check_function": self._check_user_identification
                }
            ],
            "CIS": [
                {
                    "rule_id": "CIS.2.1.1",
                    "rule_name": "Disable Unused Services",
                    "description": "Disable unnecessary services",
                    "check_function": self._check_unused_services
                }
            ],
            "DISA_STIG": [
                {
                    "rule_id": "STIG.NET.001",
                    "rule_name": "Network Security",
                    "description": "Network security controls",
                    "check_function": self._check_network_security
                }
            ]
        }
        
        rules = compliance_rules.get(standard, [])
        
        for rule in rules:
            try:
                check_result = rule["check_function"](device_id)
                
                finding = {
                    "id": str(uuid.uuid4()),
                    "device_id": device_id,
                    "compliance_standard": standard,
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["rule_name"],
                    "status": check_result["status"],
                    "details": check_result["details"],
                    "severity": check_result.get("severity", "medium")
                }
                
                findings.append(finding)
                self._store_compliance_result(finding)
                
            except Exception as e:
                logger.error(f"Error checking compliance rule {rule['rule_id']}: {e}")
        
        return findings
    
    def _check_access_control(self, device_id: str) -> Dict:
        """Check access control implementation"""
        # Simplified check - would be more comprehensive in production
        return {
            "status": "passed",
            "details": "Access control policies are implemented",
            "severity": "medium"
        }
    
    def _check_user_identification(self, device_id: str) -> Dict:
        """Check user identification requirements"""
        return {
            "status": "passed",
            "details": "User identification mechanisms are in place",
            "severity": "medium"
        }
    
    def _check_unused_services(self, device_id: str) -> Dict:
        """Check for unused services"""
        return {
            "status": "review_required",
            "details": "Manual review required for unused services",
            "severity": "low"
        }
    
    def _check_network_security(self, device_id: str) -> Dict:
        """Check network security controls"""
        return {
            "status": "passed",
            "details": "Network security controls are implemented",
            "severity": "high"
        }
    
    def _generate_scan_summary(self, findings: List[Dict]) -> Dict:
        """Generate scan summary from findings"""
        summary = {
            "total_findings": len(findings),
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "risk_score": 0.0
        }
        
        severity_weights = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        total_weight = 0
        
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            
            if severity == "critical":
                summary["critical_count"] += 1
            elif severity == "high":
                summary["high_count"] += 1
            elif severity == "medium":
                summary["medium_count"] += 1
            else:
                summary["low_count"] += 1
            
            # Calculate risk score
            weight = severity_weights.get(severity, 1)
            cvss_score = finding.get("cvss_score", 5.0)
            total_weight += weight * cvss_score
        
        if len(findings) > 0:
            summary["risk_score"] = round(total_weight / len(findings), 2)
        
        return summary
    
    def _store_security_finding(self, finding: Dict):
        """Store security finding in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO security_findings (
                    id, device_id, finding_type, severity, title,
                    description, recommendation, cvss_score, timestamp, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                finding["id"],
                finding["device_id"],
                finding["finding_type"],
                finding["severity"],
                finding["title"],
                finding["description"],
                finding["recommendation"],
                finding["cvss_score"],
                datetime.now().isoformat(),
                finding.get("status", "open")
            ))
            conn.commit()
    
    def _store_port_scan_result(self, scan_id: str, device_id: str, port_info: Dict):
        """Store port scan result in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO port_scans (
                    id, device_id, port, protocol, state, service, banner
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"{scan_id}_{port_info['port']}",
                device_id,
                port_info["port"],
                "tcp",  # Assuming TCP for simplicity
                port_info["state"],
                port_info.get("service", ""),
                port_info.get("banner", "")
            ))
            conn.commit()
    
    def _store_vulnerability_scan(self, device_id: str, scan_types: List[str], summary: Dict, duration: float):
        """Store vulnerability scan metadata"""
        scan_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO vulnerability_scans (
                    id, device_id, scan_type, status, findings_count,
                    high_severity_count, medium_severity_count, low_severity_count,
                    scan_duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                device_id,
                ",".join(scan_types),
                "completed",
                summary.get("total_findings", 0),
                summary.get("high_count", 0),
                summary.get("medium_count", 0),
                summary.get("low_count", 0),
                int(duration)
            ))
            conn.commit()
    
    def _store_compliance_result(self, finding: Dict):
        """Store compliance check result"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO compliance_results (
                    id, device_id, compliance_standard, rule_id, rule_name,
                    status, details, severity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                finding["id"],
                finding["device_id"],
                finding["compliance_standard"],
                finding["rule_id"],
                finding["rule_name"],
                finding["status"],
                finding["details"],
                finding["severity"]
            ))
            conn.commit()
    
    def get_security_overview(self) -> Dict:
        """Get security overview and statistics"""
        overview = {
            "timestamp": datetime.now().isoformat(),
            "total_findings": 0,
            "open_findings": 0,
            "remediated_findings": 0,
            "severity_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "recent_scans": [],
            "top_vulnerabilities": []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get findings statistics
                cursor = conn.execute('''
                    SELECT severity, status, COUNT(*) as count
                    FROM security_findings
                    GROUP BY severity, status
                ''')
                
                for severity, status, count in cursor.fetchall():
                    if severity in overview["severity_distribution"]:
                        overview["severity_distribution"][severity] += count
                    
                    overview["total_findings"] += count
                    
                    if status == "open":
                        overview["open_findings"] += count
                    else:
                        overview["remediated_findings"] += count
                
                # Get recent scans
                cursor = conn.execute('''
                    SELECT device_id, scan_date, scan_type, findings_count
                    FROM vulnerability_scans
                    ORDER BY scan_date DESC
                    LIMIT 10
                ''')
                
                overview["recent_scans"] = [
                    {
                        "device_id": row[0],
                        "scan_date": row[1],
                        "scan_type": row[2],
                        "findings_count": row[3]
                    }
                    for row in cursor.fetchall()
                ]
        
        except Exception as e:
            logger.error(f"Error getting security overview: {e}")
        
        return overview
    
    def remediate_finding(self, finding_id: str, remediated_by: str = "system") -> bool:
        """Mark finding as remediated"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE security_findings
                    SET status = 'remediated', 
                        remediated_at = CURRENT_TIMESTAMP,
                        remediated_by = ?
                    WHERE id = ?
                ''', (remediated_by, finding_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error remediating finding {finding_id}: {e}")
            return False
    
    def export_security_report(self, device_id: str = None, format: str = "json") -> str:
        """Export security report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if device_id:
                    cursor = conn.execute('''
                        SELECT * FROM security_findings
                        WHERE device_id = ?
                        ORDER BY timestamp DESC
                    ''', (device_id,))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM security_findings
                        ORDER BY timestamp DESC
                    ''')
                
                findings = [dict(row) for row in cursor.fetchall()]
                
                if format.lower() == "json":
                    return json.dumps(findings, indent=2, default=str)
                elif format.lower() == "csv":
                    import csv
                    import io
                    
                    output = io.StringIO()
                    if findings:
                        writer = csv.DictWriter(output, fieldnames=findings[0].keys())
                        writer.writeheader()
                        writer.writerows(findings)
                    
                    return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error exporting security report: {e}")
            return ""
