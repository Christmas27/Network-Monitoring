// Dashboard JavaScript Functions

// Global variables
let loadingModal = null;
let refreshInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeComponents();
    setupEventListeners();
});

// Initialize components
function initializeComponents() {
    // Initialize Bootstrap modals
    const loadingModalElement = document.getElementById('loadingModal');
    if (loadingModalElement) {
        loadingModal = new bootstrap.Modal(loadingModalElement);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            if (alert.querySelector('.btn-close')) {
                alert.querySelector('.btn-close').click();
            }
        }, 5000);
    });
}

// Utility Functions

// Show loading modal
function showLoading(message = 'Loading...') {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.textContent = message;
    }
    
    if (loadingModal) {
        loadingModal.show();
    }
}

// Hide loading modal
function hideLoading() {
    if (loadingModal) {
        loadingModal.hide();
    }
}

// Show alert message
function showAlert(message, type = 'info', timeout = 5000) {
    const alertBanner = document.getElementById('alertBanner');
    const alertMessage = document.getElementById('alertMessage');
    
    if (alertBanner && alertMessage) {
        // Remove existing alert classes
        alertBanner.className = 'alert alert-dismissible fade show';
        
        // Add new alert class
        alertBanner.classList.add(`alert-${type}`);
        
        // Set message
        alertMessage.textContent = message;
        
        // Show alert
        alertBanner.classList.remove('d-none');
        
        // Auto-hide after timeout
        if (timeout > 0) {
            setTimeout(() => {
                alertBanner.classList.add('d-none');
            }, timeout);
        }
    }
}

// Format date/time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format file size
function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Format uptime
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0) result += `${minutes}m`;
    
    return result || '0m';
}

// Get device type icon
function getDeviceTypeIcon(deviceType) {
    const icons = {
        'cisco_ios': 'fas fa-server',
        'cisco_nxos': 'fas fa-network-wired',
        'cisco_asa': 'fas fa-shield-alt',
        'juniper_junos': 'fas fa-router',
        'arista_eos': 'fas fa-ethernet',
        'hp_procurve': 'fas fa-hdd'
    };
    
    return icons[deviceType] || 'fas fa-question-circle';
}

// Get device type color class
function getDeviceTypeColor(deviceType) {
    const colors = {
        'router': 'device-router',
        'switch': 'device-switch',
        'firewall': 'device-firewall',
        'wireless': 'device-wireless'
    };
    
    // Extract device category from device type
    if (deviceType.includes('router') || deviceType.includes('junos')) {
        return colors.router;
    } else if (deviceType.includes('switch') || deviceType.includes('nxos')) {
        return colors.switch;
    } else if (deviceType.includes('asa') || deviceType.includes('firewall')) {
        return colors.firewall;
    } else if (deviceType.includes('wireless') || deviceType.includes('ap')) {
        return colors.wireless;
    }
    
    return colors.router; // Default
}

// Get status color
function getStatusColor(status) {
    const colors = {
        'online': 'success',
        'offline': 'danger',
        'warning': 'warning',
        'unknown': 'secondary'
    };
    
    return colors[status] || 'secondary';
}

// Get severity color
function getSeverityColor(severity) {
    const colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'secondary'
    };
    
    return colors[severity] || 'secondary';
}

// API Functions

// Generic API call function
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Get devices
async function getDevices() {
    return await apiCall('/api/devices');
}

// Add device
async function addDeviceAPI(deviceData) {
    return await apiCall('/api/devices', {
        method: 'POST',
        body: JSON.stringify(deviceData)
    });
}

// Get device status
async function getDeviceStatus(deviceId) {
    return await apiCall(`/api/devices/${deviceId}/status`);
}

// Backup device config
async function backupDeviceConfig(deviceId) {
    return await apiCall(`/api/devices/${deviceId}/backup`, {
        method: 'POST'
    });
}

// Run security scan
async function runSecurityScan(deviceId) {
    return await apiCall(`/api/security/scan/${deviceId}`, {
        method: 'POST'
    });
}

// Get network metrics
async function getNetworkMetrics() {
    return await apiCall('/api/metrics');
}

// Get alerts
async function getAlerts() {
    return await apiCall('/api/alerts');
}

// Data Visualization Functions

// Create status badge
function createStatusBadge(status) {
    const color = getStatusColor(status);
    const icon = status === 'online' ? 'check-circle' : 
                 status === 'offline' ? 'times-circle' : 
                 status === 'warning' ? 'exclamation-triangle' : 'question-circle';
    
    return `
        <span class="badge bg-${color} d-flex align-items-center">
            <i class="fas fa-${icon} me-1"></i>
            ${status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    `;
}

// Create severity badge
function createSeverityBadge(severity) {
    const color = getSeverityColor(severity);
    return `
        <span class="badge bg-${color}">
            ${severity.charAt(0).toUpperCase() + severity.slice(1)}
        </span>
    `;
}

// Create progress bar
function createProgressBar(value, max = 100, color = 'primary') {
    const percentage = Math.round((value / max) * 100);
    return `
        <div class="progress" style="height: 20px;">
            <div class="progress-bar bg-${color}" role="progressbar" 
                 style="width: ${percentage}%" 
                 aria-valuenow="${value}" 
                 aria-valuemin="0" 
                 aria-valuemax="${max}">
                ${percentage}%
            </div>
        </div>
    `;
}

// Table Functions

// Create sortable table header
function createSortableHeader(text, sortKey, currentSort) {
    const isCurrentSort = currentSort && currentSort.key === sortKey;
    const direction = isCurrentSort ? currentSort.direction : 'asc';
    const nextDirection = direction === 'asc' ? 'desc' : 'asc';
    const icon = isCurrentSort ? 
                 (direction === 'asc' ? 'fa-sort-up' : 'fa-sort-down') : 
                 'fa-sort';
    
    return `
        <th class="sortable" onclick="sortTable('${sortKey}', '${nextDirection}')" style="cursor: pointer;">
            ${text}
            <i class="fas ${icon} ms-1"></i>
        </th>
    `;
}

// Sort table data
function sortTableData(data, sortKey, direction = 'asc') {
    return data.sort((a, b) => {
        let aValue = a[sortKey];
        let bValue = b[sortKey];
        
        // Handle null/undefined values
        if (aValue == null) aValue = '';
        if (bValue == null) bValue = '';
        
        // Convert to string for comparison if not already
        if (typeof aValue !== 'string') aValue = String(aValue);
        if (typeof bValue !== 'string') bValue = String(bValue);
        
        // Compare values
        const comparison = aValue.localeCompare(bValue, undefined, {
            numeric: true,
            sensitivity: 'base'
        });
        
        return direction === 'asc' ? comparison : -comparison;
    });
}

// Filter table data
function filterTableData(data, searchTerm) {
    if (!searchTerm) return data;
    
    searchTerm = searchTerm.toLowerCase();
    
    return data.filter(item => {
        return Object.values(item).some(value => {
            if (value == null) return false;
            return String(value).toLowerCase().includes(searchTerm);
        });
    });
}

// Animation Functions

// Fade in element
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    let start = null;
    
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        
        element.style.opacity = Math.min(progress / duration, 1);
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

// Slide down element
function slideDown(element, duration = 300) {
    element.style.height = '0px';
    element.style.overflow = 'hidden';
    element.style.display = 'block';
    
    const targetHeight = element.scrollHeight + 'px';
    
    let start = null;
    
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        
        const percentage = Math.min(progress / duration, 1);
        element.style.height = (parseInt(targetHeight) * percentage) + 'px';
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        } else {
            element.style.height = '';
            element.style.overflow = '';
        }
    }
    
    requestAnimationFrame(animate);
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard', 'success', 2000);
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        showAlert('Failed to copy to clipboard', 'danger', 3000);
    }
}

// Download data as file
function downloadAsFile(data, filename, type = 'application/json') {
    const blob = new Blob([data], { type });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Validation Functions

// Validate IP address
function validateIPAddress(ip) {
    const ipRegex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

// Validate hostname
function validateHostname(hostname) {
    const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$/;
    return hostnameRegex.test(hostname);
}

// Validate port number
function validatePort(port) {
    const portNum = parseInt(port);
    return portNum >= 1 && portNum <= 65535;
}

// Local Storage Functions

// Save to local storage
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Failed to save to local storage:', error);
    }
}

// Load from local storage
function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Failed to load from local storage:', error);
        return defaultValue;
    }
}

// Remove from local storage
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Failed to remove from local storage:', error);
    }
}

// Theme Functions

// Toggle dark mode
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.contains('dark-mode');
    
    if (isDark) {
        body.classList.remove('dark-mode');
        saveToLocalStorage('darkMode', false);
    } else {
        body.classList.add('dark-mode');
        saveToLocalStorage('darkMode', true);
    }
}

// Initialize theme
function initializeTheme() {
    const darkMode = loadFromLocalStorage('darkMode', false);
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
}

// Error Handling

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showAlert('An unexpected error occurred', 'danger');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showAlert('A network error occurred', 'warning');
});

// Initialize theme on load
document.addEventListener('DOMContentLoaded', initializeTheme);
