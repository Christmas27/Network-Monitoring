/**
 * Devices Page JavaScript - Network Dashboard
 * Handles device management, testing, and display functionality
 */

// Global variables
let currentView = 'card'; // 'card' or 'table'

// Initialize devices page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 Devices page loading...');
    initializeDevicesPage();
});

/**
 * Initialize the devices page
 */
function initializeDevicesPage() {
    console.log('🚀 Initializing devices page...');
    
    // Load devices from Catalyst Center
    loadDevices();
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('✅ Devices page initialized');
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.querySelector('[onclick="refreshDevices()"]');
    if (refreshBtn) {
        refreshBtn.removeAttribute('onclick');
        refreshBtn.addEventListener('click', refreshDevices);
    }
    
    // Add device button
    const addDeviceBtn = document.querySelector('[data-bs-target="#addDeviceModal"]');
    if (addDeviceBtn) {
        addDeviceBtn.addEventListener('click', function() {
            console.log('📝 Opening add device modal...');
        });
    }
    
    // View toggle buttons
    const cardViewBtn = document.getElementById('card-view-btn');
    const tableViewBtn = document.getElementById('table-view-btn');
    
    if (cardViewBtn) {
        cardViewBtn.removeAttribute('onclick');
        cardViewBtn.addEventListener('click', switchToCardView);
    }
    
    if (tableViewBtn) {
        tableViewBtn.removeAttribute('onclick');
        tableViewBtn.addEventListener('click', switchToTableView);
    }
    
    console.log('✅ Event listeners set up');
}

/**
 * Main function to load devices from Catalyst Center
 */
function loadDevices() {
    console.log('📡 Fetching devices from Catalyst Center...');
    
    // Show loading state
    showLoadingState();
    
    fetch('/api/devices')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Received device data:', data);
            
            // Update statistics
            updateDeviceStats(data);
            
            // Display devices based on current view
            if (currentView === 'card') {
                displayDeviceCards(data.devices);
            } else {
                displayDeviceTable(data.devices);
            }
            
            // Update device count badge
            updateDeviceCountBadge(data.total || 0);
            
            console.log(`✅ Successfully loaded ${data.total || 0} devices`);
        })
        .catch(error => {
            console.error('❌ Error loading devices:', error);
            showError('Failed to load devices from Catalyst Center: ' + error.message);
        });
}

/**
 * Show loading state
 */
function showLoadingState() {
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

/**
 * Update device statistics cards
 */
function updateDeviceStats(data) {
    const total = data.total || 0;
    const devices = data.devices || [];
    
    const online = devices.filter(d => d.status === 'online').length;
    const offline = total - online;
    const types = new Set(devices.map(d => d.type)).size;
    
    // Update DOM elements
    updateElementText('totalDevices', total);
    updateElementText('onlineDevices', online);
    updateElementText('offlineDevices', offline);
    updateElementText('deviceTypes', types);
    
    console.log(`📊 Stats updated: ${total} total, ${online} online, ${offline} offline, ${types} types`);
}

/**
 * Update device count badge
 */
function updateDeviceCountBadge(count) {
    const badge = document.getElementById('device-count-badge');
    if (badge) {
        badge.innerHTML = `<i class="fas fa-hashtag me-1"></i>${count} Devices`;
    }
}

/**
 * Display devices as cards
 */
function displayDeviceCards(devices) {
    const container = document.getElementById('device-cards-container');
    
    if (!devices || devices.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-server fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No devices found</h5>
                <p class="text-muted">Check your Catalyst Center connection</p>
                <button class="btn btn-outline-primary" id="retry-btn">
                    <i class="fas fa-sync-alt me-1"></i>Refresh
                </button>
            </div>
        `;
        
        // Add event listener to retry button
        const retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', refreshDevices);
        }
        
        return;
    }
    
    container.innerHTML = '';
    
    devices.forEach(device => {
        const deviceCard = createDeviceCard(device);
        container.appendChild(deviceCard);
    });
    
    console.log(`✅ Displayed ${devices.length} devices in card view`);
}

/**
 * Create a device card element
 */
function createDeviceCard(device) {
    const deviceCard = document.createElement('div');
    deviceCard.className = 'col-xl-3 col-lg-4 col-md-6';
    
    const statusBadge = device.status === 'online' ? 
        '<span class="badge bg-success"><i class="fas fa-check-circle me-1"></i>Online</span>' : 
        '<span class="badge bg-danger"><i class="fas fa-times-circle me-1"></i>Offline</span>';
    
    deviceCard.innerHTML = `
        <div class="card h-100 border-0 shadow-sm device-card">
            <div class="card-body">
                <!-- Device Header -->
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div class="d-flex align-items-center">
                        <div class="device-icon me-3">
                            <i class="fas fa-network-wired text-primary"></i>
                        </div>
                        <div>
                            <h6 class="card-title mb-0 fw-bold">${escapeHtml(device.name)}</h6>
                            <small class="text-muted">${escapeHtml(device.role)}</small>
                        </div>
                    </div>
                    ${statusBadge}
                </div>
                
                <!-- Device Details -->
                <div class="device-details mb-3">
                    <div class="detail-item mb-2">
                        <i class="fas fa-globe text-muted me-2"></i>
                        <span class="fw-medium">${escapeHtml(device.host)}</span>
                    </div>
                    <div class="detail-item mb-2">
                        <i class="fas fa-microchip text-muted me-2"></i>
                        <span class="small">${escapeHtml(device.type)}</span>
                    </div>
                    <div class="detail-item mb-2">
                        <i class="fas fa-tag text-muted me-2"></i>
                        <span class="small">${escapeHtml(device.series)}</span>
                    </div>
                </div>
                
                <!-- Device Description -->
                <div class="device-model mb-3 p-2 bg-light rounded">
                    <small class="text-muted">${escapeHtml(device.description)}</small>
                </div>
                
                <!-- Action Buttons -->
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-primary btn-sm test-device-btn" data-device-id="${device.id}">
                        <i class="fas fa-stethoscope me-1"></i>Test Connection
                    </button>
                </div>
            </div>
            
            <!-- Card Footer -->
            <div class="card-footer bg-transparent border-top-0 px-3 pb-3">
                <small class="text-muted">
                    <i class="fas fa-clock me-1"></i>
                    Last checked: ${new Date(device.last_check).toLocaleTimeString()}
                </small>
            </div>
        </div>
    `;
    
    // Add event listener to test button
    const testBtn = deviceCard.querySelector('.test-device-btn');
    if (testBtn) {
        testBtn.addEventListener('click', function() {
            testDevice(device.id, this);
        });
    }
    
    return deviceCard;
}

/**
 * Display devices as table
 */
function displayDeviceTable(devices) {
    const tbody = document.getElementById('device-table-body');
    
    if (!devices || devices.length === 0) {
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
    
    devices.forEach(device => {
        const statusBadge = device.status === 'online' ? 
            '<span class="badge bg-success">Online</span>' : 
            '<span class="badge bg-danger">Offline</span>';
        
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="fas fa-network-wired text-primary me-2"></i>
                    <strong>${escapeHtml(device.name)}</strong>
                </div>
            </td>
            <td>${escapeHtml(device.host)}</td>
            <td>${escapeHtml(device.type)}</td>
            <td><span class="badge bg-light text-dark">${escapeHtml(device.role)}</span></td>
            <td><small>${escapeHtml(device.series)}</small></td>
            <td>${statusBadge}</td>
            <td><small>${new Date(device.last_check).toLocaleTimeString()}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary test-device-table-btn" data-device-id="${device.id}" title="Test Connection">
                        <i class="fas fa-plug"></i>
                    </button>
                    <button class="btn btn-outline-info view-details-btn" data-device-id="${device.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            </td>
        `;
        
        // Add event listeners to action buttons
        const testBtn = row.querySelector('.test-device-table-btn');
        const viewBtn = row.querySelector('.view-details-btn');
        
        if (testBtn) {
            testBtn.addEventListener('click', function() {
                testDevice(device.id, this);
            });
        }
        
        if (viewBtn) {
            viewBtn.addEventListener('click', function() {
                viewDetails(device.id);
            });
        }
    });
    
    console.log(`✅ Displayed ${devices.length} devices in table view`);
}

/**
 * Switch to card view
 */
function switchToCardView() {
    currentView = 'card';
    document.getElementById('card-view').style.display = 'block';
    document.getElementById('table-view').style.display = 'none';
    
    document.getElementById('card-view-btn').className = 'btn btn-outline-primary btn-sm';
    document.getElementById('table-view-btn').className = 'btn btn-outline-secondary btn-sm';
    
    loadDevices(); // Reload in card view
    console.log('🔄 Switched to card view');
}

/**
 * Switch to table view
 */
function switchToTableView() {
    currentView = 'table';
    document.getElementById('card-view').style.display = 'none';
    document.getElementById('table-view').style.display = 'block';
    
    document.getElementById('card-view-btn').className = 'btn btn-outline-secondary btn-sm';
    document.getElementById('table-view-btn').className = 'btn btn-outline-primary btn-sm';
    
    loadDevices(); // Reload in table view
    console.log('🔄 Switched to table view');
}

/**
 * Refresh devices
 */
function refreshDevices() {
    console.log('🔄 Refreshing devices...');
    loadDevices();
}

/**
 * Test device connection
 */
function testDevice(deviceId, buttonElement) {
    console.log(`🧪 Testing device: ${deviceId}`);
    
    if (!buttonElement) {
        console.error('❌ Button element not provided for device test');
        return;
    }
    
    const originalHTML = buttonElement.innerHTML;
    
    // Show loading state
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
    buttonElement.disabled = true;
    buttonElement.classList.add('btn-loading');
    
    fetch(`/api/catalyst-center/test/${deviceId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('🧪 Device test result:', data);
            
            if (data.status === 'success') {
                showTestResult(`
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <strong><i class="fas fa-check-circle me-2"></i>Connection Successful!</strong><br>
                        <strong>Device:</strong> ${escapeHtml(data.details.device_name)}<br>
                        <strong>IP:</strong> ${escapeHtml(data.details.ip_address)}<br>
                        <strong>Response Time:</strong> ${escapeHtml(data.details.response_time)}<br>
                        <small class="text-muted">Test completed at ${new Date(data.details.timestamp).toLocaleTimeString()}</small>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `, 'success');
                
                // Briefly show success on button
                buttonElement.innerHTML = '<i class="fas fa-check me-1"></i>Success!';
                buttonElement.classList.remove('btn-outline-primary');
                buttonElement.classList.add('btn-success');
                
            } else {
                showTestResult(`
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <strong><i class="fas fa-times-circle me-2"></i>Connection Failed!</strong><br>
                        <strong>Error:</strong> ${escapeHtml(data.message)}<br>
                        ${data.details ? `<strong>Device:</strong> ${escapeHtml(data.details.device_name)}<br>` : ''}
                        ${data.details ? `<strong>IP:</strong> ${escapeHtml(data.details.ip_address)}<br>` : ''}
                        <small class="text-muted">Test completed at ${new Date().toLocaleTimeString()}</small>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `, 'error');
                
                // Briefly show error on button
                buttonElement.innerHTML = '<i class="fas fa-times me-1"></i>Failed';
                buttonElement.classList.remove('btn-outline-primary');
                buttonElement.classList.add('btn-danger');
            }
        })
        .catch(error => {
            console.error('❌ Device test failed:', error);
            showTestResult(`
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <strong><i class="fas fa-exclamation-triangle me-2"></i>Test Error!</strong><br>
                    Failed to test device connection: ${escapeHtml(error.message)}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `, 'error');
            
            buttonElement.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Error';
            buttonElement.classList.remove('btn-outline-primary');
            buttonElement.classList.add('btn-danger');
        })
        .finally(() => {
            // Reset button after 3 seconds
            setTimeout(() => {
                buttonElement.innerHTML = originalHTML;
                buttonElement.disabled = false;
                buttonElement.classList.remove('btn-loading', 'btn-success', 'btn-danger');
                buttonElement.classList.add('btn-outline-primary');
            }, 3000);
        });
}

/**
 * View device details
 */
function viewDetails(deviceId) {
    console.log(`👁️ Viewing details for device: ${deviceId}`);
    // TODO: Implement device details modal or page
    showAlert('Device details functionality coming soon!', 'info');
}

/**
 * Add new device
 */
function addDevice() {
    console.log('➕ Adding new device...');
    
    // Get form data
    const formData = {
        name: document.getElementById('deviceName').value,
        host: document.getElementById('deviceHost').value,
        type: document.getElementById('deviceType').value,
        vendor: document.getElementById('deviceVendor').value,
        username: document.getElementById('deviceUsername').value,
        password: document.getElementById('devicePassword').value,
        port: document.getElementById('devicePort').value || 22
    };
    
    // Validate form data
    if (!formData.name || !formData.host || !formData.type || !formData.vendor) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    // TODO: Send to backend API
    console.log('📝 Form data:', formData);
    showAlert('Add device functionality coming soon!', 'info');
}

/**
 * Show test result notification
 */
function showTestResult(html, type) {
    let resultContainer = document.getElementById('test-results-container');
    if (!resultContainer) {
        resultContainer = document.createElement('div');
        resultContainer.id = 'test-results-container';
        resultContainer.className = 'position-fixed';
        resultContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1055; max-width: 400px;';
        document.body.appendChild(resultContainer);
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = html;
    resultContainer.appendChild(alertDiv.firstElementChild);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        const alerts = resultContainer.querySelectorAll('.alert');
        if (alerts.length > 0) {
            alerts[0].remove();
        }
    }, 10000);
}

/**
 * Show error message
 */
function showError(message) {
    const container = document.getElementById('device-cards-container');
    if (container) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                <h5 class="text-danger">Error</h5>
                <p class="text-muted">${escapeHtml(message)}</p>
                <button class="btn btn-outline-primary" id="error-retry-btn">
                    <i class="fas fa-sync-alt me-1"></i>Try Again
                </button>
            </div>
        `;
        
        // Add event listener to retry button
        const retryBtn = document.getElementById('error-retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', refreshDevices);
        }
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    alertContainer.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.parentNode.removeChild(alertContainer);
        }
    }, 5000);
}

/**
 * Utility function to update element text content
 */
function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Utility function to escape HTML
 */
function escapeHtml(text) {
    if (typeof text !== 'string') return text;
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

console.log('📱 Devices page JavaScript loaded');