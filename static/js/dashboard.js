/**
 * Network Dashboard JavaScript - MANUAL REFRESH ONLY
 * No auto-refresh loops, no background timers
 */

// Global variables
let performanceChart = null;
let statusChart = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard initializing (manual mode only)...');
    
    // Initialize theme and charts only
    initializeTheme();
    initializeCharts();
    
    console.log('✅ Dashboard initialized - NO AUTO-REFRESH');
    console.log('💡 Click refresh button to load data');
});

/**
 * MANUAL REFRESH ONLY - Called by refresh button
 */
function refreshDashboard() {
    console.log('🔄 Manual refresh triggered by user');
    
    const refreshBtn = document.querySelector('.btn-outline-primary');
    if (refreshBtn) {
        // Show loading state
        const originalHTML = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        refreshBtn.disabled = true;
        
        // Load data once
        Promise.all([
            loadDashboardMode(),
            loadDeviceData(),
            loadPerformanceData(),
            loadAlerts()
        ]).then(() => {
            console.log('✅ Manual refresh completed');
            updateLastRefreshTime();
        }).catch(error => {
            console.error('❌ Refresh failed:', error);
            showAlert('Refresh failed: ' + error.message, 'danger');
        }).finally(() => {
            // Reset button
            refreshBtn.innerHTML = originalHTML;
            refreshBtn.disabled = false;
        });
    }
}

/**
 * Load dashboard mode (one time only)
 */
function loadDashboardMode() {
    console.log('📊 Loading dashboard mode...');
    
    return fetch('/api/dashboard/mode')
        .then(response => response.json())
        .then(data => {
            const modeIndicator = document.getElementById('mode-indicator');
            if (modeIndicator) {
                let badgeClass, icon, description;
                
                if (data.mode === 'catalyst_center') {
                    badgeClass = 'bg-success';
                    icon = '🌐';
                    description = 'Live Catalyst Center';
                } else {
                    badgeClass = 'bg-warning';
                    icon = '📡';
                    description = 'Simulation Mode';
                }
                
                modeIndicator.innerHTML = `
                    <span class="badge ${badgeClass}">
                        ${icon} ${description}
                    </span>
                `;
            }
            
            console.log(`✅ Dashboard mode: ${data.mode}`);
        })
        .catch(error => {
            console.error('❌ Failed to load dashboard mode:', error);
        });
}

/**
 * Load device data (one time only)
 */
function loadDeviceData() {
    console.log('📱 Loading device data...');
    
    return fetch('/api/devices')
        .then(response => {
            console.log('📡 Device API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📊 Device API data received:', data);
            console.log('🔍 Device count:', data.total);
            console.log('🔍 First device:', data.devices[0]);
            
            // Update device statistics
            const totalElement = document.getElementById('total-devices');
            const onlineElement = document.getElementById('online-devices');
            const offlineElement = document.getElementById('offline-devices');
            
            // Update total devices
            if (totalElement) {
                totalElement.textContent = data.total || 0;
                console.log(`📊 Updated total devices: ${data.total}`);
            }
            
            if (data.devices && data.devices.length > 0) {
                // Count online/offline devices
                const onlineCount = data.devices.filter(d => d.status === 'online').length;
                const offlineCount = data.devices.length - onlineCount;
                
                if (onlineElement) {
                    onlineElement.textContent = onlineCount;
                    console.log(`📊 Updated online devices: ${onlineCount}`);
                }
                if (offlineElement) {
                    offlineElement.textContent = offlineCount;
                    console.log(`📊 Updated offline devices: ${offlineCount}`);
                }
                
                // Update charts
                updateStatusChart(data);
                
                // Display device list
                displayDeviceList(data.devices);
                
                // Show success message
                showAlert(`Successfully loaded ${data.total} Catalyst Center devices!`, 'success');
                
            } else {
                console.log('⚠️ No devices found in response');
                if (onlineElement) onlineElement.textContent = '0';
                if (offlineElement) offlineElement.textContent = '0';
            }
            
            console.log(`✅ Device data loaded: ${data.total || 0} total devices`);
        })
        .catch(error => {
            console.error('❌ Failed to load device data:', error);
            showAlert('Failed to load device data: ' + error.message, 'danger');
        });
}

/**
 * Load performance data (one time only)
 */
function loadPerformanceData() {
    console.log('📈 Loading performance data...');
    
    // For now, just simulate some data since we don't have a performance endpoint
    const performanceData = {
        response_time: Math.random() * 50 + 10,
        network_health: 'Good',
        timestamp: new Date().toLocaleTimeString()
    };
    
    updatePerformanceChart(performanceData);
    
    return Promise.resolve();
}

/**
 * Load alerts (one time only)
 */
function loadAlerts() {
    console.log('🚨 Loading alerts...');
    
    // For now, show static alerts since we don't have alerts endpoint
    const alertsContainer = document.getElementById('recentAlerts');
    if (alertsContainer) {
        alertsContainer.innerHTML = `
            <div class="list-group-item text-center text-muted py-4">
                <i class="fas fa-check-circle me-2 text-success"></i>
                No recent alerts
            </div>
        `;
    }
    
    // Update alerts count
    const alertsCountElement = document.getElementById('total-alerts');
    if (alertsCountElement) {
        alertsCountElement.textContent = '0';
    }
    
    return Promise.resolve();
}

/**
 * Initialize charts (no data loading)
 */
function initializeCharts() {
    try {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            performanceChart = new Chart(performanceCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Start'],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [0],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Status Chart
        const statusCtx = document.getElementById('statusChart');
        if (statusCtx) {
            statusChart = new Chart(statusCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Online', 'Offline'],
                    datasets: [{
                        data: [0, 0],
                        backgroundColor: ['#28a745', '#dc3545'],
                        borderWidth: 0
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
        
        console.log('✅ Charts initialized (empty)');
    } catch (error) {
        console.error('❌ Chart initialization failed:', error);
    }
}

/**
 * Update status chart
 */
function updateStatusChart(data) {
    if (!statusChart || !data.devices) return;
    
    const onlineCount = data.devices.filter(d => d.status === 'online').length;
    const offlineCount = data.devices.length - onlineCount;
    
    statusChart.data.datasets[0].data = [onlineCount, offlineCount];
    statusChart.update('none');
}

/**
 * Update performance chart
 */
function updatePerformanceChart(data) {
    if (!performanceChart) return;
    
    performanceChart.data.labels.push(data.timestamp);
    performanceChart.data.datasets[0].data.push(data.response_time);
    
    // Keep only last 10 data points
    if (performanceChart.data.labels.length > 10) {
        performanceChart.data.labels.shift();
        performanceChart.data.datasets[0].data.shift();
    }
    
    performanceChart.update('none');
}

/**
 * Theme management
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeIcon = document.querySelector('.theme-toggle i');
    if (themeIcon) {
        themeIcon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            themeIcon.style.transform = 'rotate(0deg)';
        }, 150);
    }
    
    showAlert(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
}

/**
 * Utility functions
 */
function showAlert(message, type) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.parentNode.removeChild(alertContainer);
        }
    }, 3000);
}

function updateLastRefreshTime() {
    const updateTimeElement = document.getElementById('update-time');
    if (updateTimeElement) {
        updateTimeElement.textContent = new Date().toLocaleTimeString();
    }
}

/**
 * Add function to test individual Catalyst devices
 */
function testCatalystDevice(deviceId) {
    console.log(`🧪 Testing Catalyst device: ${deviceId}`);
    
    // Show loading state
    const button = event.target.closest('button');
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
    button.disabled = true;
    
    fetch(`/api/catalyst-center/test/${deviceId}`)
        .then(response => response.json())
        .then(data => {
            console.log('🧪 Device test result:', data);
            
            if (data.status === 'success') {
                showAlert(`✅ Device test successful: ${data.message}`, 'success');
            } else {
                showAlert(`❌ Device test failed: ${data.message}`, 'warning');
            }
        })
        .catch(error => {
            console.error('❌ Device test failed:', error);
            showAlert('Device test failed: ' + error.message, 'danger');
        })
        .finally(() => {
            // Reset button
            button.innerHTML = originalHTML;
            button.disabled = false;
        });
}

/**
 * Display your real Catalyst devices
 */
function displayDeviceList(devices) {
    console.log('📱 Device data loaded for dashboard stats only');
    // Don't display device cards on dashboard - just update stats
    // Device cards will be shown on the dedicated Devices page
}

console.log('📁 Dashboard JavaScript loaded (MANUAL REFRESH ONLY)');
