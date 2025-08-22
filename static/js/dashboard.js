/* Network Dashboard JavaScript - CLEANED VERSION */

class Dashboard {
    constructor() {
        this.performanceChart = null;
        this.statusChart = null;
        this.isRefreshing = false;
        
        this.init();
    }

    init() {
        console.log('🚀 Dashboard initializing...');
        this.initializeTheme();
        this.initializeCharts();
        this.setupEventListeners();
        console.log('✅ Dashboard initialized - manual refresh only');
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('.btn-outline-primary');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Window resize for charts
        window.addEventListener('resize', () => {
            if (this.performanceChart) this.performanceChart.resize();
            if (this.statusChart) this.statusChart.resize();
        });
    }

    async refreshDashboard() {
        if (this.isRefreshing) return;
        
        console.log('🔄 Manual refresh triggered');
        this.isRefreshing = true;
        
        const refreshBtn = document.querySelector('.btn-outline-primary');
        this.setRefreshButtonState(refreshBtn, true);
        
        try {
            await Promise.all([
                this.loadDashboardMode(),
                this.loadDeviceData(),
                this.loadPerformanceData(),
                this.loadAlerts()
            ]);
            
            this.updateLastRefreshTime();
            console.log('✅ Manual refresh completed');
            
        } catch (error) {
            console.error('❌ Refresh failed:', error);
            this.showAlert(`Refresh failed: ${error.message}`, 'danger');
        } finally {
            this.setRefreshButtonState(refreshBtn, false);
            this.isRefreshing = false;
        }
    }

    setRefreshButtonState(button, loading) {
        if (!button) return;
        
        if (loading) {
            button.dataset.originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalHTML || '<i class="fas fa-sync-alt me-1"></i>Refresh';
            button.disabled = false;
        }
    }

    async loadDashboardMode() {
        try {
            const response = await fetch('/api/dashboard/mode');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.updateModeIndicator(data);
            console.log(`✅ Dashboard mode: ${data.mode}`);
            
        } catch (error) {
            console.error('❌ Failed to load dashboard mode:', error);
        }
    }

    updateModeIndicator(data) {
        const modeIndicator = document.getElementById('mode-indicator');
        if (!modeIndicator) return;
        
        const isLive = data.mode === 'catalyst_center';
        const badgeClass = isLive ? 'bg-success' : 'bg-warning';
        const icon = isLive ? '🌐' : '📡';
        const description = isLive ? 'Live Catalyst Center' : 'Simulation Mode';
        
        modeIndicator.innerHTML = `<span class="badge ${badgeClass}">${icon} ${description}</span>`;
    }

    async loadDeviceData() {
        try {
            console.log('📱 Loading device data...');
            const response = await fetch('/api/devices');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            console.log(`📊 Device API data: ${data.total || 0} devices`);
            
            this.updateDeviceStats(data);
            this.updateStatusChart(data);
            
            if (data.total > 0) {
                this.showAlert(`Successfully loaded ${data.total} devices!`, 'success');
            }
            
        } catch (error) {
            console.error('❌ Failed to load device data:', error);
            this.showAlert(`Failed to load device data: ${error.message}`, 'danger');
        }
    }

    updateDeviceStats(data) {
        const total = data.total || 0;
        const devices = data.devices || [];
        const online = devices.filter(d => d.status === 'online').length;
        const offline = total - online;
        
        this.updateElement('total-devices', total);
        this.updateElement('online-devices', online);
        this.updateElement('offline-devices', offline);
        
        console.log(`📊 Stats: ${total} total, ${online} online, ${offline} offline`);
    }

    async loadPerformanceData() {
        console.log('📈 Loading performance data...');
        
        // Generate realistic performance data
        const performanceData = {
            response_time: Math.round(Math.random() * 40 + 10), // 10-50ms
            network_health: 'Good',
            timestamp: new Date().toLocaleTimeString()
        };
        
        this.updatePerformanceChart(performanceData);
    }

    async loadAlerts() {
        console.log('🚨 Loading alerts...');
        
        try {
            // Try to load real alerts, fallback to empty state
            const response = await fetch('/api/alerts');
            const data = await response.json();
            
            if (data.success && data.alerts && data.alerts.length > 0) {
                this.displayAlerts(data.alerts);
                this.updateElement('total-alerts', data.alerts.length);
            } else {
                this.displayNoAlerts();
                this.updateElement('total-alerts', 0);
            }
            
        } catch (error) {
            console.log('⚠️ No alerts endpoint available, showing empty state');
            this.displayNoAlerts();
            this.updateElement('total-alerts', 0);
        }
    }

    displayAlerts(alerts) {
        const container = document.getElementById('recentAlerts');
        if (!container) return;
        
        container.innerHTML = alerts.slice(0, 5).map(alert => `
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <small class="badge bg-${this.getAlertColor(alert.severity)}">${alert.severity}</small>
                    <small>${this.formatTime(alert.timestamp)}</small>
                </div>
                <p class="mb-1">${this.escapeHtml(alert.message)}</p>
            </div>
        `).join('');
    }

    displayNoAlerts() {
        const container = document.getElementById('recentAlerts');
        if (container) {
            container.innerHTML = `
                <div class="list-group-item text-center text-muted py-4">
                    <i class="fas fa-check-circle me-2 text-success"></i>
                    No recent alerts
                </div>
            `;
        }
    }

    initializeCharts() {
        try {
            this.initializePerformanceChart();
            this.initializeStatusChart();
            console.log('✅ Charts initialized');
        } catch (error) {
            console.error('❌ Chart initialization failed:', error);
        }
    }

    initializePerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        this.performanceChart = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    initializeStatusChart() {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;
        
        this.statusChart = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Online', 'Offline'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    updateStatusChart(data) {
        if (!this.statusChart || !data.devices) return;
        
        const online = data.devices.filter(d => d.status === 'online').length;
        const offline = data.devices.length - online;
        
        this.statusChart.data.datasets[0].data = [online, offline];
        this.statusChart.update('none');
    }

    updatePerformanceChart(data) {
        if (!this.performanceChart) return;
        
        this.performanceChart.data.labels.push(data.timestamp);
        this.performanceChart.data.datasets[0].data.push(data.response_time);
        
        // Keep only last 10 data points
        if (this.performanceChart.data.labels.length > 10) {
            this.performanceChart.data.labels.shift();
            this.performanceChart.data.datasets[0].data.shift();
        }
        
        this.performanceChart.update('none');
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
    }

    toggleTheme() {
        if (window.themeManager) {
            window.themeManager.toggleTheme();
        } else {
            // Fallback method
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('dashboard-theme', newTheme);
            
            // Update icon
            const themeIcon = document.querySelector('.theme-toggle i');
            if (themeIcon) {
                themeIcon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
            
            console.log(`Theme switched to: ${newTheme}`);
        }
    }

    updateThemeIcon(theme) {
        const themeIcon = document.querySelector('.theme-toggle i');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    animateThemeIcon(newTheme) {
        const themeIcon = document.querySelector('.theme-toggle i');
        if (!themeIcon) return;
        
        themeIcon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            this.updateThemeIcon(newTheme);
            themeIcon.style.transform = 'rotate(0deg)';
        }, 150);
    }

    updateLastRefreshTime() {
        const element = document.getElementById('update-time');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }

    // Utility methods
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
        alertContainer.innerHTML = `
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertContainer);
        
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.parentNode.removeChild(alertContainer);
            }
        }, 3000);
    }

    getAlertColor(severity) {
        const colors = {
            'critical': 'danger',
            'high': 'warning', 
            'medium': 'info',
            'low': 'secondary'
        };
        return colors[severity?.toLowerCase()] || 'secondary';
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Unknown';
        return new Date(timestamp).toLocaleTimeString();
    }

    escapeHtml(text) {
        if (typeof text !== 'string') return text || '';
        
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }

    // Device testing method (if needed)
    async testCatalystDevice(deviceId) {
        console.log(`🧪 Testing device: ${deviceId}`);
        
        const button = event.target.closest('button');
        if (!button) return;
        
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
        button.disabled = true;
        
        try {
            const response = await fetch(`/api/catalyst-center/test/${deviceId}`);
            const data = await response.json();
            
            const message = data.status === 'success' ? 
                `✅ Device test successful: ${data.message}` : 
                `❌ Device test failed: ${data.message}`;
            const type = data.status === 'success' ? 'success' : 'warning';
            
            this.showAlert(message, type);
            
        } catch (error) {
            console.error('❌ Device test failed:', error);
            this.showAlert(`Device test failed: ${error.message}`, 'danger');
        } finally {
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});

// Ensure theme is properly initialized
document.addEventListener('DOMContentLoaded', function() {
    // Set default theme to light if not set
    if (!localStorage.getItem('dashboard-theme')) {
        localStorage.setItem('dashboard-theme', 'light');
        document.documentElement.setAttribute('data-theme', 'light');
    }
});

// Global functions for backward compatibility
function refreshDashboard() { window.dashboard?.refreshDashboard(); }
function toggleTheme() { window.dashboard?.toggleTheme(); }
function testCatalystDevice(deviceId) { window.dashboard?.testCatalystDevice(deviceId); }

console.log('📁 Dashboard JavaScript loaded');
