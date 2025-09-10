/* Network Topology Visualization - IMPROVED VERSION */

class NetworkTopology {
    constructor() {
        this.network = null;
        this.networkData = { nodes: [], edges: [] };
        this.physicsEnabled = true;
        this.isDarkMode = false;
        this.container = null;
        
        this.init();
    }

    init() {
        console.log('🌐 Network Topology page loaded');
        
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeTopology());
        } else {
            this.initializeTopology();
        }
    }

    initializeTopology() {
        this.container = document.getElementById('topology-container');
        
        if (!this.container) {
            console.error('❌ Topology container not found!');
            this.showError('Topology container not found');
            return;
        }

        console.log('✅ Topology container found');
        this.setupEventListeners();
        this.checkDarkMode();
        this.loadTopologyData();
    }

    setupEventListeners() {
        // Dark mode detection
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.isDarkMode = e.matches;
            this.updateTheme();
        });

        // Window resize
        window.addEventListener('resize', () => {
            if (this.network) {
                this.network.redraw();
                this.network.fit();
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    checkDarkMode() {
        const htmlElement = document.documentElement;
        const bodyClasses = document.body.classList;
        
        this.isDarkMode = 
            htmlElement.getAttribute('data-bs-theme') === 'dark' ||
            bodyClasses.contains('dark-mode') ||
            bodyClasses.contains('dark') ||
            window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    updateTheme() {
        if (this.network) {
            const options = this.getNetworkOptions();
            this.network.setOptions(options);
            this.network.redraw();
        }
    }

    async loadTopologyData() {
        try {
            console.log('📡 Loading topology data...');
            this.showLoading(true);
            this.updateConnectionStatus('Loading...', 'loading');
            
            const response = await fetch('/api/network/topology');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 Topology data received:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Handle empty topology
            if (!data.nodes || data.nodes.length === 0) {
                this.showEmptyTopology(data.message || 'No devices found');
                this.updateConnectionStatus('No Data Available', 'unavailable');
                return;
            }
            
            this.processTopologyData(data);
            this.createTopology();
            this.showLoading(false);
            
            // Update connection status based on mode
            if (data.mode === 'catalyst_center') {
                this.updateConnectionStatus(`🌐 Live DevNet Data (${data.device_count} devices)`, 'catalyst-center');
            } else {
                this.updateConnectionStatus('Simulation Mode', 'simulation');
            }
            
        } catch (error) {
            console.error('❌ Error loading topology:', error);
            this.showError(`Failed to load network topology: ${error.message}`);
            this.showLoading(false);
            this.updateConnectionStatus('Connection Error', 'error');
        }
    }

    updateConnectionStatus(message, type) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.innerHTML = message;
            statusElement.className = `badge fs-6 ${this.getStatusClass(type)}`;
        }
    }

    getStatusClass(type) {
        const classMap = {
            'loading': 'bg-secondary',
            'catalyst-center': 'bg-success',
            'simulation': 'bg-warning',
            'unavailable': 'bg-danger',
            'error': 'bg-danger'
        };
        return classMap[type] || 'bg-secondary';
    }

    showEmptyTopology(message) {
        console.log('📭 Showing empty topology message');
        this.showLoading(false);
        
        if (this.container) {
            this.container.innerHTML = `
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-align: center; color: #6c757d;">
                    <i class="fas fa-network-wired fa-4x mb-3" style="opacity: 0.3;"></i>
                    <h5>No Network Topology Available</h5>
                    <p>${message}</p>
                    <button class="btn btn-outline-primary" onclick="networkTopology.refreshTopology()">
                        <i class="fas fa-sync-alt me-1"></i>Retry
                    </button>
                </div>
            `;
        }
        
        // Update stats
        this.updateElement('total-devices', '0');
        this.updateElement('online-devices', '0');
        this.updateElement('total-connections', '0');
        this.updateElement('network-health', 'N/A');
    }

    processTopologyData(data) {
        // Process nodes with better labels and tooltips
        this.networkData.nodes = data.nodes?.map(node => ({
            id: node.id,
            label: node.name || node.hostname || `Device ${node.id}`,
            group: this.getDeviceGroup(node.type),
            title: this.createNodeTooltip(node),
            color: this.getNodeColor(node.type, node.status),
            font: this.getNodeFont(),
            shape: 'dot',
            size: this.getDeviceSize(node.type),
            borderWidth: 2,
            borderColor: this.getNodeBorderColor(node.status)
        })) || [];

        // Process edges with better visualization
        this.networkData.edges = data.edges?.map(edge => ({
            id: edge.id,
            from: edge.source,
            to: edge.target,
            label: edge.interface || '',
            title: this.createEdgeTooltip(edge),
            color: {
                color: this.getEdgeColor(edge.status),
                highlight: this.getEdgeColor(edge.status),
                hover: this.getEdgeColor(edge.status)
            },
            width: edge.bandwidth ? this.calculateEdgeWidth(edge.bandwidth) : 2,
            dashes: edge.status === 'down' ? [5, 5] : false,
            arrows: 'to'
        })) || [];

        console.log(`📊 Processed ${this.networkData.nodes.length} nodes and ${this.networkData.edges.length} edges`);
        
        // Update stats
        this.updateStats();
    }

    updateStats() {
        const totalDevices = this.networkData.nodes.length;
        const onlineDevices = this.networkData.nodes.filter(node => 
            node.title && node.title.includes('online')
        ).length;
        const totalConnections = this.networkData.edges.length;
        
        this.updateElement('total-devices', totalDevices);
        this.updateElement('online-devices', onlineDevices);
        this.updateElement('total-connections', totalConnections);
        this.updateElement('network-health', totalDevices > 0 ? 'Good' : 'N/A');
    }

    createTopology() {
        if (!this.container) {
            console.error('❌ Container not available for topology creation');
            return;
        }

        try {
            console.log('🎨 Creating network visualization...');
            
            // Check if vis is available
            if (typeof vis === 'undefined') {
                throw new Error('vis.js library not loaded');
            }
            
            const options = this.getNetworkOptions();
            this.network = new vis.Network(this.container, this.networkData, options);
            this.setupNetworkEvents();
            
            console.log('✅ Network visualization created successfully');
            
            // Auto-fit after initial render
            setTimeout(() => {
                if (this.network) {
                    this.network.fit({ animation: true });
                }
            }, 500);
            
        } catch (error) {
            console.error('❌ Error creating topology:', error);
            this.showError(`Failed to create network visualization: ${error.message}`);
        }
    }

    getNetworkOptions() {
    const theme = this.getThemeColors();
    
    return {
        nodes: {
            borderWidth: 2,
            borderWidthSelected: 4,
            font: {
                size: 14,
                color: theme.text,
                face: 'arial',
                background: 'rgba(255,255,255,0.8)',
                strokeWidth: 2,
                strokeColor: theme.background
            },
            shadow: true,
            // Add these properties for better dragging
            chosen: {
                node: (values, id, selected, hovering) => {
                    values.shadow = true;
                    values.shadowSize = 10;
                    values.shadowX = 3;
                    values.shadowY = 3;
                }
            }
        },
        edges: {
            width: 2,
            font: {
                size: 10,
                color: theme.text,
                background: 'rgba(255,255,255,0.8)',
                strokeWidth: 1,
                strokeColor: theme.background
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            },
            shadow: true,
            // Add these properties for better edge handling
            chosen: {
                edge: (values, id, selected, hovering) => {
                    values.shadow = true;
                    values.shadowSize = 5;
                }
            }
        },
        physics: {
            enabled: this.physicsEnabled,
            stabilization: { iterations: 150 },
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 120,
                springConstant: 0.04,
                damping: 0.09
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            // FIX: Disable hiding during drag - this was causing the issue!
            hideEdgesOnDrag: false,
            hideNodesOnDrag: false,
            selectConnectedEdges: false,
            // Add these for better interaction
            dragNodes: true,
            dragView: true,
            zoomView: true,
            // Improve drag performance
            keyboard: {
                enabled: false
            }
        },
        layout: {
            improvedLayout: true,
            randomSeed: 42
        },
        // Add configure options for better performance
        configure: {
            enabled: false
        }
    };
}

    getThemeColors() {
        if (this.isDarkMode) {
            return {
                background: '#212529',
                text: '#ffffff',
                border: '#495057',
                highlight: '#0d6efd',
                success: '#198754',
                warning: '#ffc107',
                danger: '#dc3545'
            };
        } else {
            return {
                background: '#ffffff',
                text: '#212529',
                border: '#dee2e6',
                highlight: '#0d6efd',
                success: '#198754',
                warning: '#ffc107',
                danger: '#dc3545'
            };
        }
    }

    setupNetworkEvents() {
    if (!this.network) return;

    this.network.on('click', (params) => {
        if (params.nodes.length > 0) {
            this.onNodeClick(params.nodes[0]);
        }
    });

    this.network.on('doubleClick', (params) => {
        if (params.nodes.length > 0) {
            this.onNodeDoubleClick(params.nodes[0]);
        }
    });

    this.network.on('hoverNode', (params) => {
        if (this.container) {
            this.container.style.cursor = 'pointer';
        }
    });

    this.network.on('blurNode', (params) => {
        if (this.container) {
            this.container.style.cursor = 'default';
        }
    });

    // ADD: Better drag handling
    this.network.on('dragStart', (params) => {
        if (params.nodes.length > 0) {
            this.container.style.cursor = 'grabbing';
            console.log('🖱️ Drag started');
        }
    });

    this.network.on('dragging', (params) => {
        // Optional: You can add drag feedback here
        if (params.nodes.length > 0) {
            // Node is being dragged - no special action needed
        }
    });

    this.network.on('dragEnd', (params) => {
        if (params.nodes.length > 0) {
            this.container.style.cursor = 'pointer';
            console.log('🖱️ Drag ended');
            
            // Optional: Save node positions if needed
            // this.saveNodePositions();
        }
    });

    this.network.on('stabilizationIterationsDone', () => {
        console.log('🎯 Network stabilization complete');
        this.network.setOptions({ physics: false });
        this.physicsEnabled = false;
        
        // Update physics button
        const button = document.getElementById('togglePhysics');
        if (button) {
            button.innerHTML = '<i class="fas fa-play me-1"></i>Start Physics';
        }
    });
}

// ADD: Optional method to save node positions
saveNodePositions() {
    if (!this.network) return;
    
    const positions = this.network.getPositions();
    console.log('💾 Node positions saved:', positions);
    // You could save these to localStorage or send to server
    // localStorage.setItem('topology-positions', JSON.stringify(positions));
}

// ADD: Optional method to restore node positions
restoreNodePositions() {
    if (!this.network) return;
    
    try {
        const savedPositions = localStorage.getItem('topology-positions');
        if (savedPositions) {
            const positions = JSON.parse(savedPositions);
            this.network.setPositions(positions);
            console.log('📍 Node positions restored');
        }
    } catch (error) {
        console.log('⚠️ Could not restore node positions:', error);
    }
}

    // Device type utilities
    getDeviceGroup(deviceType) {
        const typeMap = {
            'router': 'routers',
            'switch': 'switches', 
            'firewall': 'security',
            'access point': 'wireless',
            'server': 'servers'
        };
        return typeMap[deviceType?.toLowerCase()] || 'unknown';
    }

    getNodeColor(deviceType, status) {
        const theme = this.getThemeColors();
        
        if (status === 'offline' || status === 'down') {
            return theme.danger;
        }
        
        const colorMap = {
            'router': theme.success,
            'switch': theme.highlight,
            'firewall': '#fd7e14',
            'access point': '#6f42c1',
            'server': '#20c997'
        };
        return colorMap[deviceType?.toLowerCase()] || theme.highlight;
    }

    getNodeBorderColor(status) {
        return status === 'online' ? '#28a745' : '#dc3545';
    }

    getDeviceSize(deviceType) {
        const sizeMap = {
            'router': 30,
            'switch': 25,
            'firewall': 28,
            'access point': 22,
            'server': 25
        };
        return sizeMap[deviceType?.toLowerCase()] || 20;
    }

    getNodeFont() {
        return {
            size: 14,
            color: this.getThemeColors().text,
            face: 'arial'
        };
    }

    getEdgeColor(status) {
        const colorMap = {
            'up': '#28a745',
            'down': '#dc3545',
            'warning': '#ffc107'
        };
        return colorMap[status?.toLowerCase()] || '#6c757d';
    }

    calculateEdgeWidth(bandwidth) {
        const bw = parseInt(bandwidth) || 100;
        if (bw >= 10000) return 6;
        if (bw >= 1000) return 4;
        if (bw >= 100) return 3;
        if (bw >= 10) return 2;
        return 1;
    }

    // Tooltip creators
    createNodeTooltip(node) {
        return `
            <div style="padding: 10px; max-width: 250px; font-family: Arial, sans-serif;">
                <strong style="color: #007bff;">${node.name || 'Unknown Device'}</strong><br>
                <strong>Type:</strong> ${node.type || 'Unknown'}<br>
                <strong>IP:</strong> ${node.ip || 'N/A'}<br>
                <strong>Status:</strong> <span style="color: ${node.status === 'online' ? '#28a745' : '#dc3545'};">${node.status || 'Unknown'}</span><br>
                <strong>Role:</strong> ${node.role || 'N/A'}<br>
                <strong>Location:</strong> ${node.location || 'N/A'}<br>
                <small style="color: #6c757d;">Click for details</small>
            </div>
        `;
    }

    createEdgeTooltip(edge) {
        return `
            <div style="padding: 10px; max-width: 200px; font-family: Arial, sans-serif;">
                <strong>Network Connection</strong><br>
                <strong>Interface:</strong> ${edge.interface || 'N/A'}<br>
                <strong>Bandwidth:</strong> ${edge.bandwidth || 'N/A'} Mbps<br>
                <strong>Status:</strong> <span style="color: ${edge.status === 'up' ? '#28a745' : '#dc3545'};">${edge.status || 'Unknown'}</span>
            </div>
        `;
    }

    // Event handlers
    async onNodeClick(nodeId) {
        console.log(`🖱️ Node clicked: ${nodeId}`);
        await this.showDeviceDetails(nodeId);
    }

    onNodeDoubleClick(nodeId) {
        console.log(`🖱️ Node double-clicked: ${nodeId}`);
        window.location.href = `/devices?device=${nodeId}`;
    }

    async showDeviceDetails(deviceId) {
        try {
            console.log(`📋 Loading device details for: ${deviceId}`);
            
            const response = await fetch(`/api/devices/${deviceId}/details`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Failed to load device details');
            }
            
            this.displayDeviceModal(data.device);
            
        } catch (error) {
            console.error('❌ Error loading device details:', error);
            this.showAlert(`Failed to load device details: ${error.message}`, 'danger');
        }
    }

    displayDeviceModal(device) {
        const modalTitle = document.getElementById('deviceModalTitle');
        const modalBody = document.getElementById('deviceModalBody');
        
        if (modalTitle) {
            modalTitle.innerHTML = `<i class="fas fa-server me-2"></i>${device.name}`;
        }
        
        if (modalBody) {
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-info-circle me-2"></i>Device Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Name:</strong></td><td>${device.name}</td></tr>
                            <tr><td><strong>IP Address:</strong></td><td>${device.ip}</td></tr>
                            <tr><td><strong>Type:</strong></td><td>${device.type}</td></tr>
                            <tr><td><strong>Role:</strong></td><td>${device.role}</td></tr>
                            <tr><td><strong>Series:</strong></td><td>${device.series}</td></tr>
                            <tr><td><strong>Location:</strong></td><td>${device.location}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-line me-2"></i>Status Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Status:</strong></td><td><span class="badge ${device.status === 'online' ? 'bg-success' : 'bg-danger'}">${device.status}</span></td></tr>
                            <tr><td><strong>Connection:</strong></td><td>${device.connection_status}</td></tr>
                            <tr><td><strong>Uptime:</strong></td><td>${device.uptime}</td></tr>
                            <tr><td><strong>Software:</strong></td><td>${device.software_version}</td></tr>
                            <tr><td><strong>Platform:</strong></td><td>${device.platform}</td></tr>
                            <tr><td><strong>Last Seen:</strong></td><td>${device.last_seen}</td></tr>
                        </table>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="alert alert-info">
                            <i class="fas fa-lightbulb me-2"></i>
                            <strong>DevNet Sandbox Device:</strong> This is a real network device from your Cisco DevNet sandbox environment.
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('deviceModal'));
        modal.show();
    }

    // Control methods
    togglePhysics() {
        this.physicsEnabled = !this.physicsEnabled;
        if (this.network) {
            this.network.setOptions({ physics: { enabled: this.physicsEnabled } });
        }
        
        const button = document.getElementById('togglePhysics');
        if (button) {
            button.innerHTML = `<i class="fas fa-${this.physicsEnabled ? 'pause' : 'play'} me-1"></i>${this.physicsEnabled ? 'Stop' : 'Start'} Physics`;
        }
    }

    fitNetwork() {
        if (this.network) {
            this.network.fit({ animation: { duration: 1000, easingFunction: 'easeInOutQuad' } });
        }
    }

    refreshTopology() {
        console.log('🔄 Refreshing topology...');
        this.loadTopologyData();
    }

    // Utility methods
    showLoading(show) {
        const spinner = document.getElementById('topology-spinner');
        
        if (spinner) {
            spinner.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('topology-error');
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="networkTopology.refreshTopology()">
                        <i class="fas fa-redo me-1"></i>Retry
                    </button>
                </div>
            `;
            errorDiv.style.display = 'block';
        }
        console.error(message);
    }

    showAlert(message, type = 'info') {
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
        }, 5000);
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    cleanup() {
        if (this.network) {
            this.network.destroy();
            this.network = null;
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, initializing topology...');
    window.networkTopology = new NetworkTopology();
});

// Global functions for backward compatibility
function togglePhysics() { window.networkTopology?.togglePhysics(); }
function fitNetwork() { window.networkTopology?.fitNetwork(); }
function refreshTopology() { window.networkTopology?.refreshTopology(); }
function autoLayout() { window.networkTopology?.fitNetwork(); }
function exportTopology() { console.log('Export functionality coming soon!'); }
function toggleLabels() { console.log('Toggle labels functionality coming soon!'); }
function toggleRealTime() { console.log('Real-time toggle functionality coming soon!'); }
function testDeviceConnection() { 
    console.log('Testing device connection...');
    window.networkTopology?.showAlert('Device connection test started!', 'info');
}