# 🌐 Network Automation Dashboard

A comprehensive web-based dashboard for network automation, monitoring, and management built with Flask and modern web technologies.

![Dashboard Preview](https://img.shields.io/badge/Status-Portfolio%20Ready-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green?style=for-the-badge&logo=flask)
![Cisco](https://img.shields.io/badge/Cisco-DevNet-orange?style=for-the-badge&logo=cisco)

## ✨ Features

### 🖥️ **Dashboard & Monitoring**
- **Real-time Network Monitoring** - Live device status and performance metrics
- **Dark/Light Theme Toggle** - Professional UI with smooth theme transitions
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Live Data Updates** - Automatic refresh of network statistics and alerts

### 🔧 **Network Management**
- **Device Management** - Add, configure, and monitor network devices
- **Configuration Management** - Backup and restore device configurations
- **Security Scanning** - Automated security assessments and vulnerability detection
- **DevNet Integration** - Connect to real Cisco DevNet sandbox devices

### 📊 **Analytics & Reporting**
- **Performance Metrics** - CPU, memory, interface utilization tracking
- **Network Topology** - Visual representation of network infrastructure
- **Alert System** - Real-time notifications for network issues
- **Historical Data** - Trend analysis and reporting capabilities

### 🔒 **Security Features**
- **Secure Authentication** - User management and session handling
- **Encrypted Communications** - Secure device connections via SSH
- **Audit Logging** - Complete audit trail of all network changes
- **Permission Management** - Role-based access control

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8 or higher
- Git
- Modern web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Christmas27/Network-Monitoring
   cd network-automation-dashboard
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

## 🌟 **Live Demo Modes**

The dashboard automatically detects and adapts to available network resources:

### 🌐 **Live Mode (DevNet Available)**
- Connects to real Cisco DevNet sandbox devices
- Live configuration management
- Real device monitoring and control

### 📡 **Simulation Mode (DevNet Unavailable)**
- High-quality simulated network data
- Perfect for demonstrations and portfolio showcasing
- All features functional with realistic data

## 🔧 **Technology Stack**

### **Backend**
- **Flask** - Python web framework
- **Netmiko** - Network device automation library
- **SQLAlchemy** - Database ORM
- **Cisco DevNet APIs** - Real device integration

### **Frontend**
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive data visualization
- **Font Awesome** - Professional icons
- **Custom CSS** - Dark/light theme system

### **Infrastructure**
- **SQLite** - Lightweight database
- **Docker Ready** - Containerization support
- **RESTful APIs** - Clean API architecture

## 📁 **Project Structure**

```
network-automation-dashboard/
├── 📄 main.py                 # Main Flask application
├── 📁 modules/                # Core application modules
│   ├── device_manager.py      # Device management logic
│   ├── network_monitor.py     # Network monitoring
│   ├── config_manager.py      # Configuration management
│   ├── security_scanner.py    # Security assessment
│   ├── devnet_integration.py  # Cisco DevNet integration
│   └── live_monitoring.py     # Real-time monitoring
├── 📁 templates/              # HTML templates
│   ├── dashboard.html         # Main dashboard
│   ├── devices.html           # Device management
│   ├── config.html            # Configuration page
│   └── security.html          # Security dashboard
├── 📁 static/                 # Static assets
│   ├── css/dashboard.css      # Custom styling
│   ├── js/dashboard.js        # Dashboard JavaScript
│   └── img/                   # Images and icons
├── 📁 config/                 # Configuration files
│   └── config.py              # Application configuration
├── 📁 data/                   # Data storage
├── 📄 requirements.txt        # Python dependencies
└── 📄 README.md              # This file
```

## 🎯 **Key Capabilities**

### **Network Automation**
- ✅ Automated device discovery and inventory
- ✅ Bulk configuration deployment
- ✅ Scheduled backup operations
- ✅ Compliance monitoring and reporting

### **Real-time Monitoring**
- ✅ Live device health monitoring
- ✅ Interface utilization tracking
- ✅ Network performance metrics
- ✅ Alert and notification system

### **Security Management**
- ✅ Vulnerability scanning and assessment
- ✅ Configuration compliance checking
- ✅ Security policy enforcement
- ✅ Threat detection and response

## 📚 **Professional Features**

- **Enterprise-grade Architecture** - Scalable and maintainable codebase
- **Error Handling & Logging** - Comprehensive error management
- **API Documentation** - RESTful API with clear endpoints
- **Testing Framework** - Unit and integration tests included
- **Deployment Ready** - Docker and cloud deployment configurations

## 🏆 **Certifications & Skills Demonstrated**

This project showcases expertise in:
- **Cisco DevNet Associate** - Network programmability and automation
- **CCNA** - Switching, Routing, and Wireless Essentials
- **Network Security** - Security fundamentals and implementation
- **Python Programming** - Advanced scripting and automation
- **Web Development** - Full-stack web application development
- **DevOps Practices** - CI/CD, containerization, and deployment

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 **Acknowledgments**

- Cisco DevNet for providing sandbox environments
- Flask community for excellent documentation
- Bootstrap team for the responsive framework
- All contributors who helped improve this project

---

⭐ **Star this repository if you found it helpful!** ⭐

![Portfolio Ready](https://img.shields.io/badge/Portfolio-Ready-brightgreen?style=for-the-badge)
![Production Ready](https://img.shields.io/badge/Production-Ready-blue?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open-Source-orange?style=for-the-badge)