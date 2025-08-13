/* Network Topology Visualization - Dark Mode Support */

// Global variables
let network = null;
let networkData = { nodes: [], edges: [] };
let physicsEnabled = true;
let isDarkMode = false;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Initializing Network Topology...');
    checkDarkMode();
    initializeTopology();
    loadTopologyData();
});

/**
 * Check if dark mode is active
 */
function checkDarkMode() {
    isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark' ||
                document.body.classList.contains('dark-mode') ||
                window.matchMedia('(prefers-color-scheme: dark)').matches;
    console.log(`🌙 Dark mode: ${isDarkMode ? 'enabled' : 'disabled'}`);
}

/**
 * Get colors based on current theme
 */
function getThemeColors() {
    if (isDarkMode) {
        return {
            background: '#2d3748',
            text: '#e2e8f0',
            border: '#4a5568',
            nodes: {
                offline: '#e53e3e',
                warning: '#d69e2e',
                router: '#38a169',
                switch: '#3182ce',
                access_point: '#805ad5',
                firewall: '#dd6b20',
                wireless_controller: '#319795',
                default: '#718096'
            },
            edges: {
                active: '#38a169',
                inactive: '#e53e3e',
                default: '#718096'
            }
        };
    } else {
        return {
            background: '#fdfdfd',
            text: '#2c3e50',
            border: '#e9ecef',
            nodes: {
                offline: '#f8d7da',
                warning: '#fff3cd',
                router: '#d4edda',
                switch: '#cce5ff',
                access_point: '#e2d9f3',
                firewall: '#ffe4cc',
                wireless_controller: '#d1ecf1',
                default: '#e9ecef'
            },
            edges: {
                active: '#28a745',
                inactive: '#dc3545',
                default: '#6c757d'
            }
        };
    }
}

/**
 * Initialize the network visualization
 */
function initializeTopology() {
    checkDarkMode();
    const colors = getThemeColors();
    
    const options = {
        nodes: {
            shape: 'box',
            size: 45,
            margin: 10,
            font: {
                size: 13,
                color: colors.text,
                face: 'Arial, sans-serif',
                strokeWidth: 1,
                strokeColor: isDarkMode ? '#2d3748' : 'white'
            },
            borderWidth: 2,
            shadow: {
                enabled: true,
                color: isDarkMode ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.1)',
                size: 5
            }
        },
        edges: {
            width: 3,
            color: { 
                color: colors.edges.default,
                highlight: isDarkMode ? '#e2e8f0' : '#495057'
            },
            smooth: {
                type: 'straightCross',
                roundness: 0.1
            },
            shadow: {
                enabled: true,
                color: isDarkMode ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.1)',
                size: 3
            }
        },
        physics: {
            enabled: true,
            stabilization: { 
                iterations: 80,
                updateInterval: 50
            },
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.1,
                springLength: 150,
                springConstant: 0.05,
                damping: 0.2,
                avoidOverlap: 0.3
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };

    const container = document.getElementById('topology-network');
    network = new vis.Network(container, networkData, options);

    // Event listeners
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            showDeviceDetails(nodeId);
        }
    });

    network.on('hoverNode', function(params) {
        document.body.style.cursor = 'pointer';
    });

    network.on('blurNode', function(params) {
        document.body.style.cursor = 'default';
    });

    network.on('stabilizationProgress', function(params) {
        const progress = Math.round(params.iterations / params.total * 100);
        showLoading(`Layout optimization... ${progress}%`);
    });

    network.on('stabilizationIterationsDone', function() {
        console.log('✅ Network layout complete');
        hideLoading();
        
        setTimeout(() => {
            network.fit({ animation: { duration: 800 } });
        }, 300);
    });

    // Auto-disable physics after 6 seconds
    setTimeout(() => {
        if (network) {
            network.setOptions({ physics: { enabled: false } });
            hideLoading();
            console.log('⏰ Physics disabled');
        }
    }, 6000);

    console.log('✅ Network topology initialized');
}

/**
 * Load topology data from API
 */
async function loadTopologyData() {
    showLoading('Loading devices...');
    
    try {
        const response = await fetch('/api/catalyst-center/topology');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'catalyst_center' && data.nodes && data.nodes.length > 0) {
            console.log(`🎉 Loaded ${data.nodes.length} real devices`);
            updateTopologyVisualization(data);
            updateNetworkStats(data);
            updateConnectionStatus('catalyst_center');
        } else {
            throw new Error('No topology data received');
        }
        
    } catch (error) {
        console.error('❌ Error loading topology:', error);
        loadSimulationData();
    }
    
    setTimeout(() => {
        hideLoading();
    }, 800);
}

/**
 * Load simulation data as fallback
 */
function loadSimulationData() {
    const simulatedData = {
        status: 'simulated',
        nodes: [
            { 
                id: 'sim-router-1', 
                type: 'router', 
                status: 'online', 
                ip: '192.168.1.1',
                hostname: 'Router-1',
                model: 'Cisco ISR 4431'
            },
            { 
                id: 'sim-switch-1', 
                type: 'switch', 
                status: 'online', 
                ip: '192.168.1.10',
                hostname: 'Switch-1',
                model: 'Cisco Catalyst 9300'
            },
            { 
                id: 'sim-switch-2', 
                type: 'switch', 
                status: 'warning', 
                ip: '192.168.2.1',
                hostname: 'Switch-2',
                model: 'Cisco Catalyst 2960'
            },
            { 
                id: 'sim-firewall-1', 
                type: 'firewall', 
                status: 'online', 
                ip: '192.168.1.254',
                hostname: 'Firewall-1',
                model: 'Cisco ASA 5515-X'
            }
        ],
        edges: [
            { from: 'sim-router-1', to: 'sim-firewall-1', status: 'active' },
            { from: 'sim-router-1', to: 'sim-switch-1', status: 'active' },
            { from: 'sim-switch-1', to: 'sim-switch-2', status: 'active' }
        ],
        stats: {
            totalDevices: 4,
            onlineDevices: 3,
            totalConnections: 3,
            networkHealth: '87%'
        }
    };

    updateTopologyVisualization(simulatedData);
    updateNetworkStats(simulatedData);
    updateConnectionStatus('simulation');
}

/**
 * Update the network visualization
 */
function updateTopologyVisualization(data) {
    console.log(`📊 Processing ${data.nodes?.length || 0} devices`);
    
    if (!data.nodes || data.nodes.length === 0) {
        console.warn('⚠️ No devices found');
        return;
    }
    
    checkDarkMode();
    const colors = getThemeColors();
    
    // Process nodes with theme-aware colors
    const nodes = data.nodes.map((node, index) => {
        const deviceName = node.hostname || node.name || `Device-${index + 1}`;
        const showLabels = document.getElementById('showLabels')?.checked !== false;
        
        return {
            id: node.id,
            label: showLabels ? `${deviceName}\n${node.ip || ''}` : '',
            color: {
                background: getNodeColor(node.type, node.status),
                border: isDarkMode ? colors.border : '#495057',
                highlight: isDarkMode ? '#e2e8f0' : '#007bff'
            },
            font: {
                color: colors.text,
                strokeColor: isDarkMode ? '#2d3748' : 'white'
            },
            title: createDeviceTooltip(node),
            shape: getNodeShape(node.type),
            size: getNodeSize(node.type),
            borderWidth: node.status === 'offline' ? 3 : 2,
            ...node
        };
    });

    // Process edges with theme-aware colors
    const edges = (data.edges || []).map(edge => ({
        from: edge.from,
        to: edge.to,
        color: edge.status === 'active' ? colors.edges.active : colors.edges.inactive,
        dashes: edge.status === 'active' ? false : [5, 3],
        width: edge.status === 'active' ? 3 : 2,
        title: `${edge.from} ↔ ${edge.to}`,
        ...edge
    }));

    // Update network
    networkData = { nodes: nodes, edges: edges };
    network.setData(networkData);
    
    if (data.status === 'catalyst_center') {
        console.log(`✅ Displaying ${nodes.length} real devices`);
    }
    
    hideLoading();
}

/**
 * Helper functions with theme-aware colors
 */
function getNodeColor(type, status) {
    const colors = getThemeColors();
    
    if (status === 'offline') return colors.nodes.offline;
    if (status === 'warning') return colors.nodes.warning;
    
    return colors.nodes[type] || colors.nodes.default;
}

function getNodeShape(type) {
    const shapes = {
        'router': 'triangle',
        'switch': 'box',
        'access_point': 'dot',
        'firewall': 'diamond',
        'wireless_controller': 'ellipse'
    };
    return shapes[type] || 'box';
}

function getNodeSize(type) {
    const sizes = {
        'router': 35,
        'switch': 30,
        'firewall': 30,
        'wireless_controller': 25,
        'access_point': 25
    };
    return sizes[type] || 30;
}

function createDeviceTooltip(node) {
    const deviceName = node.hostname || node.name || 'Unknown Device';
    const textColor = isDarkMode ? '#e2e8f0' : '#212529';
    const nameColor = isDarkMode ? '#90cdf4' : '#495057';
    
    return `<div style="font-family: Arial; line-height: 1.4; max-width: 200px; color: ${textColor}; background: ${isDarkMode ? '#2d3748' : 'white'}; padding: 10px; border-radius: 5px;">
        <strong style="color: ${nameColor};">${deviceName}</strong><br>
        <strong>IP:</strong> ${node.ip || 'N/A'}<br>
        <strong>Type:</strong> ${node.type}<br>
        <strong>Status:</strong> <span style="color: ${node.status === 'online' ? '#68d391' : '#fc8181'};">${node.status}</span><br>
        <em>Click for details</em>
    </div>`;
}

function updateNetworkStats(data) {
    document.getElementById('total-devices').textContent = data.stats?.totalDevices || data.nodes?.length || 0;
    document.getElementById('online-devices').textContent = data.stats?.onlineDevices || 0;
    document.getElementById('total-connections').textContent = data.stats?.totalConnections || data.edges?.length || 0;
    document.getElementById('network-health').textContent = data.stats?.networkHealth || 'N/A';
}

function updateConnectionStatus(mode) {
    const statusElement = document.getElementById('connection-status');
    if (mode === 'catalyst_center') {
        statusElement.innerHTML = '<i class="fas fa-cloud me-1"></i>Live Data';
        statusElement.className = 'catalyst-center';
    } else {
        statusElement.innerHTML = '<i class="fas fa-desktop me-1"></i>Demo Mode';
        statusElement.className = 'simulation';
    }
}

function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        const text = overlay.querySelector('p');
        if (text) text.textContent = message;
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showAlert(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
}

function showDeviceDetails(nodeId) {
    const node = networkData.nodes.find(n => n.id === nodeId);
    if (!node) return;

    const deviceName = node.hostname || node.name || 'Unknown Device';
    
    document.getElementById('deviceModalTitle').innerHTML = `
        <i class="fas fa-${getDeviceIcon(node.type)} me-2"></i>
        ${deviceName}
    `;
    
    document.getElementById('deviceModalBody').innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 style="margin-bottom: 15px;">Device Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Hostname:</strong></td><td>${deviceName}</td></tr>
                    <tr><td><strong>IP Address:</strong></td><td>${node.ip || 'N/A'}</td></tr>
                    <tr><td><strong>Type:</strong></td><td>${node.type}</td></tr>
                    <tr><td><strong>Status:</strong></td><td><span class="badge ${node.status === 'online' ? 'bg-success' : 'bg-danger'}">${node.status}</span></td></tr>
                    <tr><td><strong>Model:</strong></td><td>${node.model || 'Unknown'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 style="margin-bottom: 15px;">Network Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Role:</strong></td><td>${node.role || 'Unknown'}</td></tr>
                    <tr><td><strong>Series:</strong></td><td>${node.series || 'Unknown'}</td></tr>
                    <tr><td><strong>Location:</strong></td><td>${node.location || 'Unknown'}</td></tr>
                    <tr><td><strong>Source:</strong></td><td>Catalyst Center</td></tr>
                </table>
            </div>
        </div>
    `;

    new bootstrap.Modal(document.getElementById('deviceModal')).show();
}

function getDeviceIcon(type) {
    const icons = {
        'router': 'route',
        'switch': 'network-wired',
        'access_point': 'wifi',
        'firewall': 'shield-alt',
        'wireless_controller': 'broadcast-tower'
    };
    return icons[type] || 'server';
}

// Control functions
function refreshTopology() {
    console.log('🔄 Refreshing...');
    checkDarkMode(); // Re-check dark mode
    loadTopologyData();
}

function autoLayout() {
    if (network) {
        network.setOptions({ physics: { enabled: true } });
        setTimeout(() => {
            network.setOptions({ physics: { enabled: false } });
        }, 2000);
    }
}

function fitNetwork() {
    if (network) {
        network.fit({ animation: { duration: 800 } });
    }
}

function togglePhysics() {
    physicsEnabled = !physicsEnabled;
    if (network) {
        network.setOptions({ physics: { enabled: physicsEnabled } });
    }
    console.log(`Physics ${physicsEnabled ? 'enabled' : 'disabled'}`);
}

function toggleLabels() {
    loadTopologyData();
}

function toggleRealTime() {
    const enabled = document.getElementById('realTimeUpdates')?.checked;
    console.log(`Real-time updates ${enabled ? 'enabled' : 'disabled'}`);
}

function exportTopology() {
    console.log('📸 Export feature coming soon...');
}

function testDeviceConnection() {
    console.log('🔍 Connection test feature coming soon...');
}

// Listen for theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        console.log('🌙 Theme changed, refreshing topology...');
        setTimeout(() => {
            refreshTopology();
        }, 100);
    });
}