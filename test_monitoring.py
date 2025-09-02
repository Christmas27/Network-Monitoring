from modules.network_monitor import NetworkMonitor
import json

# Test the monitoring functionality
monitor = NetworkMonitor()

# Test container metrics
containers = monitor.get_lab_containers()
print('Lab containers found:', len(containers))
for container in containers:
    print(f'  - {container["name"]}: {container["status"]}')

# Test SSH response time
ssh_test = monitor.test_ssh_response_time('127.0.0.1', 2221)
print('\nSSH test result:')
print(json.dumps(ssh_test, indent=2))

# Test device metrics collection
device_info = {
    'hostname': 'lab-router1',
    'ip_address': '127.0.0.1:2221'
}

metrics = monitor.collect_device_metrics(device_info)
print('\nDevice metrics:')
print(json.dumps(metrics, indent=2, default=str))
