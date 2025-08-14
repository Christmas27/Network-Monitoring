/* Security Monitoring JavaScript - CLEANED VERSION */

class SecurityDashboard {
    constructor() {
        this.refreshInterval = null;
        this.init();
    }

    init() {
        console.log('🛡️ Security page loaded');
        this.loadAllSecurityData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
        
        // Manual refresh only - no auto-refresh
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.loadAllSecurityData();
            }
        });
    }

    async loadAllSecurityData() {
        try {
            await Promise.all([
                this.loadSecurityOverview(),
                this.loadSecurityAlerts(),
                this.loadVulnerabilities(),
                this.loadComplianceData(),
                this.loadAccessLogs()
            ]);
        } catch (error) {
            console.error('Error loading security data:', error);
            this.showError('Failed to load security data');
        }
    }

    async loadSecurityOverview() {
        try {
            const data = await this.fetchData('/api/security/overview');
            this.updateOverviewCards(data);
        } catch (error) {
            console.error('Error loading security overview:', error);
            this.showError('Failed to load security overview');
        }
    }

    async loadSecurityAlerts() {
        try {
            const data = await this.fetchData('/api/security/alerts');
            this.updateAlertsTable(data.alerts);
        } catch (error) {
            console.error('Error loading security alerts:', error);
            this.updateTableError('alertsTableBody', 'Error loading security alerts');
        }
    }

    async loadVulnerabilities() {
        try {
            const data = await this.fetchData('/api/security/vulnerabilities');
            this.updateVulnerabilityList(data.vulnerabilities);
        } catch (error) {
            console.error('Error loading vulnerabilities:', error);
            this.updateElementError('vulnerabilityList', 'Error loading vulnerability data');
        }
    }

    async loadComplianceData() {
        try {
            const data = await this.fetchData('/api/security/compliance');
            this.updateComplianceRules(data.compliance);
            this.createComplianceChart();
        } catch (error) {
            console.error('Error loading compliance data:', error);
            this.updateElementError('complianceRules', 'Error loading compliance data');
        }
    }

    async loadAccessLogs() {
        try {
            const data = await this.fetchData('/api/security/access-logs');
            this.updateAccessLogsTable(data.logs);
        } catch (error) {
            console.error('Error loading access logs:', error);
            this.updateTableError('accessLogsTableBody', 'Error loading access logs');
        }
    }

    // Utility method for API calls
    async fetchData(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    }

    // Update methods (shortened for brevity)
    updateOverviewCards(data) {
        this.updateElement('securityScore', `<span class="score-${this.getScoreClass(data.security_score)}">${data.security_score}/100</span>`);
        this.updateElement('criticalAlerts', data.alert_counts.critical);
        this.updateElement('vulnerabilityCount', Object.values(data.vulnerability_counts).reduce((a, b) => a + b, 0));
        this.updateElement('complianceRate', `${data.compliance_status.percentage}%`);
    }

    updateAlertsTable(alerts) {
        const tbody = document.getElementById('alertsTableBody');
        if (!alerts || alerts.length === 0) {
            tbody.innerHTML = this.getNoDataRow(6, 'No active security alerts', 'success');
            return;
        }
        
        tbody.innerHTML = alerts.map(alert => this.createAlertRow(alert)).join('');
    }

    // Utility methods
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = content;
        }
    }

    updateElementError(id, message) {
        this.updateElement(id, `<div class="alert alert-danger">${message}</div>`);
    }

    updateTableError(id, message) {
        const tbody = document.getElementById(id);
        if (tbody) {
            const colCount = tbody.closest('table').querySelectorAll('thead th').length;
            tbody.innerHTML = this.getNoDataRow(colCount, message, 'danger');
        }
    }

    getNoDataRow(colCount, message, type = 'muted') {
        const iconClass = type === 'success' ? 'fa-shield-alt' : type === 'danger' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        return `<tr><td colspan="${colCount}" class="text-center text-${type}"><i class="fas ${iconClass} me-2"></i>${message}</td></tr>`;
    }

    createAlertRow(alert) {
        return `
            <tr>
                <td><span class="badge bg-${this.getSeverityColor(alert.severity)}">${alert.severity.toUpperCase()}</span></td>
                <td><strong>${alert.title}</strong><br><small class="text-muted">${alert.description}</small></td>
                <td>${alert.device_name || alert.device_id}</td>
                <td><span class="badge bg-secondary">${alert.category}</span></td>
                <td>${this.formatTimestamp(alert.timestamp)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="securityDashboard.viewAlertDetails('${alert.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="securityDashboard.acknowledgeAlert('${alert.id}')">
                        <i class="fas fa-check"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    // Action methods
    async acknowledgeAlert(alertId) {
        if (!confirm('Acknowledge this security alert?')) return;
        
        try {
            const data = await this.fetchData(`/api/security/alerts/${alertId}/acknowledge`, { method: 'POST' });
            if (data.success) {
                this.showAlert('Alert acknowledged successfully!', 'success');
                this.loadSecurityAlerts();
            }
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            this.showAlert('Error acknowledging alert', 'danger');
        }
    }

    async runSecurityScan() {
        console.log('🔍 Running security scan...');
        // Implementation here...
    }

    // Utility methods
    getSeverityColor(severity) {
        const colors = { 'critical': 'danger', 'high': 'warning', 'medium': 'info', 'low': 'secondary' };
        return colors[severity] || 'secondary';
    }

    getScoreClass(score) {
        if (score >= 90) return 'excellent';
        if (score >= 70) return 'good';
        if (score >= 50) return 'warning';
        return 'danger';
    }

    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    showAlert(message, type = 'info') {
        // Toast notification implementation
        console.log(`${type.toUpperCase()}: ${message}`);
    }

    showError(message) {
        console.error(message);
        this.showAlert(message, 'danger');
    }

    cleanup() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.securityDashboard = new SecurityDashboard();
});

// Global functions for backward compatibility
function refreshSecurityData() { window.securityDashboard?.loadAllSecurityData(); }
function runSecurityScan() { window.securityDashboard?.runSecurityScan(); }
function acknowledgeAlert(alertId) { window.securityDashboard?.acknowledgeAlert(alertId); }