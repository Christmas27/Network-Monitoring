/**
 * Devices Page JavaScript - Network Dashboard
 * Handles device management, testing, and display functionality
 */

/* Device Management JavaScript - CLEANED VERSION */

class DeviceManager {
    constructor() {
        this.currentView = 'card';
        this.devices = [];
        this.init();
    }

    init() {
        console.log('📱 Devices page loaded');
        this.setupEventListeners();
        this.loadDevices();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshDevices()"]');
        if (refreshBtn) {
            refreshBtn.removeAttribute('onclick');
            refreshBtn.addEventListener('click', () => this.refreshDevices());
        }

        // View toggle buttons
        const cardViewBtn = document.getElementById('card-view-btn');
        const tableViewBtn = document.getElementById('table-view-btn');

        if (cardViewBtn) {
            cardViewBtn.removeAttribute('onclick');
            cardViewBtn.addEventListener('click', () => this.switchView('card'));
        }

        if (tableViewBtn) {
            tableViewBtn.removeAttribute('onclick');
            tableViewBtn.addEventListener('click', () => this.switchView('table'));
        }

        // Add device modal
        const addDeviceBtn = document.querySelector('[data-bs-target="#addDeviceModal"]');
        if (addDeviceBtn) {
            addDeviceBtn.addEventListener('click', () => console.log('📝 Opening add device modal'));
        }
    }

    async loadDevices() {
        console.log('📡 Fetching devices from Catalyst Center...');
        
        try {
            this.showLoadingState();
            
            const response = await fetch('/api/devices');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Received device data:', data);
            
            this.devices = data.devices || [];
            this.updateDeviceStats(data);
            this.displayDevices();
            this.updateDeviceCountBadge(data.total || 0);
            
            console.log(`✅ Successfully loaded ${data.total || 0} devices`);
            
        } catch (error) {
            console.error('❌ Error loading devices:', error);
            this.showError(`Failed to load devices: ${error.message}`);
        }
    }

    updateDeviceStats(data) {
        const total = data.total || 0;
        const online = this.devices.filter(d => d.status === 'online').length;
        const offline = total - online;
        const types = new Set(this.devices.map(d => d.type)).size;

        this.updateElement('totalDevices', total);
        this.updateElement('onlineDevices', online);
        this.updateElement('offlineDevices', offline);
        this.updateElement('deviceTypes', types);

        console.log(`📊 Stats: ${total} total, ${online} online, ${offline} offline, ${types} types`);
    }

    updateDeviceCountBadge(count) {
        this.updateElement('device-count-badge', `<i class="fas fa-hashtag me-1"></i>${count} Devices`);
    }

    displayDevices() {
        if (this.currentView === 'card') {
            this.displayDeviceCards();
        } else {
            this.displayDeviceTable();
        }
    }

    displayDeviceCards() {
        const container = document.getElementById('device-cards-container');
        if (!container) return;

        if (!this.devices || this.devices.length === 0) {
            container.innerHTML = this.getNoDevicesHTML();
            this.setupRetryButton();
            return;
        }

        container.innerHTML = '';
        this.devices.forEach(device => {
            const deviceCard = this.createDeviceCard(device);
            container.appendChild(deviceCard);
        });

        console.log(`✅ Displayed ${this.devices.length} devices in card view`);
    }

    createDeviceCard(device) {
        const deviceCard = document.createElement('div');
        deviceCard.className = 'col-xl-3 col-lg-4 col-md-6';
        
        const statusBadge = this.getStatusBadge(device.status);
        
        deviceCard.innerHTML = `
            <div class="card h-100 border-0 shadow-sm device-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="d-flex align-items-center">
                            <div class="device-icon me-3">
                                <i class="fas fa-network-wired text-primary"></i>
                            </div>
                            <div>
                                <h6 class="card-title mb-0 fw-bold">${this.escapeHtml(device.name)}</h6>
                                <small class="text-muted">${this.escapeHtml(device.role || device.type)}</small>
                            </div>
                        </div>
                        ${statusBadge}
                    </div>
                    
                    <div class="device-details mb-3">
                        <div class="detail-item mb-2">
                            <i class="fas fa-globe text-muted me-2"></i>
                            <span class="fw-medium">${this.escapeHtml(device.host || device.ip)}</span>
                        </div>
                        <div class="detail-item mb-2">
                            <i class="fas fa-microchip text-muted me-2"></i>
                            <span class="small">${this.escapeHtml(device.type)}</span>
                        </div>
                        ${device.series ? `
                        <div class="detail-item mb-2">
                            <i class="fas fa-tag text-muted me-2"></i>
                            <span class="small">${this.escapeHtml(device.series)}</span>
                        </div>` : ''}
                    </div>
                    
                    ${device.description ? `
                    <div class="device-model mb-3 p-2 bg-light rounded">
                        <small class="text-muted">${this.escapeHtml(device.description)}</small>
                    </div>` : ''}
                    
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-primary btn-sm test-device-btn" data-device-id="${device.id}">
                            <i class="fas fa-stethoscope me-1"></i>Test Connection
                        </button>
                    </div>
                </div>
                
                <div class="card-footer bg-transparent border-top-0 px-3 pb-3">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>
                        Last checked: ${this.formatTime(device.last_check)}
                    </small>
                </div>
            </div>
        `;
        
        // Add event listener to test button
        const testBtn = deviceCard.querySelector('.test-device-btn');
        if (testBtn) {
            testBtn.addEventListener('click', (e) => this.testDevice(device.id, e.target));
        }
        
        return deviceCard;
    }

    displayDeviceTable() {
        const tbody = document.getElementById('device-table-body');
        if (!tbody) return;

        if (!this.devices || this.devices.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center py-4 text-muted">
                        <i class="fas fa-server fa-2x mb-2"></i><br>
                        No devices found
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = '';
        this.devices.forEach(device => {
            const row = this.createDeviceTableRow(device);
            tbody.appendChild(row);
        });

        console.log(`✅ Displayed ${this.devices.length} devices in table view`);
    }

    createDeviceTableRow(device) {
        const row = document.createElement('tr');
        const statusBadge = this.getStatusBadge(device.status);
        
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-network-wired text-primary me-2"></i>
                    <strong>${this.escapeHtml(device.name)}</strong>
                </div>
            </td>
            <td>${this.escapeHtml(device.host || device.ip)}</td>
            <td>${this.escapeHtml(device.type)}</td>
            <td><span class="badge bg-light text-dark">${this.escapeHtml(device.role || 'N/A')}</span></td>
            <td><small>${this.escapeHtml(device.series || 'N/A')}</small></td>
            <td>${statusBadge}</td>
            <td><small>${this.formatTime(device.last_check)}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary test-device-btn" data-device-id="${device.id}" title="Test Connection">
                        <i class="fas fa-plug"></i>
                    </button>
                    <button class="btn btn-outline-info view-details-btn" data-device-id="${device.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </td>
        `;
        
        // Add event listeners
        const testBtn = row.querySelector('.test-device-btn');
        const viewBtn = row.querySelector('.view-details-btn');
        
        if (testBtn) {
            testBtn.addEventListener('click', (e) => this.testDevice(device.id, e.target));
        }
        
        if (viewBtn) {
            viewBtn.addEventListener('click', () => this.viewDetails(device.id));
        }
        
        return row;
    }

    switchView(view) {
        this.currentView = view;
        
        // Toggle view containers
        document.getElementById('card-view').style.display = view === 'card' ? 'block' : 'none';
        document.getElementById('table-view').style.display = view === 'table' ? 'block' : 'none';
        
        // Update button states
        const cardBtn = document.getElementById('card-view-btn');
        const tableBtn = document.getElementById('table-view-btn');
        
        cardBtn.className = `btn btn-outline-${view === 'card' ? 'primary' : 'secondary'} btn-sm`;
        tableBtn.className = `btn btn-outline-${view === 'table' ? 'primary' : 'secondary'} btn-sm`;
        
        this.displayDevices();
        console.log(`🔄 Switched to ${view} view`);
    }

    async testDevice(deviceId, buttonElement) {
        console.log(`🧪 Testing device: ${deviceId}`);
        
        if (!buttonElement) return;
        
        const originalHTML = buttonElement.innerHTML;
        const originalClass = buttonElement.className;
        
        // Show loading state
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
        buttonElement.disabled = true;
        
        try {
            const response = await fetch(`/api/catalyst-center/test/${deviceId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('🧪 Device test result:', data);
            
            if (data.status === 'success') {
                this.showTestResult(this.createSuccessAlert(data), 'success');
                this.setButtonState(buttonElement, 'success', '<i class="fas fa-check me-1"></i>Success!');
            } else {
                this.showTestResult(this.createErrorAlert(data), 'error');
                this.setButtonState(buttonElement, 'danger', '<i class="fas fa-times me-1"></i>Failed');
            }
            
        } catch (error) {
            console.error('❌ Device test failed:', error);
            this.showTestResult(this.createGenericErrorAlert(error), 'error');
            this.setButtonState(buttonElement, 'danger', '<i class="fas fa-exclamation-triangle me-1"></i>Error');
        }
        
        // Reset button after 3 seconds
        setTimeout(() => {
            buttonElement.innerHTML = originalHTML;
            buttonElement.className = originalClass;
            buttonElement.disabled = false;
        }, 3000);
    }

    setButtonState(button, type, content) {
        button.innerHTML = content;
        button.className = button.className.replace(/btn-\w+/g, '').trim() + ` btn-${type}`;
    }

    refreshDevices() {
        console.log('🔄 Refreshing devices...');
        this.loadDevices();
    }

    viewDetails(deviceId) {
        console.log(`👁️ Viewing details for device: ${deviceId}`);
        this.showAlert('Device details functionality coming soon!', 'info');
    }

    // Utility methods
    getStatusBadge(status) {
        return status === 'online' ? 
            '<span class="badge bg-success"><i class="fas fa-check-circle me-1"></i>Online</span>' : 
            '<span class="badge bg-danger"><i class="fas fa-times-circle me-1"></i>Offline</span>';
    }

    getNoDevicesHTML() {
        return `
            <div class="col-12 text-center py-5">
                <i class="fas fa-server fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No devices found</h5>
                <p class="text-muted">Check your Catalyst Center connection</p>
                <button class="btn btn-outline-primary" id="retry-btn">
                    <i class="fas fa-sync-alt me-1"></i>Refresh
                </button>
            </div>
        `;
    }

    setupRetryButton() {
        const retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.refreshDevices());
        }
    }

    showLoadingState() {
        const container = document.getElementById('device-cards-container');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-spinner fa-spin fa-2x text-muted mb-3"></i>
                    <p class="text-muted">Loading devices from Catalyst Center...</p>
                </div>
            `;
        }
    }

    showError(message) {
        const container = document.getElementById('device-cards-container');
        if (container) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h5 class="text-danger">Error</h5>
                    <p class="text-muted">${this.escapeHtml(message)}</p>
                    <button class="btn btn-outline-primary" id="error-retry-btn">
                        <i class="fas fa-sync-alt me-1"></i>Try Again
                    </button>
                </div>
            `;
            
            const retryBtn = document.getElementById('error-retry-btn');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => this.refreshDevices());
            }
        }
    }

    showTestResult(html, type) {
        let container = document.getElementById('test-results-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'test-results-container';
            container.className = 'position-fixed';
            container.style.cssText = 'top: 20px; right: 20px; z-index: 1055; max-width: 400px;';
            document.body.appendChild(container);
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = html;
        container.appendChild(alertDiv.firstElementChild);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            const alerts = container.querySelectorAll('.alert');
            if (alerts.length > 0) {
                alerts[0].remove();
            }
        }, 10000);
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
        }, 5000);
    }

    // Alert creators
    createSuccessAlert(data) {
        return `
            <div class="alert alert-success alert-dismissible fade show">
                <strong><i class="fas fa-check-circle me-2"></i>Connection Successful!</strong><br>
                <strong>Device:</strong> ${this.escapeHtml(data.details.device_name)}<br>
                <strong>IP:</strong> ${this.escapeHtml(data.details.ip_address)}<br>
                <strong>Response Time:</strong> ${this.escapeHtml(data.details.response_time)}<br>
                <small class="text-muted">Test completed at ${this.formatTime(data.details.timestamp)}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    createErrorAlert(data) {
        return `
            <div class="alert alert-danger alert-dismissible fade show">
                <strong><i class="fas fa-times-circle me-2"></i>Connection Failed!</strong><br>
                <strong>Error:</strong> ${this.escapeHtml(data.message)}<br>
                ${data.details ? `<strong>Device:</strong> ${this.escapeHtml(data.details.device_name)}<br>` : ''}
                ${data.details ? `<strong>IP:</strong> ${this.escapeHtml(data.details.ip_address)}<br>` : ''}
                <small class="text-muted">Test completed at ${this.formatTime(new Date().toISOString())}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    createGenericErrorAlert(error) {
        return `
            <div class="alert alert-danger alert-dismissible fade show">
                <strong><i class="fas fa-exclamation-triangle me-2"></i>Test Error!</strong><br>
                Failed to test device connection: ${this.escapeHtml(error.message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }

    // Utility functions
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            if (typeof content === 'string' && content.includes('<')) {
                element.innerHTML = content;
            } else {
                element.textContent = content;
            }
        }
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Never';
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
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.deviceManager = new DeviceManager();
});

// Global functions for backward compatibility
function refreshDevices() { window.deviceManager?.refreshDevices(); }
function switchToCardView() { window.deviceManager?.switchView('card'); }
function switchToTableView() { window.deviceManager?.switchView('table'); }
function testDevice(deviceId, button) { window.deviceManager?.testDevice(deviceId, button); }
function viewDetails(deviceId) { window.deviceManager?.viewDetails(deviceId); }
function addDevice() { console.log('Add device functionality coming soon!'); }

console.log('📱 Device Management JavaScript loaded');