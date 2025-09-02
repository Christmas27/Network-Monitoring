#!/usr/bin/env python3
"""Test security alerts method"""

from modules.security_scanner import SecurityScanner

def test_alerts():
    print("🧪 Testing security alerts method...")
    
    scanner = SecurityScanner()
    alerts = scanner.get_security_alerts()
    
    print(f"✅ Found {len(alerts)} security alerts")
    
    if alerts:
        print("📋 First alert details:")
        for key, value in alerts[0].items():
            print(f"  {key}: {value}")
    else:
        print("ℹ️ No active alerts found")
    
    print("✅ get_security_alerts method works!")

if __name__ == "__main__":
    test_alerts()
