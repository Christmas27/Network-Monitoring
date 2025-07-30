# Network Automation Dashboard 🌐

A comprehensive network automation and monitoring dashboard built with Python Flask, showcasing network infrastructure management, cybersecurity scanning, and automation capabilities.

![Dashboard Preview](static/images/dashboard-preview.png)

## 🚀 Features

- **🔧 Device Management**: Multi-vendor network device support (Cisco, Juniper, Arista, HP)
- **📊 Real-time Monitoring**: Live network status and performance metrics
- **⚙️ Configuration Management**: Automated configuration deployment and backup
- **🔒 Security Scanning**: Vulnerability assessment and compliance checking
- **🌐 API Integration**: RESTful endpoints for all operations
- **🎨 Modern UI**: Responsive web interface with dark mode

## 🛠️ Technologies Used

- **Backend**: Python Flask, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Network Libraries**: Netmiko, NAPALM, Paramiko
- **APIs**: Flask-CORS, RESTful design
- **Monitoring**: Real-time charts with Chart.js

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Network devices or access to Cisco DevNet Sandbox

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/network-automation-dashboard.git
cd network-automation-dashboard

# Run automated setup
python setup.py

# Activate virtual environment (Windows)
network_dashboard_env\Scripts\activate

# Start the application
python main.py
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/network-automation-dashboard.git
cd network-automation-dashboard

# Create virtual environment
python -m venv network_dashboard_env

# Activate virtual environment
# Windows:
network_dashboard_env\Scripts\activate
# Linux/Mac:
source network_dashboard_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Start application
python main.py
```

## 🌐 Access the Dashboard

Open your browser to: `http://localhost:5000`

## 📱 Dashboard Sections

### 🖥️ Main Dashboard
- Real-time network device status
- Performance metrics and charts
- Quick actions and alerts
- Network topology overview

### 🔧 Device Management
- Add/remove network devices
- Test device connectivity
- View device information
- Manage SSH/SNMP credentials

### ⚙️ Configuration Management
- Deploy configurations using Jinja2 templates
- Backup device configurations
- Configuration version control
- Template library management

### 🔒 Security Scanner
- Port scanning and service detection
- Vulnerability assessment
- Compliance checking (NIST, CIS, DISA STIG)
- Security recommendations and remediation

## 🌐 Integration Options

### Cisco DevNet Sandbox
Built-in integration with Cisco DevNet Always-On Sandbox:
- IOS XE devices
- NX-OS switches
- ASA firewalls

Access free Cisco devices for testing: [DevNet Sandbox](https://devnetsandbox.cisco.com/)

### Virtual Lab Support
- **GNS3**: Import topologies and manage virtual devices
- **EVE-NG**: Connect to virtual network labs
- **Packet Tracer**: Integration with Cisco Packet Tracer
- **Docker**: Containerized network services

## 📁 Project Structure

```
network-automation-dashboard/
├── main.py                    # Main Flask application
├── setup.py                   # Automated setup script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── config/
│   ├── config.py             # Configuration management
│   └── devices.json          # Device configurations (not in git)
├── network_modules/
│   ├── device_manager.py     # Device management logic
│   ├── config_manager.py     # Configuration management
│   └── security_scanner.py   # Security scanning tools
├── templates/                # HTML templates
│   ├── index.html           # Main dashboard
│   ├── devices.html         # Device management
│   ├── config.html          # Configuration management
│   └── security.html        # Security scanner
├── static/                   # Frontend assets
│   ├── css/
│   ├── js/
│   └── images/
├── data/                     # Database files (not in git)
├── logs/                     # Application logs (not in git)
└── backups/                  # Configuration backups (not in git)
```

## 🔧 Configuration

1. **Copy environment template**:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** with your settings:
   ```env
   SECRET_KEY=your-secret-key-here
   FLASK_DEBUG=True
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   ```

3. **Add your device credentials** (optional):
   ```env
   PRIVATE_DEVICE_1_HOST=192.168.1.1
   PRIVATE_DEVICE_1_USER=admin
   PRIVATE_DEVICE_1_PASS=your_password
   ```

## 🔒 Security Considerations

- ✅ Credentials stored in environment variables
- ✅ Device configurations excluded from version control
- ✅ Input validation on all endpoints
- ✅ HTTPS recommended for production deployment
- ✅ Secret key management for session security

## 🧪 Testing

```bash
# Activate virtual environment
network_dashboard_env\Scripts\activate

# Run basic connectivity test
python -c "from network_modules.device_manager import DeviceManager; print('✅ Modules loaded successfully')"

# Test DevNet Sandbox connectivity (requires internet)
python -c "from main import app; print('✅ Application loads successfully')"
```

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
1. Set `FLASK_DEBUG=False` in `.env`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Configure reverse proxy (nginx, Apache)
4. Set up SSL/TLS certificates
5. Use environment-specific configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**[Your Name]** - Computer Science Student
- 🎓 **Certifications**: Cisco DevNet Associate, CCNA SRWE, CCNA ENSA, CCNA Network Security
- 🎯 **Interests**: Network Automation, Cybersecurity, Infrastructure Programming
- 📧 **Contact**: [your.email@example.com]
- 🔗 **LinkedIn**: [Your LinkedIn Profile]
- 🐙 **GitHub**: [Your GitHub Profile]

## 🏆 Skills Demonstrated

This portfolio project showcases proficiency in:

### 🌐 **Computer Networks**
- Multi-vendor device management and automation
- Network monitoring and performance analysis
- SNMP and SSH connectivity protocols
- Network topology discovery and mapping

### 🔒 **Cybersecurity**
- Vulnerability assessment and security scanning
- Compliance checking against industry standards
- Security configuration auditing
- Threat detection and alerting

### 🤖 **Automation & Programming**
- Python network automation with Netmiko/NAPALM
- RESTful API design and implementation
- Configuration template management with Jinja2
- Automated testing and deployment workflows

### 💻 **Full-Stack Development**
- Backend development with Python Flask
- Frontend development with HTML5/CSS3/JavaScript
- Database design and management
- Real-time web applications with WebSocket

## 📊 Portfolio Value

This project demonstrates practical application of:
- **Cisco DevNet** skills for network programmability
- **CCNA SRWE** knowledge in switching and routing
- **CCNA ENSA** expertise in enterprise networking
- **Network Security** understanding of security principles

Perfect for showcasing to potential employers in:
- Network Engineering roles
- DevOps and Automation positions
- Cybersecurity analyst positions
- Full-stack developer roles with network focus

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/network-automation-dashboard/issues) page
2. Review the setup instructions in this README
3. Ensure all dependencies are properly installed
4. Check the logs in the `logs/` directory

---

⭐ **Star this repository if you found it helpful!**