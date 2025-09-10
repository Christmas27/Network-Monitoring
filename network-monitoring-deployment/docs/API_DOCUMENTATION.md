# 🔌 API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently using session-based authentication. Future versions will include API key authentication.

## Response Format
All API responses follow this format:
```json
{
  "success": boolean,
  "data": object|array,
  "message": string,
  "timestamp": string
}
```

## Error Handling
Error responses include:
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERR_XXX",
  "timestamp": "ISO 8601 timestamp"
}
```

## Endpoints

### Device Management

#### Get All Devices
```http
GET /api/devices
```

**Response:**
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "id": "device-001",
        "name": "Core Router",
        "ip": "192.168.1.1",
        "type": "router",
        "status": "online",
        "last_seen": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 1
  },
  "message": "Devices retrieved successfully"
}
```

#### Get Device Details
```http
GET /api/devices/{device_id}/details
```

**Response:**
```json
{
  "success": true,
  "data": {
    "device": {
      "id": "device-001",
      "name": "Core Router",
      "ip": "192.168.1.1",
      "type": "router",
      "status": "online",
      "uptime": "15 days",
      "software_version": "IOS XE 16.9.04",
      "hardware_info": {...}
    }
  }
}
```

#### Test Device Connection
```http
POST /api/devices/{device_id}/test
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "success",
    "response_time": "15ms",
    "details": {
      "ping": "success",
      "ssh": "success",
      "snmp": "success"
    }
  }
}
```

### Network Topology

#### Get Network Topology
```http
GET /api/network/topology
```

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "device-001",
        "name": "Core Router",
        "type": "router",
        "status": "online",
        "position": {"x": 100, "y": 200}
      }
    ],
    "edges": [
      {
        "id": "connection-001",
        "source": "device-001",
        "target": "device-002",
        "interface": "GigE0/0/1",
        "bandwidth": "1000",
        "status": "up"
      }
    ]
  }
}
```

### Network Monitoring

#### Get Network Health
```http
GET /api/network/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_health": "excellent",
    "uptime_percentage": 99.8,
    "avg_response_time": "15ms",
    "devices_online": 24,
    "total_devices": 25,
    "alerts": []
  }
}
```

#### Get Live Monitoring Data
```http
GET /api/monitoring/live
```

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-01T12:00:00Z",
    "metrics": {
      "cpu_usage": 15.5,
      "memory_usage": 45.2,
      "network_throughput": 1500,
      "active_connections": 150
    }
  }
}
```

### Security

#### Get Security Alerts
```http
GET /api/security/alerts
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert-001",
        "severity": "high",
        "type": "vulnerability",
        "message": "Outdated firmware detected",
        "device_id": "device-001",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 1
  }
}
```

#### Start Security Scan
```http
POST /api/security/scan/{device_id}
```

**Request Body:**
```json
{
  "scan_type": "vulnerability",
  "options": {
    "deep_scan": true,
    "compliance_check": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan-001",
    "status": "started",
    "estimated_duration": "5 minutes"
  }
}
```

### Configuration Management

#### Get Device Configuration
```http
GET /api/config/{device_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "device_id": "device-001",
    "configuration": "! Configuration content here",
    "last_backup": "2024-01-01T12:00:00Z",
    "checksum": "abc123..."
  }
}
```

#### Update Device Configuration
```http
PUT /api/config/{device_id}
```

**Request Body:**
```json
{
  "configuration": "! New configuration content",
  "backup_current": true,
  "validate": true
}
```

## Rate Limiting
- **Development**: No rate limiting
- **Production**: 100 requests per minute per IP

## Status Codes
- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Too Many Requests
- **500**: Internal Server Error

## WebSocket Events (Future)
```javascript
// Real-time device status updates
socket.on('device_status_update', (data) => {
  console.log('Device status changed:', data);
});

// Real-time alerts
socket.on('security_alert', (alert) => {
  console.log('New security alert:', alert);
});
```