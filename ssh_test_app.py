#!/usr/bin/env python3
"""
Simple SSH Integration Test for Streamlit Dashboard

This creates a minimal working integration to demonstrate real SSH execution
"""

import streamlit as st
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.device_manager import DeviceManager
from modules.real_ssh_manager import get_ssh_manager

def test_ssh_integration():
    """Test SSH integration in Streamlit"""
    
    st.title("🔥 Real SSH Lab Integration Test")
    
    # Initialize managers
    device_manager = DeviceManager()
    ssh_manager = get_ssh_manager()
    
    # Get lab devices
    lab_devices = [d for d in device_manager.get_all_devices() if 'lab' in d.get('tags', '')]
    
    # Display status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🐳 Lab Devices", len(lab_devices), "Available")
    
    with col2:
        st.metric("🔧 SSH Engine", "Ready", "Real Execution")
    
    with col3:
        st.metric("🚀 Mode", "LIVE", "No Simulation")
    
    if lab_devices:
        st.success(f"✅ Found {len(lab_devices)} lab devices ready for real SSH execution!")
        
        # Show devices
        st.subheader("📱 Available Lab Devices")
        for device in lab_devices:
            st.write(f"• **{device['hostname']}** ({device['ip_address']}) - {device.get('role', 'unknown').title()}")
        
        st.divider()
        
        # Real SSH operations
        st.subheader("🔥 Real SSH Operations")
        
        operation = st.selectbox(
            "Choose operation:",
            ["🔗 Connectivity Test", "⚙️ Configuration Deployment", "📊 System Monitoring"]
        )
        
        if st.button("🚀 Execute Real SSH Operation", type="primary"):
            with st.spinner(f"Executing {operation} on {len(lab_devices)} devices..."):
                try:
                    if "Connectivity" in operation:
                        result = ssh_manager.execute_lab_connectivity_test(lab_devices)
                    elif "Configuration" in operation:
                        result = ssh_manager.execute_lab_configuration(lab_devices)
                    elif "Monitoring" in operation:
                        result = ssh_manager.execute_lab_monitoring(lab_devices)
                    
                    # Display results
                    if result['status'] == 'completed':
                        st.success(f"🎉 {operation} completed successfully!")
                        st.balloons()
                        
                        # Results summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("⏱️ Duration", f"{result['duration']}s")
                        with col2:
                            st.metric("✅ Success Rate", f"{result['devices_successful']}/{len(lab_devices)}")
                        with col3:
                            st.metric("🔧 Mode", result['execution_mode'])
                        
                        # Show sample output
                        st.subheader("📋 Sample Real Output")
                        for hostname, device_result in result['results'].items():
                            if device_result['status'] == 'success':
                                with st.expander(f"📄 Output from {hostname}"):
                                    if 'output' in device_result:
                                        st.code(device_result['output'][:1000] + '\n...(truncated)', language='bash')
                                    elif 'command_outputs' in device_result:
                                        for cmd_name, cmd_output in device_result['command_outputs'].items():
                                            st.write(f"**{cmd_name.replace('_', ' ').title()}:**")
                                            st.code(cmd_output['stdout'][:800] + '\n...(truncated)', language='bash')
                                            break
                                break
                    else:
                        st.error(f"❌ Operation failed: {result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ No lab devices found!")
        st.info("💡 Run `python setup_lab.py` to add lab devices for real SSH execution.")
        
        # Show how to add devices
        with st.expander("🛠️ How to Add Lab Devices"):
            st.code("""
# 1. Make sure Docker containers are running:
docker start lab-router1 lab-switch1 lab-firewall1

# 2. Run the lab setup script:
python setup_lab.py

# 3. Refresh this page to see your devices!
            """, language="bash")

if __name__ == "__main__":
    test_ssh_integration()
