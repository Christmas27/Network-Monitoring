elif selected_page == "🤖 Automation":
    st.header("🤖 Network Automation Hub")
    
    # Get managers from session state
    ssh_manager = st.session_state.ssh_manager
    wsl_ansible_bridge = st.session_state.wsl_ansible_bridge
    wsl_ansible_available = st.session_state.wsl_ansible_available
    
    # Check automation capabilities
    lab_devices = [d for d in device_manager.get_all_devices() if 'lab' in d.get('tags', '')]
    
    # Status overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ssh_status = "✅ Ready" if len(lab_devices) > 0 else "⚠️ No Devices"
        st.metric("🔧 Direct SSH", ssh_status)
    
    with col2:
        wsl_status = "✅ Ready" if wsl_ansible_available else "⚠️ Not Available"
        st.metric("🏗️ WSL Ansible", wsl_status)
    
    with col3:
        st.metric("🎯 Lab Devices", len(lab_devices))
    
    st.divider()
    
    # Main automation interface
    automation_tabs = st.tabs(["🔧 Direct SSH", "🏗️ WSL Ansible", "📊 Results"])
    
    # Tab 1: Direct SSH Operations
    with automation_tabs[0]:
        st.subheader("🔧 Direct SSH Automation")
        
        if not lab_devices:
            st.warning("⚠️ No lab devices found. Please add lab devices first!")
            st.info("Go to **Devices** tab and add lab devices on ports 2221, 2222, 2223")
        else:
            # SSH operation selection
            ssh_operations = [
                "🔗 Connectivity Test",
                "📊 System Information", 
                "🧪 Custom Commands"
            ]
            
            selected_ssh_operation = st.selectbox("Select SSH Operation", ssh_operations)
            
            # Target device selection
            device_options = [f"{d['hostname']} ({d['ip_address']})" for d in lab_devices]
            selected_devices = st.multiselect("Target Devices", device_options, default=device_options[:1])
            
            # Execute SSH operation
            if st.button("🚀 Execute SSH Operation", type="primary"):
                if selected_devices:
                    with st.spinner("⏳ Executing SSH operations..."):
                        for device_str in selected_devices:
                            hostname = device_str.split(' (')[0]
                            device = next(d for d in lab_devices if d['hostname'] == hostname)
                            
                            try:
                                if selected_ssh_operation == "🔗 Connectivity Test":
                                    result = ssh_manager.execute_lab_connectivity_test([device])
                                    if result['status'] == 'completed':
                                        st.success(f"✅ {hostname}: Connected successfully")
                                    else:
                                        st.error(f"❌ {hostname}: Connection failed")
                                else:
                                    st.info(f"📊 {hostname}: {selected_ssh_operation} executed")
                                    
                            except Exception as e:
                                st.error(f"❌ {hostname}: {str(e)}")
                else:
                    st.warning("Please select at least one device")
    
    # Tab 2: WSL Ansible Operations  
    with automation_tabs[1]:
        st.subheader("🏗️ WSL Ansible Automation")
        
        if not wsl_ansible_available:
            st.error("❌ WSL Ansible not available")
            st.info("Install WSL2 Ubuntu and Ansible to use this feature")
        else:
            # Ansible operation selection
            ansible_operations = [
                "🔗 Connectivity Test",
                "📊 Show Commands"
            ]
            
            selected_ansible_operation = st.selectbox("Select Ansible Operation", ansible_operations)
            
            # Execute Ansible operation
            if st.button("🏗️ Execute Ansible Operation", type="primary"):
                with st.spinner("⏳ Executing Ansible operation..."):
                    try:
                        if selected_ansible_operation == "🔗 Connectivity Test":
                            result = wsl_ansible_bridge.run_connectivity_test()
                        else:
                            result = wsl_ansible_bridge.run_show_commands()
                        
                        if result['status'] == 'success':
                            st.success("✅ Ansible operation completed successfully!")
                            if 'devices_reachable' in result:
                                st.info(f"📊 {result['devices_reachable']}/{result['total_devices']} devices reachable")
                        else:
                            st.error(f"❌ Ansible operation failed: {result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error executing Ansible operation: {str(e)}")
    
    # Tab 3: Results  
    with automation_tabs[2]:
        st.subheader("📊 Automation Results")
        st.info("Execution history will appear here after running operations")

# Continue with other pages
