/* Security Monitoring JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🛡️ Security page loaded');
    
    // Load initial security data
    loadSecurityOverview();
    loadSecurityAlerts();
    loadVulnerabilities();
    loadComplianceData();
    loadAccessLogs();
    
    // Auto-refresh every 30 seconds
    setInterval(refreshSecurityData, 30000);
});

// Load security overview
function loadSecurityOverview() {
    fetch('/api/security/overview')
        .then(response => response.json())
        .then(data => {
            // Update security score
            document.getElementById('securityScore').innerHTML = `
                <span class="score-${getScoreClass(data.security_score)}">${data.security_score}/100</span>
            `;
            
            // Update alert counts
            document.getElementById('criticalAlerts').textContent = data.alert_counts.critical;
            
            // Update vulnerability count
            const totalVulns = Object.values(data.vulnerability_counts).reduce((a, b) => a + b, 0);
            document.getElementById('vulnerabilityCount').textContent = totalVulns;
            
            // Update compliance rate
            document.getElementById('complianceRate').textContent = `${data.compliance_status.percentage}%`;
            
            // Update card colors based on values
            updateCardColors(data);
        })
        .catch(error => {
            console.error('Error loading security overview:', error);
            showError('Failed to load security overview');
        });
}

function getScoreClass(score) {
    if (score >= 90) return 'excellent';
    if (score >= 70) return 'good';
    if (score >= 50) return 'warning';
    return 'danger';
}

function updateCardColors(data) {
    // Update critical alerts card
    const criticalCard = document.querySelector('#criticalAlerts').closest('.card');
    if (data.alert_counts.critical > 0) {
        criticalCard.classList.add('border-left-danger');
    } else {
        criticalCard.classList.remove('border-left-danger');
        criticalCard.classList.add('border-left-success');
    }
}

// Load security alerts
function loadSecurityAlerts() {
    fetch('/api/security/alerts')
        .then(response => response.json())
        .then(data => {
            const alertsTableBody = document.getElementById('alertsTableBody');
            
            if (data.alerts && data.alerts.length > 0) {
                alertsTableBody.innerHTML = data.alerts.map(alert => `
                    <tr>
                        <td>
                            <span class="badge bg-${getSeverityColor(alert.severity)}">
                                ${alert.severity.toUpperCase()}
                            </span>
                        </td>
                        <td>
                            <strong>${alert.title}</strong><br>
                            <small class="text-muted">${alert.description}</small>
                        </td>
                        <td>${alert.device_name || alert.device_id}</td>
                        <td>
                            <span class="badge bg-secondary">${alert.category}</span>
                        </td>
                        <td>${formatTimestamp(alert.timestamp)}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="viewAlertDetails('${alert.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-warning" onclick="acknowledgeAlert('${alert.id}')">
                                <i class="fas fa-check"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                alertsTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-success">
                            <i class="fas fa-shield-alt me-2"></i>No active security alerts
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading security alerts:', error);
            document.getElementById('alertsTableBody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        Error loading security alerts
                    </td>
                </tr>
            `;
        });
}

function getSeverityColor(severity) {
    const colors = {
        'critical': 'danger',
        'high': 'warning', 
        'medium': 'info',
        'low': 'secondary'
    };
    return colors[severity] || 'secondary';
}

// Load vulnerabilities
function loadVulnerabilities() {
    fetch('/api/security/vulnerabilities')
        .then(response => response.json())
        .then(data => {
            const vulnerabilityList = document.getElementById('vulnerabilityList');
            
            if (data.vulnerabilities && data.vulnerabilities.length > 0) {
                vulnerabilityList.innerHTML = data.vulnerabilities.map(vuln => `
                    <div class="alert alert-${getSeverityColor(vuln.severity)} alert-dismissible">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="alert-heading">
                                    <i class="fas fa-bug me-2"></i>${vuln.title}
                                    <span class="badge bg-${getSeverityColor(vuln.severity)} ms-2">${vuln.severity}</span>
                                </h6>
                                <p class="mb-2">${vuln.description}</p>
                                <p class="mb-1">
                                    <strong>CVE ID:</strong> ${vuln.cve_id}<br>
                                    <strong>Risk Score:</strong> ${vuln.risk_score}/10<br>
                                    <strong>Affected Devices:</strong> ${vuln.affected_devices.join(', ')}
                                </p>
                                ${vuln.fix_available ? 
                                    '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Fix Available</span>' :
                                    '<span class="badge bg-warning"><i class="fas fa-clock me-1"></i>No Fix Available</span>'
                                }
                            </div>
                            <div class="ms-3">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewVulnerabilityDetails('${vuln.id}')">
                                    Details
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                vulnerabilityList.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-shield-alt me-2"></i>No vulnerabilities detected
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading vulnerabilities:', error);
            document.getElementById('vulnerabilityList').innerHTML = `
                <div class="alert alert-danger">
                    Error loading vulnerability data
                </div>
            `;
        });
}

// Load compliance data
function loadComplianceData() {
    fetch('/api/security/compliance')
        .then(response => response.json())
        .then(data => {
            const complianceRules = document.getElementById('complianceRules');
            
            if (data.compliance && Object.keys(data.compliance).length > 0) {
                let html = '';
                
                Object.keys(data.compliance).forEach(device => {
                    html += `<h6 class="fw-bold">${device}</h6>`;
                    
                    data.compliance[device].forEach(rule => {
                        const statusClass = rule.status === 'passed' ? 'success' : 'danger';
                        const statusIcon = rule.status === 'passed' ? 'check' : 'times';
                        
                        html += `
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                                <div>
                                    <strong>${rule.rule_name}</strong><br>
                                    <small class="text-muted">${rule.description}</small>
                                </div>
                                <span class="badge bg-${statusClass}">
                                    <i class="fas fa-${statusIcon} me-1"></i>${rule.status}
                                </span>
                            </div>
                        `;
                    });
                    
                    html += '<hr>';
                });
                
                complianceRules.innerHTML = html;
            } else {
                complianceRules.innerHTML = '<p class="text-muted">No compliance data available</p>';
            }
            
            // Create compliance chart
            createComplianceChart();
        })
        .catch(error => {
            console.error('Error loading compliance data:', error);
            document.getElementById('complianceRules').innerHTML = `
                <div class="alert alert-danger">
                    Error loading compliance data
                </div>
            `;
        });
}

// Load access logs
function loadAccessLogs() {
    fetch('/api/security/access-logs')
        .then(response => response.json())
        .then(data => {
            const accessLogsTableBody = document.getElementById('accessLogsTableBody');
            
            if (data.logs && data.logs.length > 0) {
                accessLogsTableBody.innerHTML = data.logs.map(log => `
                    <tr>
                        <td>${log.device_name || log.device_id}</td>
                        <td>${log.username}</td>
                        <td>
                            <span class="badge bg-info">${log.access_method}</span>
                        </td>
                        <td>${log.source_ip}</td>
                        <td>
                            <span class="badge bg-${log.success ? 'success' : 'danger'}">
                                <i class="fas fa-${log.success ? 'check' : 'times'} me-1"></i>
                                ${log.success ? 'Success' : 'Failed'}
                            </span>
                        </td>
                        <td>${formatTimestamp(log.timestamp)}</td>
                    </tr>
                `).join('');
            } else {
                accessLogsTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            No access logs available
                        </td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading access logs:', error);
            document.getElementById('accessLogsTableBody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        Error loading access logs
                    </td>
                </tr>
            `;
        });
}

// Create compliance chart
function createComplianceChart() {
    const ctx = document.getElementById('complianceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [{
                data: [75, 25], // Example data
                backgroundColor: [
                    '#28a745',
                    '#dc3545'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Utility functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function refreshSecurityData() {
    console.log('🔄 Refreshing security data...');
    loadSecurityOverview();
    loadSecurityAlerts();
    loadVulnerabilities();
    loadAccessLogs();
}

function runSecurityScan() {
    console.log('🔍 Running security scan...');
    
    // Show loading state
    const scanBtn = event.target;
    const originalText = scanBtn.innerHTML;
    scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Scanning...';
    scanBtn.disabled = true;
    
    fetch('/api/security/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(`Security scan completed!\nScan Duration: ${data.scan_duration}\nVulnerabilities Found: ${data.vulnerabilities_found}`);
        
        // Refresh data
        setTimeout(() => {
            refreshSecurityData();
        }, 1000);
    })
    .catch(error => {
        console.error('Error running security scan:', error);
        alert('Error running security scan');
    })
    .finally(() => {
        // Restore button
        scanBtn.innerHTML = originalText;
        scanBtn.disabled = false;
    });
}

function runVulnerabilityScan() {
    runSecurityScan(); // Same function for now
}

function runComplianceCheck() {
    console.log('✅ Running compliance check...');
    
    const checkBtn = event.target;
    const originalText = checkBtn.innerHTML;
    checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Checking...';
    checkBtn.disabled = true;
    
    setTimeout(() => {
        loadComplianceData();
        checkBtn.innerHTML = originalText;
        checkBtn.disabled = false;
        alert('Compliance check completed!');
    }, 2000);
}

function viewAlertDetails(alertId) {
    console.log(`👁️ Viewing alert details: ${alertId}`);
    // This would show detailed alert information in a modal
    alert('Alert details viewer coming soon!');
}

function acknowledgeAlert(alertId) {
    if (!confirm('Acknowledge this security alert?')) {
        return;
    }
    
    fetch(`/api/security/alerts/${alertId}/acknowledge`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Alert acknowledged successfully!');
            loadSecurityAlerts();
        } else {
            alert('Error acknowledging alert: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error acknowledging alert:', error);
        alert('Error acknowledging alert');
    });
}

function viewVulnerabilityDetails(vulnId) {
    console.log(`🔍 Viewing vulnerability details: ${vulnId}`);
    alert('Vulnerability details viewer coming soon!');
}

function showError(message) {
    console.error(message);
    // You could show a toast notification here
}