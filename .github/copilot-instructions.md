# AI Coding Agent Instructions - Network Monitoring Dashboard

## Project Overview
This is a **hybrid network automation dashboard** with dual frontends: Flask (legacy) and Streamlit (modern). The project implements enterprise-grade network automation using **real SSH execution**, **WSL-based Ansible integration**, and **Docker lab environments** for professional network management.

## Architecture & Key Components

### Dual Frontend Architecture
- **`main.py`**: Flask backend (legacy, port 5000) - JSON APIs for network operations
- **`streamlit_app.py`**: Modern Streamlit frontend (port 8501) - Interactive dashboard with real-time data
- **Shared backend modules**: Both frontends use the same `modules/` directory for consistency

### Core Backend Modules (`modules/`)
- **`device_manager.py`**: SQLite-based device inventory with SSH connectivity testing
- **`real_ssh_manager.py`**: Direct SSH execution engine (bypasses Ansible for speed)
- **`wsl_ansible_bridge.py`**: Windows-to-WSL bridge for professional Ansible execution
- **`ansible_manager_simple.py`**: Traditional Ansible integration with simulation fallback
- **`catalyst_center_integration.py`**: Cisco DevNet integration for enterprise devices
- **`network_monitor.py`**: Performance and availability monitoring
- **`security_scanner.py`**: Vulnerability assessment and compliance checking

### Hybrid Execution Model
The project supports **three execution modes**:
1. **Real SSH** (`real_ssh_manager.py`) - Direct paramiko execution for rapid testing
2. **WSL Ansible** (`wsl_ansible_bridge.py`) - Professional automation via Windows→WSL subprocess bridge
3. **Simulation Mode** - Fallback for environments without lab devices

## Critical Development Patterns

### WSL Integration Pattern
```python
# Windows Python → WSL Ubuntu → Ansible execution
bridge = get_wsl_ansible_bridge()
result = bridge.run_connectivity_test()  # Executes ansible in WSL
```

### Docker Lab Environment
- **Lab location**: `portfolio/local-testing/docker-compose.yml`
- **Containers**: SSH-enabled Linux containers (linuxserver/openssh-server)
- **Access pattern**: localhost:2221,2222,2223 → admin/admin credentials
```bash
# Start lab environment
cd portfolio/local-testing && docker-compose up -d
# Or use project script: python setup_lab.py
```

### Database Schema Convention
All managers use SQLite with **consistent column naming**:
```python
# Always use 'updated_at', never 'last_updated'
conn.execute('SELECT * FROM devices WHERE updated_at > ?', (timestamp,))
```

### Session State Management (Streamlit)
```python
# Initialize managers in session state to persist across interactions
if 'wsl_ansible_bridge' not in st.session_state:
    st.session_state.wsl_ansible_bridge = get_wsl_ansible_bridge()
```

### Error Handling Pattern
```python
# All modules follow this exception handling pattern with emoji logging
try:
    result = some_network_operation()
    logger.info(f"✅ Operation successful: {result}")
    return result
except SpecificException as e:
    logger.error(f"❌ Specific error: {e}")
    return {'status': 'failed', 'error': str(e)}
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    return {'status': 'error', 'message': 'Operation failed'}
```

## Lab Environment Setup

### Docker Lab Architecture
The project uses **containerized lab environments** in multiple locations:
- **Primary lab**: `portfolio/local-testing/docker-compose.yml` - Full environment with dashboard
- **Standalone lab**: `lab/docker/docker-compose.yml` - Devices only
- **Device pattern**: SSH-enabled Linux containers simulating network devices

```bash
# Start complete lab environment (preferred)
cd portfolio/local-testing && docker-compose up -d

# Check lab device status
docker ps --filter name=lab-

# Start individual devices if stopped
docker start lab-router1 lab-switch1 lab-firewall1
```

### WSL Ansible Integration
- **Bridge pattern**: `modules/wsl_ansible_bridge.py` handles Windows→WSL communication
- **UTF-16LE encoding**: WSL commands require proper encoding handling
- **Inventory path**: `/tmp/lab_inventory.yml` in WSL filesystem
- **Collections**: cisco.ios, arista.eos, juniper.junos installed in WSL

```python
# WSL Ansible execution pattern
wsl_bridge = get_wsl_ansible_bridge()
status = wsl_bridge.check_wsl_availability()  # Validates WSL + Ansible
result = wsl_bridge.run_connectivity_test()   # Real Ansible execution
```

## Development Workflows

### Lab Device Management
```bash
# Essential lab workflow
docker ps --filter name=lab-           # Check device status
python test_wsl_integration.py         # Test WSL Ansible bridge
python test_bridge_direct.py           # Debug bridge issues
streamlit run streamlit_app.py          # Launch dashboard on port 8501
```

### Testing Real Automation
```bash
# Progressive testing approach
python test_lab_devices.py             # SSH connectivity only
python test_wsl_integration.py         # WSL Ansible integration  
python test_real_lab.py                # End-to-end automation
```

### Debugging WSL Issues
- **UTF-16 encoding**: WSL `--list` outputs require `encoding='utf-16le'`
- **Distro detection**: Check for "ubuntu" in output but exclude "docker-desktop"
- **Path handling**: Use absolute paths in WSL subprocess calls
```python
# Correct WSL subprocess pattern
subprocess.run(["wsl", "-d", "Ubuntu", "--", "command"], 
               encoding='utf-16le', capture_output=True)
```

### Adding New Network Operations
1. **Implement in `real_ssh_manager.py`** for rapid prototyping
2. **Create Ansible playbook** in WSL for production workflows
3. **Add UI controls** in `streamlit_app.py` automation section
4. **Update device status** using `device_manager.update_device_status()`

### Device Type Handling
Lab devices are **Linux containers**, not actual network devices:
```python
# Inventory must use SSH connection, not network_cli
ansible_connection: ssh  # For lab containers
ansible_network_os: cisco_ios  # Only for real Cisco devices
```

### CSS Styling Convention
The Streamlit app uses **Nordic dark theme** with specific color codes:
```python
# Standard color palette used throughout UI
background: #2e3440
text: #d8dee9  
accent: #5e81ac
success: #a3be8c
warning: #ebcb8b
error: #bf616a
```

## Integration Points

### Multi-Vendor Device Support
```python
# Device type mapping for different execution contexts
device_type_mapping = {
    'cisco_ios': {'port': 22, 'platform': 'cisco'},
    'linux': {'port': 22, 'platform': 'linux'},  # Lab containers
    'juniper_junos': {'port': 22, 'platform': 'juniper'}
}
```

### Cross-Component Communication
- **Device inventory** shared between all modules via SQLite
- **Session state** preserves manager instances in Streamlit
- **Result formatting** consistent across SSH and Ansible executions

## Key Files for Common Tasks

- **Device management**: `modules/device_manager.py` + `streamlit_app.py` (Devices tab)
- **Real automation**: `modules/real_ssh_manager.py` + `modules/wsl_ansible_bridge.py`
- **Lab setup**: `portfolio/local-testing/docker-compose.yml` + `setup_lab.py`
- **UI styling**: CSS sections in `streamlit_app.py` (Nordic theme)
- **Configuration**: `config/config.py` + `modules/config.py`
- **Testing**: `test_wsl_integration.py` + `test_bridge_direct.py`

## Testing Strategy
- **Unit tests**: Individual module functionality
- **Integration tests**: `test_wsl_integration.py` for WSL Ansible bridge
- **Lab tests**: `test_real_lab.py` for end-to-end automation with Docker devices
- **UI testing**: Manual verification via Streamlit automation tabs
- **Debug tests**: `test_bridge_direct.py` for WSL communication troubleshooting

This project prioritizes **real network automation** over simulations, **professional Ansible workflows** alongside rapid SSH testing, and **enterprise-ready patterns** while maintaining development flexibility.
