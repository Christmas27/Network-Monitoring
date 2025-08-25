/* Automation Management JavaScript */

class AutomationManager {
    constructor() {
        this.init();
    }

    init() {
        console.log('🤖 Automation page loaded');
        this.setupEventListeners();
        this.loadAutomationData();
    }

    setupEventListeners() {
        // Playbook execution form
        const form = document.getElementById('playbookExecutionForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.executePlaybook();
            });
        }

        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadAutomationStatus();
        }, 30000);
    }

    async loadAutomationData() {
        try {
            await Promise.all([
                this.loadAutomationStatus(),
                this.loadPlaybooks()
            ]);
        } catch (error) {
            console.error('Error loading automation data:', error);
            this.showAlert('Failed to load automation data', 'danger');
        }
    }

    async loadAutomationStatus() {
        try {
            const response = await fetch('/api/automation/status');
            const data = await response.json();
            
            if (response.ok) {
                this.updateStatusCards(data);
            } else {
                throw new Error(data.error || 'Failed to load status');
            }
        } catch (error) {
            console.error('Error loading automation status:', error);
        }
    }

    async loadPlaybooks() {
        try {
            const response = await fetch('/api/automation/playbooks');
            const data = await response.json();
            
            if (response.ok) {
                this.updatePlaybooksList(data.playbooks);
                this.updatePlaybookSelect(data.playbooks);
            } else {
                throw new Error(data.error || 'Failed to load playbooks');
            }
        } catch (error) {
            console.error('Error loading playbooks:', error);
            this.showAlert('Failed to load playbooks', 'warning');
        }
    }

    updateStatusCards(status) {
        // Update status card
        const statusElement = document.getElementById('automationStatus');
        if (statusElement) {
            statusElement.textContent = status.status.replace('_', ' ').toUpperCase();
        }

        // Update playbook count
        const countElement = document.getElementById('playbookCount');
        if (countElement) {
            countElement.textContent = status.playbooks_count || 0;
        }

        // Update Ansible status
        const ansibleElement = document.getElementById('ansibleStatus');
        if (ansibleElement) {
            ansibleElement.textContent = status.ansible_available ? 'Ready' : 'Development';
        }
    }

    updatePlaybooksList(playbooks) {
        const container = document.getElementById('playbooksList');
        if (!container) return;

        if (playbooks && playbooks.length > 0) {
            container.innerHTML = playbooks.map(playbook => `
                <div class="card mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${this.escapeHtml(playbook.name)}</h6>
                                <small class="text-muted">${this.escapeHtml(playbook.description || 'No description')}</small>
                                <br>
                                <small class="text-info">Modified: ${new Date(playbook.modified).toLocaleDateString()}</small>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-outline-primary" 
                                        onclick="automationManager.selectPlaybook('${playbook.name}')">
                                    <i class="fas fa-check"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-info-circle me-2"></i>
                    No playbooks available
                </div>
            `;
        }
    }

    updatePlaybookSelect(playbooks) {
        const select = document.getElementById('playbookSelect');
        if (!select) return;

        // Clear existing options except the first one
        select.innerHTML = '<option value="">Choose a playbook...</option>';

        if (playbooks && playbooks.length > 0) {
            playbooks.forEach(playbook => {
                const option = document.createElement('option');
                option.value = playbook.name;
                option.textContent = `${playbook.name} - ${playbook.description || 'No description'}`;
                select.appendChild(option);
            });
        }
    }

    selectPlaybook(playbookName) {
        const select = document.getElementById('playbookSelect');
        if (select) {
            select.value = playbookName;
            this.showAlert(`Selected playbook: ${playbookName}`, 'info');
        }
    }

    async executePlaybook() {
        const playbookName = document.getElementById('playbookSelect').value;
        const limitHosts = document.getElementById('limitHosts').value;
        const extraVarsText = document.getElementById('extraVars').value;

        if (!playbookName) {
            this.showAlert('Please select a playbook to execute', 'warning');
            return;
        }

        // Parse extra variables
        let extraVars = {};
        if (extraVarsText.trim()) {
            try {
                extraVars = JSON.parse(extraVarsText);
            } catch (error) {
                this.showAlert('Invalid JSON in extra variables', 'danger');
                return;
            }
        }

        // Show loading state
        this.showExecutionLoading();

        try {
            const response = await fetch('/api/automation/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    playbook_name: playbookName,
                    limit: limitHosts || null,
                    extra_vars: extraVars
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showExecutionResult(data.execution_result);
                this.showAlert('Playbook execution completed!', 'success');
                
                // Update last execution time
                const lastExecElement = document.getElementById('lastExecution');
                if (lastExecElement) {
                    lastExecElement.textContent = new Date().toLocaleTimeString();
                }
            } else {
                throw new Error(data.error || 'Execution failed');
            }

        } catch (error) {
            console.error('Error executing playbook:', error);
            this.showExecutionError(error.message);
            this.showAlert(`Execution failed: ${error.message}`, 'danger');
        }
    }

    showExecutionLoading() {
        const container = document.getElementById('executionResults');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Executing...</span>
                    </div>
                    <div class="mt-2">
                        <strong>Executing playbook...</strong>
                    </div>
                </div>
            `;
        }
    }

    showExecutionResult(result) {
        const container = document.getElementById('executionResults');
        if (!container) return;

        const statusClass = result.status === 'success' ? 'success' : 
                           result.status === 'failed' ? 'danger' : 'info';
        const statusIcon = result.status === 'success' ? 'check-circle' : 
                          result.status === 'failed' ? 'times-circle' : 'info-circle';

        container.innerHTML = `
            <div class="alert alert-${statusClass}">
                <h6><i class="fas fa-${statusIcon} me-2"></i>Execution Result</h6>
                <strong>Status:</strong> ${result.status}<br>
                <strong>Playbook:</strong> ${result.playbook}<br>
                <strong>Job ID:</strong> ${result.job_id}<br>
                <strong>Duration:</strong> ${result.duration}s<br>
                ${result.message ? `<strong>Message:</strong> ${result.message}<br>` : ''}
                <small class="text-muted">Executed at: ${new Date(result.start_time).toLocaleString()}</small>
            </div>
            
            ${result.stdout ? `
                <div class="mt-3">
                    <h6>Output:</h6>
                    <pre class="bg-light p-3 rounded" style="max-height: 300px; overflow-y: auto;"><code>${this.escapeHtml(result.stdout)}</code></pre>
                </div>
            ` : ''}
            
            ${result.devices_targeted ? `
                <div class="mt-2">
                    <small class="text-info">
                        <i class="fas fa-server me-1"></i>
                        Targeted ${result.devices_targeted} device(s)
                    </small>
                </div>
            ` : ''}
        `;
    }

    showExecutionError(errorMessage) {
        const container = document.getElementById('executionResults');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Execution Failed</h6>
                    <strong>Error:</strong> ${this.escapeHtml(errorMessage)}
                </div>
            `;
        }
    }

    async generateInventory() {
        try {
            this.showInventoryLoading();
            
            const response = await fetch('/api/automation/inventory');
            const data = await response.json();

            if (response.ok) {
                this.showInventoryResult(data);
                this.showAlert('Inventory generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate inventory');
            }

        } catch (error) {
            console.error('Error generating inventory:', error);
            this.showInventoryError(error.message);
            this.showAlert(`Failed to generate inventory: ${error.message}`, 'danger');
        }
    }

    showInventoryLoading() {
        const container = document.getElementById('inventoryDisplay');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Generating...</span>
                    </div>
                    <div class="mt-2 text-muted">Generating inventory...</div>
                </div>
            `;
        }
    }

    showInventoryResult(data) {
        const container = document.getElementById('inventoryDisplay');
        if (!container) return;

        const inventory = data.inventory;
        const deviceCount = data.device_count;

        // Count devices by group
        const groups = inventory.all?.children || {};
        const groupStats = Object.keys(groups).map(groupName => {
            const hostCount = Object.keys(groups[groupName]?.hosts || {}).length;
            return { name: groupName, count: hostCount };
        }).filter(group => group.count > 0);

        container.innerHTML = `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">Device Summary</h6>
                    <span class="badge bg-primary">${deviceCount} devices</span>
                </div>
                
                ${groupStats.map(group => `
                    <div class="d-flex justify-content-between py-1">
                        <span class="text-capitalize">${group.name}:</span>
                        <span class="badge bg-secondary">${group.count}</span>
                    </div>
                `).join('')}
            </div>
            
            <div class="mb-2">
                <small class="text-muted">
                    <i class="fas fa-file me-1"></i>
                    Saved to: ${data.inventory_file}
                </small>
            </div>
            
            <button class="btn btn-sm btn-outline-info w-100" onclick="automationManager.showFullInventory('${encodeURIComponent(JSON.stringify(inventory))}')">
                <i class="fas fa-eye me-1"></i>View Full Inventory
            </button>
        `;
    }

    showInventoryError(errorMessage) {
        const container = document.getElementById('inventoryDisplay');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error: ${this.escapeHtml(errorMessage)}
                </div>
            `;
        }
    }

    showFullInventory(encodedInventory) {
        try {
            const inventory = JSON.parse(decodeURIComponent(encodedInventory));
            const yamlContent = this.objectToYaml(inventory);
            
            // Create modal or new window to show full inventory
            const modal = `
                <div class="modal fade" id="inventoryModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Generated Ansible Inventory</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <pre class="bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto;"><code>${this.escapeHtml(yamlContent)}</code></pre>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                <button type="button" class="btn btn-primary" onclick="automationManager.downloadInventory('${encodedInventory}')">
                                    <i class="fas fa-download me-1"></i>Download
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('inventoryModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to body and show it
            document.body.insertAdjacentHTML('beforeend', modal);
            const modalElement = new bootstrap.Modal(document.getElementById('inventoryModal'));
            modalElement.show();
            
        } catch (error) {
            this.showAlert('Error displaying inventory', 'danger');
        }
    }

    downloadInventory(encodedInventory) {
        try {
            const inventory = JSON.parse(decodeURIComponent(encodedInventory));
            const yamlContent = this.objectToYaml(inventory);
            
            const blob = new Blob([yamlContent], { type: 'text/yaml' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'ansible_inventory.yml';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showAlert('Inventory downloaded successfully!', 'success');
        } catch (error) {
            this.showAlert('Error downloading inventory', 'danger');
        }
    }

    objectToYaml(obj, indent = 0) {
        // Simple YAML converter for display purposes
        let yaml = '';
        const spaces = '  '.repeat(indent);
        
        for (const [key, value] of Object.entries(obj)) {
            yaml += `${spaces}${key}:`;
            
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                yaml += '\n' + this.objectToYaml(value, indent + 1);
            } else if (Array.isArray(value)) {
                yaml += '\n';
                value.forEach(item => {
                    yaml += `${spaces}  - ${item}\n`;
                });
            } else {
                yaml += ` ${value}\n`;
            }
        }
        
        return yaml;
    }

    refreshAutomationData() {
        console.log('🔄 Refreshing automation data...');
        this.loadAutomationData();
    }

    showAlert(message, type = 'info') {
        // Create and show Bootstrap alert
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
        alertContainer.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'danger' ? 'exclamation-triangle' : 'info'}-circle me-2"></i>
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertContainer);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.parentNode.removeChild(alertContainer);
            }
        }, 5000);
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Global functions for backward compatibility
function refreshAutomationData() {
    if (window.automationManager) {
        window.automationManager.refreshAutomationData();
    }
}

function generateInventory() {
    if (window.automationManager) {
        window.automationManager.generateInventory();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.automationManager = new AutomationManager();
    console.log('🤖 Automation Manager initialized');
});
