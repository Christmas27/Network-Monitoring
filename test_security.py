from modules.security_scanner_clean import SecurityScanner
import json

# Test the clean security scanner functionality
scanner = SecurityScanner()

print("🛡️ Testing Clean Security Scanner...")

# Test port scanning
print("\n🔍 Testing Port Scanning...")
try:
    results = scanner.scan_ports('127.0.0.1', [2221, 2222, 2223, 80, 443])
    print(f"Found {len(results)} open ports:")
    for result in results:
        print(f"  - Port {result.port}: {result.service} ({result.status})")
except Exception as e:
    print(f"Port scan error: {e}")

# Test SSH security analysis
print("\n🔐 Testing SSH Security Analysis...")
try:
    ssh_analysis = scanner.analyze_ssh_security('127.0.0.1', 2221)
    print(f"SSH Analysis for 127.0.0.1:2221:")
    print(f"  - Accessible: {ssh_analysis['accessible']}")
    print(f"  - Version: {ssh_analysis.get('version', 'Unknown')}")
    print(f"  - Risk Level: {ssh_analysis['risk_level']}")
    print(f"  - Issues Found: {len(ssh_analysis['security_issues'])}")
except Exception as e:
    print(f"SSH analysis error: {e}")

# Test security overview
print("\n📊 Testing Security Overview...")
try:
    overview = scanner.get_security_overview()
    print(json.dumps(overview, indent=2, default=str))
except Exception as e:
    print(f"Security overview error: {e}")

print("✅ Clean Security Scanner test completed!")
