# Network Monitoring Dashboard

A professional network monitoring and automation platform built with Python Flask, integrating with Cisco DevNet APIs for enterprise network management.

## 🚀 Live Demo
**[Your Render URL Here]**

## 📋 Features

### Core Functionality
- **Real-time Network Monitoring** - Live device status and performance metrics
- **Configuration Management** - Automated device configuration with Jinja2 templates
- **Security Scanning** - Network vulnerability assessment and compliance checking
- **Network Topology** - Interactive visualization of network infrastructure
- **Device Management** - CRUD operations for network devices

### Enterprise Integration
- **Cisco DevNet API Integration** - Real network device management
- **Catalyst Center Support** - Direct integration with Cisco's network controller
- **SNMP Monitoring** - Standard network protocol support
- **SSH Automation** - Secure device configuration via Netmiko

### Technical Features
- **Responsive Web Interface** - Modern, mobile-friendly design
- **RESTful API** - JSON endpoints for all operations
- **Database Management** - SQLite with comprehensive data models
- **Error Handling** - Graceful fallbacks and comprehensive logging
- **Production Ready** - Cloud deployment with proper configuration

## 🛠️ Technology Stack

### Backend
- **Python 3.11** - Core application language
- **Flask** - Web application framework
- **SQLite** - Database for device and configuration storage
- **Gunicorn** - Production WSGI server

### Network Automation
- **Netmiko** - SSH connections to network devices
- **NAPALM** - Network device abstraction layer
- **Requests** - HTTP client for API integration
- **PyYAML** - Configuration file processing

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript** - Interactive functionality
- **Bootstrap** - Responsive design framework
- **Chart.js** - Data visualization

### DevOps & Deployment
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline
- **Render** - Cloud hosting platform
- **Git** - Version control

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │────│   Flask App      │────│   Network APIs  │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • REST Routes    │    │ • Cisco DevNet  │
│ • Device Mgmt   │    │ • Data Models    │    │ • SNMP          │
│ • Configuration │    │ • Business Logic │    │ • SSH           │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │   SQLite DB      │
                       │                  │
                       │ • Devices        │
                       │ • Configurations │
                       │ • Monitoring     │
                       │ • Security       │
                       └──────────────────┘
```

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Git
- (Optional) Cisco DevNet sandbox access

### Local Development
```bash
# Clone repository
git clone https://github.com/Christmas27/Network-Monitoring.git
cd Network-Monitoring

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

Visit `http://localhost:5000` to access the dashboard.

### Environment Variables
```bash
# Flask Configuration
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
SECRET_KEY=your-secret-key

# DevNet Integration (Optional)
CATALYST_CENTER_HOST=sandboxdnac2.cisco.com
CATALYST_CENTER_USERNAME=devnetuser
CATALYST_CENTER_PASSWORD=Cisco123!
```

## 🔧 Deployment

### Render (Recommended)
1. Fork this repository
2. Connect to Render
3. Set environment variables
4. Deploy automatically from main branch

### Docker
```bash
# Build image
docker build -t network-monitor .

# Run container
docker run -p 5000:5000 network-monitor
```

## 📊 CI/CD Pipeline

Automated pipeline with GitHub Actions:
- ✅ **Code Quality** - Linting with flake8
- ✅ **Testing** - Unit tests with pytest
- ✅ **Security** - Dependency scanning
- ✅ **Build** - Docker image creation
- ✅ **Deploy** - Automatic deployment to cloud

## 🎓 Professional Skills Demonstrated

### Networking & Automation
- Cisco DevNet Associate certification knowledge
- Enterprise network device management
- Network monitoring and troubleshooting
- Configuration automation and templating

### Software Development
- Full-stack web development
- RESTful API design
- Database modeling and management
- Error handling and logging

### DevOps & Cloud
- Containerization with Docker
- CI/CD pipeline implementation
- Cloud deployment and scaling
- Infrastructure as Code principles

### Security
- Network vulnerability assessment
- Secure API integration
- Credential management
- Access control implementation

## 🏆 Certifications & Learning

This project demonstrates practical application of:
- **Cisco CCNA** - Network fundamentals and protocols
- **Cisco DevNet Associate** - Network automation and APIs
- **Enterprise Network Security** - Security best practices
- **Switching, Routing & Wireless Essentials** - Infrastructure management

## 📈 Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced network analytics
- [ ] Multi-vendor device support
- [ ] Network automation workflows
- [ ] Integration with monitoring tools (Grafana, Prometheus)
- [ ] Mobile application development

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome! Please feel free to:
- Open issues for bugs or feature requests
- Submit pull requests for improvements
- Share your thoughts on the implementation

## 📞 Contact

**[Your Name]**
- LinkedIn: [Your LinkedIn Profile]
- Email: [Your Email]
- Portfolio: [Your Portfolio Website]

---

*Built with ❤️ and lots of ☕ by a Computer Science student passionate about network automation and full-stack development.*
