#!/usr/bin/env python3
"""
Topology Page - Network Topology Visualization and Discovery
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from plotly.subplots import make_subplots

# Import our modular components
from components.forms import device_selector
from components.tables import topology_table, connection_table
from components.metrics import topology_metrics_row
from utils.shared_utils import (
    PerformanceMonitor,
    notification_manager,
    show_loading_spinner
)
from utils.data_processing import DataProcessor

logger = logging.getLogger(__name__)

class TopologyPage:
    """Network topology visualization and discovery page"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.data_processor = DataProcessor()
    
    def render(self):
        """Render the topology page"""
        # Page header
        st.markdown("# 🌐 Network Topology")
        st.markdown("Visualize network topology, discover connections, and analyze network structure")
        st.markdown("---")
        
        # Get managers from session state
        device_manager = st.session_state.get('device_manager')
        network_monitor = st.session_state.get('network_monitor')
        
        if not device_manager:
            st.error("❌ Device manager not initialized")
            return
        
        # Topology tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🗺️ Network Map", 
            "🔍 Discovery", 
            "📊 Analysis",
            "⚙️ Configuration"
        ])
        
        with tab1:
            self._render_network_map(device_manager, network_monitor)
        
        with tab2:
            self._render_discovery_tab(device_manager, network_monitor)
        
        with tab3:
            self._render_analysis_tab(device_manager, network_monitor)
        
        with tab4:
            self._render_configuration_tab(device_manager)
    
    def _render_network_map(self, device_manager, network_monitor):
        """Render interactive network topology map"""
        st.markdown("### 🗺️ Interactive Network Map")
        
        # Map controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            layout_type = st.selectbox(
                "Layout:",
                ["Spring", "Circular", "Hierarchical", "Grid", "Force-directed"]
            )
        
        with col2:
            show_labels = st.checkbox("Show Labels", value=True)
        
        with col3:
            show_connections = st.checkbox("Show Connections", value=True)
        
        with col4:
            if st.button("🔄 Refresh Map", type="primary"):
                st.session_state.topology_data = None
                st.rerun()
        
        # Generate topology map
        try:
            devices = device_manager.get_all_devices()
            
            if not devices:
                st.info("No devices available. Add devices to see network topology.")
                return
            
            # Get or generate topology data
            if 'topology_data' not in st.session_state:
                st.session_state.topology_data = self._generate_topology_data(devices, network_monitor)
            
            topology_data = st.session_state.topology_data
            
            # Topology metrics overview
            topology_metrics_row(topology_data)
            
            # Render network visualization
            self._render_network_visualization(topology_data, layout_type, show_labels, show_connections)
            
            # Device details panel
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📋 Device List")
                topology_table(devices, device_manager)
            
            with col2:
                st.markdown("### 🔗 Connection Summary")
                self._render_connection_summary(topology_data)
            
        except Exception as e:
            logger.error(f"❌ Error rendering network map: {e}")
            st.error("Error loading network topology map")
    
    def _render_discovery_tab(self, device_manager, network_monitor):
        """Render network discovery interface"""
        st.markdown("### 🔍 Network Discovery")
        st.markdown("Discover network devices and automatically map topology")
        
        # Discovery controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            discovery_method = st.selectbox(
                "Discovery Method:",
                ["SNMP Discovery", "CDP/LLDP", "ARP Table Scan", "Ping Sweep", "Manual Entry"]
            )
            
            if discovery_method == "Ping Sweep":
                network_range = st.text_input(
                    "Network Range:",
                    placeholder="192.168.1.0/24",
                    help="Enter CIDR notation for network discovery"
                )
            elif discovery_method == "SNMP Discovery":
                col_ip, col_community = st.columns(2)
                with col_ip:
                    seed_device = st.text_input("Seed Device IP:", placeholder="192.168.1.1")
                with col_community:
                    snmp_community = st.text_input("SNMP Community:", value="public", type="password")
        
        with col2:
            st.markdown("**Discovery Options:**")
            include_offline = st.checkbox("Include Offline Devices", value=False)
            auto_add = st.checkbox("Auto-add Discovered Devices", value=True)
            deep_scan = st.checkbox("Deep Scan (Slower)", value=False)
        
        # Discovery actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Discovery", type="primary", use_container_width=True):
                self._start_network_discovery(
                    device_manager, discovery_method, 
                    locals().get('network_range'), locals().get('seed_device'),
                    include_offline, auto_add, deep_scan
                )
        
        with col2:
            if st.button("⏹️ Stop Discovery", use_container_width=True):
                self._stop_network_discovery()
        
        with col3:
            if st.button("📊 Discovery Report", use_container_width=True):
                self._show_discovery_report()
        
        # Discovery progress and results
        if st.session_state.get('discovery_running', False):
            self._render_discovery_progress()
        
        # Discovery history
        st.markdown("### 📋 Discovery History")
        self._render_discovery_history(device_manager)
        
        # Discovered devices
        if st.session_state.get('discovered_devices'):
            st.markdown("### 🔍 Discovered Devices")
            self._render_discovered_devices(device_manager)
    
    def _render_analysis_tab(self, device_manager, network_monitor):
        """Render topology analysis interface"""
        st.markdown("### 📊 Topology Analysis")
        st.markdown("Analyze network structure, identify bottlenecks, and optimize topology")
        
        try:
            devices = device_manager.get_all_devices()
            
            if not devices:
                st.info("No devices available for analysis")
                return
            
            # Analysis controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                analysis_type = st.selectbox(
                    "Analysis Type:",
                    ["Network Centrality", "Path Analysis", "Redundancy Analysis", "Bottleneck Detection"]
                )
            
            with col2:
                if st.button("📊 Run Analysis", type="primary", use_container_width=True):
                    self._run_topology_analysis(devices, analysis_type)
            
            with col3:
                if st.button("📤 Export Analysis", use_container_width=True):
                    self._export_topology_analysis()
            
            # Analysis results
            if st.session_state.get('analysis_results'):
                self._render_analysis_results(st.session_state.analysis_results, analysis_type)
            
            # Network metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Network Metrics")
                self._render_network_metrics(devices)
            
            with col2:
                st.markdown("### 🎯 Optimization Suggestions")
                self._render_optimization_suggestions(devices)
            
            # Path analysis
            st.markdown("### 🛤️ Path Analysis")
            self._render_path_analysis(devices)
            
        except Exception as e:
            logger.error(f"❌ Error in topology analysis: {e}")
            st.error("Error loading topology analysis")
    
    def _render_configuration_tab(self, device_manager):
        """Render topology configuration interface"""
        st.markdown("### ⚙️ Topology Configuration")
        st.markdown("Configure topology discovery settings and visualization preferences")
        
        # Discovery settings
        st.markdown("#### 🔍 Discovery Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**SNMP Settings:**")
            default_community = st.text_input("Default SNMP Community:", value="public")
            snmp_timeout = st.number_input("SNMP Timeout (seconds):", min_value=1, max_value=30, value=5)
            snmp_retries = st.number_input("SNMP Retries:", min_value=0, max_value=5, value=2)
        
        with col2:
            st.markdown("**Discovery Settings:**")
            discovery_interval = st.number_input("Auto-discovery Interval (hours):", min_value=1, max_value=168, value=24)
            max_hops = st.number_input("Maximum Hops:", min_value=1, max_value=10, value=5)
            concurrent_scans = st.number_input("Concurrent Scans:", min_value=1, max_value=50, value=10)
        
        # Visualization settings
        st.markdown("#### 🎨 Visualization Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Layout Settings:**")
            default_layout = st.selectbox("Default Layout:", ["Spring", "Circular", "Hierarchical", "Grid"])
            node_size = st.slider("Node Size:", min_value=10, max_value=100, value=30)
            edge_width = st.slider("Edge Width:", min_value=1, max_value=10, value=2)
        
        with col2:
            st.markdown("**Color Settings:**")
            online_color = st.color_picker("Online Devices:", value="#28a745")
            offline_color = st.color_picker("Offline Devices:", value="#dc3545")
            warning_color = st.color_picker("Warning Devices:", value="#ffc107")
        
        # Filtering settings
        st.markdown("#### 🔽 Filtering Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            device_types_filter = st.multiselect(
                "Show Device Types:",
                ["Router", "Switch", "Firewall", "Access Point", "Server", "Workstation"],
                default=["Router", "Switch", "Firewall"]
            )
        
        with col2:
            status_filter = st.multiselect(
                "Show Device Status:",
                ["Online", "Offline", "Warning", "Unknown"],
                default=["Online", "Warning"]
            )
        
        # Save settings
        if st.button("💾 Save Configuration", type="primary"):
            self._save_topology_configuration({
                'snmp': {
                    'community': default_community,
                    'timeout': snmp_timeout,
                    'retries': snmp_retries
                },
                'discovery': {
                    'interval': discovery_interval,
                    'max_hops': max_hops,
                    'concurrent_scans': concurrent_scans
                },
                'visualization': {
                    'layout': default_layout,
                    'node_size': node_size,
                    'edge_width': edge_width,
                    'colors': {
                        'online': online_color,
                        'offline': offline_color,
                        'warning': warning_color
                    }
                },
                'filters': {
                    'device_types': device_types_filter,
                    'status': status_filter
                }
            })
    
    def _generate_topology_data(self, devices, network_monitor):
        """Generate topology data from devices"""
        try:
            # Create sample topology connections
            topology_data = {
                'nodes': [],
                'edges': [],
                'metrics': {}
            }
            
            # Add nodes (devices)
            for i, device in enumerate(devices):
                node = {
                    'id': device['id'],
                    'label': device['hostname'],
                    'type': device.get('device_type', 'unknown'),
                    'ip': device['ip_address'],
                    'status': device.get('status', 'unknown'),
                    'x': np.random.uniform(0, 10),
                    'y': np.random.uniform(0, 10)
                }
                topology_data['nodes'].append(node)
            
            # Add edges (connections) - sample connections
            if len(devices) > 1:
                # Create a sample network topology
                for i in range(len(devices) - 1):
                    edge = {
                        'source': devices[i]['id'],
                        'target': devices[i + 1]['id'],
                        'type': 'ethernet',
                        'bandwidth': '1Gbps',
                        'status': 'active'
                    }
                    topology_data['edges'].append(edge)
                
                # Add some additional connections for a more realistic topology
                if len(devices) > 2:
                    edge = {
                        'source': devices[0]['id'],
                        'target': devices[-1]['id'],
                        'type': 'ethernet',
                        'bandwidth': '1Gbps',
                        'status': 'active'
                    }
                    topology_data['edges'].append(edge)
            
            # Calculate metrics
            topology_data['metrics'] = {
                'total_nodes': len(topology_data['nodes']),
                'total_edges': len(topology_data['edges']),
                'network_diameter': len(devices),  # Simplified
                'average_degree': len(topology_data['edges']) * 2 / len(topology_data['nodes']) if topology_data['nodes'] else 0
            }
            
            return topology_data
            
        except Exception as e:
            logger.error(f"❌ Error generating topology data: {e}")
            return {'nodes': [], 'edges': [], 'metrics': {}}
    
    def _render_network_visualization(self, topology_data, layout_type, show_labels, show_connections):
        """Render network topology visualization using Plotly"""
        try:
            if not topology_data['nodes']:
                st.info("No topology data available")
                return
            
            # Create network graph
            fig = go.Figure()
            
            # Add edges (connections) first so they appear behind nodes
            if show_connections and topology_data['edges']:
                edge_x = []
                edge_y = []
                
                for edge in topology_data['edges']:
                    source_node = next((n for n in topology_data['nodes'] if n['id'] == edge['source']), None)
                    target_node = next((n for n in topology_data['nodes'] if n['id'] == edge['target']), None)
                    
                    if source_node and target_node:
                        edge_x.extend([source_node['x'], target_node['x'], None])
                        edge_y.extend([source_node['y'], target_node['y'], None])
                
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=2, color='gray'),
                    hoverinfo='none',
                    showlegend=False,
                    name='Connections'
                ))
            
            # Add nodes
            node_x = [node['x'] for node in topology_data['nodes']]
            node_y = [node['y'] for node in topology_data['nodes']]
            node_text = [node['label'] if show_labels else '' for node in topology_data['nodes']]
            node_colors = []
            node_symbols = []
            
            for node in topology_data['nodes']:
                # Color by status
                status = node.get('status', 'unknown')
                if status == 'online':
                    node_colors.append('green')
                elif status == 'offline':
                    node_colors.append('red')
                elif status == 'warning':
                    node_colors.append('orange')
                else:
                    node_colors.append('gray')
                
                # Symbol by device type
                device_type = node.get('type', 'unknown')
                if device_type in ['router', 'cisco_ios']:
                    node_symbols.append('square')
                elif device_type in ['switch']:
                    node_symbols.append('diamond')
                elif device_type in ['firewall']:
                    node_symbols.append('triangle-up')
                else:
                    node_symbols.append('circle')
            
            # Create hover text
            hover_text = []
            for node in topology_data['nodes']:
                hover_text.append(
                    f"<b>{node['label']}</b><br>" +
                    f"Type: {node.get('type', 'Unknown')}<br>" +
                    f"IP: {node.get('ip', 'Unknown')}<br>" +
                    f"Status: {node.get('status', 'Unknown')}"
                )
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=node_colors,
                    symbol=node_symbols,
                    line=dict(width=2, color='white')
                ),
                text=node_text,
                textposition="bottom center",
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text,
                showlegend=False,
                name='Devices'
            ))
            
            # Update layout
            fig.update_layout(
                title=f"Network Topology - {layout_type} Layout",
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Click and drag to pan, scroll to zoom",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"❌ Error rendering network visualization: {e}")
            st.error("Error rendering network visualization")
    
    def _render_connection_summary(self, topology_data):
        """Render connection summary statistics"""
        try:
            metrics = topology_data.get('metrics', {})
            
            st.metric("Total Devices", metrics.get('total_nodes', 0))
            st.metric("Total Connections", metrics.get('total_edges', 0))
            st.metric("Network Diameter", metrics.get('network_diameter', 0))
            st.metric("Avg Connections", f"{metrics.get('average_degree', 0):.1f}")
            
            # Connection types breakdown
            if topology_data['edges']:
                connection_types = {}
                for edge in topology_data['edges']:
                    conn_type = edge.get('type', 'unknown')
                    connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
                
                st.markdown("**Connection Types:**")
                for conn_type, count in connection_types.items():
                    st.write(f"• {conn_type.title()}: {count}")
            
        except Exception as e:
            st.info("Connection summary not available")
    
    def _start_network_discovery(self, device_manager, method, network_range, seed_device, 
                                include_offline, auto_add, deep_scan):
        """Start network discovery process"""
        try:
            # Set discovery state
            st.session_state.discovery_running = True
            st.session_state.discovery_progress = 0
            st.session_state.discovered_devices = []
            
            with show_loading_spinner(f"Starting {method}..."):
                # Simulate discovery process
                if method == "Ping Sweep" and network_range:
                    discovered = self._simulate_ping_sweep(network_range, include_offline)
                elif method == "SNMP Discovery" and seed_device:
                    discovered = self._simulate_snmp_discovery(seed_device, deep_scan)
                else:
                    discovered = self._simulate_general_discovery(method)
                
                st.session_state.discovered_devices = discovered
                st.session_state.discovery_running = False
                st.session_state.discovery_progress = 100
            
            if discovered:
                st.success(f"✅ Discovery completed! Found {len(discovered)} devices")
                
                if auto_add:
                    self._auto_add_discovered_devices(device_manager, discovered)
            else:
                st.info("No new devices discovered")
                
        except Exception as e:
            logger.error(f"❌ Error in network discovery: {e}")
            st.error(f"Error in network discovery: {e}")
            st.session_state.discovery_running = False
    
    def _simulate_ping_sweep(self, network_range, include_offline):
        """Simulate ping sweep discovery"""
        # Generate sample discovered devices
        discovered = []
        
        base_ip = network_range.split('/')[0].rsplit('.', 1)[0]
        
        for i in range(2, 10):  # Simulate finding devices at .2 to .9
            device = {
                'hostname': f'discovered-device-{i}',
                'ip_address': f'{base_ip}.{i}',
                'device_type': np.random.choice(['router', 'switch', 'server']),
                'status': 'online' if include_offline or np.random.random() > 0.2 else 'offline',
                'discovery_method': 'ping_sweep',
                'discovered_at': datetime.now()
            }
            discovered.append(device)
        
        return discovered
    
    def _simulate_snmp_discovery(self, seed_device, deep_scan):
        """Simulate SNMP-based discovery"""
        discovered = []
        
        # Simulate finding connected devices via SNMP
        device_count = 5 if deep_scan else 3
        
        for i in range(1, device_count + 1):
            device = {
                'hostname': f'snmp-discovered-{i}',
                'ip_address': f'192.168.1.{100 + i}',
                'device_type': np.random.choice(['cisco_ios', 'cisco_nxos']),
                'status': 'online',
                'discovery_method': 'snmp',
                'snmp_info': {
                    'sysName': f'Device-{i}',
                    'sysDescr': 'Cisco Router',
                    'sysUpTime': f'{np.random.randint(1, 365)} days'
                },
                'discovered_at': datetime.now()
            }
            discovered.append(device)
        
        return discovered
    
    def _simulate_general_discovery(self, method):
        """Simulate other discovery methods"""
        discovered = []
        
        for i in range(1, 4):
            device = {
                'hostname': f'{method.lower().replace(" ", "-")}-device-{i}',
                'ip_address': f'10.0.1.{10 + i}',
                'device_type': 'unknown',
                'status': 'unknown',
                'discovery_method': method.lower().replace(' ', '_'),
                'discovered_at': datetime.now()
            }
            discovered.append(device)
        
        return discovered
    
    def _render_discovery_progress(self):
        """Render discovery progress indicator"""
        progress = st.session_state.get('discovery_progress', 0)
        st.progress(progress / 100)
        st.caption(f"Discovery progress: {progress}%")
    
    def _render_discovery_history(self, device_manager):
        """Render discovery history"""
        # Sample discovery history
        history = [
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'method': 'SNMP Discovery',
                'devices_found': 5,
                'devices_added': 3,
                'duration': '2 minutes'
            },
            {
                'timestamp': (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M'),
                'method': 'Ping Sweep',
                'devices_found': 8,
                'devices_added': 2,
                'duration': '5 minutes'
            }
        ]
        
        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No discovery history available")
    
    def _render_discovered_devices(self, device_manager):
        """Render list of discovered devices"""
        discovered = st.session_state.get('discovered_devices', [])
        
        if discovered:
            for device in discovered:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{device['hostname']}** ({device['ip_address']})")
                    st.caption(f"Type: {device['device_type']} | Method: {device['discovery_method']}")
                
                with col2:
                    status_color = {
                        'online': '🟢',
                        'offline': '🔴',
                        'unknown': '⚪'
                    }.get(device['status'], '⚪')
                    st.write(f"{status_color} {device['status'].title()}")
                
                with col3:
                    if st.button("➕ Add", key=f"add_discovered_{device['hostname']}"):
                        try:
                            device_manager.add_device(device)
                            st.success(f"✅ {device['hostname']} added to inventory")
                            # Remove from discovered list
                            st.session_state.discovered_devices.remove(device)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error adding device: {e}")
        else:
            st.info("No devices discovered yet")
    
    def _auto_add_discovered_devices(self, device_manager, discovered_devices):
        """Automatically add discovered devices to inventory"""
        added_count = 0
        
        for device in discovered_devices:
            try:
                device_manager.add_device(device)
                added_count += 1
            except Exception as e:
                logger.error(f"❌ Error auto-adding device {device['hostname']}: {e}")
        
        if added_count > 0:
            st.success(f"✅ Automatically added {added_count} devices to inventory")
            notification_manager.add_notification(
                f"Auto-added {added_count} discovered devices",
                "success"
            )
    
    def _run_topology_analysis(self, devices, analysis_type):
        """Run topology analysis"""
        try:
            with show_loading_spinner(f"Running {analysis_type}..."):
                # Simulate analysis
                if analysis_type == "Network Centrality":
                    results = self._analyze_network_centrality(devices)
                elif analysis_type == "Path Analysis":
                    results = self._analyze_network_paths(devices)
                elif analysis_type == "Redundancy Analysis":
                    results = self._analyze_network_redundancy(devices)
                elif analysis_type == "Bottleneck Detection":
                    results = self._analyze_network_bottlenecks(devices)
                else:
                    results = {"error": "Unknown analysis type"}
                
                st.session_state.analysis_results = results
            
            st.success(f"✅ {analysis_type} completed")
            
        except Exception as e:
            logger.error(f"❌ Error running topology analysis: {e}")
            st.error(f"Error running {analysis_type}")
    
    def _analyze_network_centrality(self, devices):
        """Analyze network centrality metrics"""
        return {
            'type': 'centrality',
            'most_central': devices[0]['hostname'] if devices else 'None',
            'centrality_scores': {device['hostname']: np.random.uniform(0.1, 1.0) for device in devices[:5]},
            'summary': 'Analysis shows Router-01 as the most central device in the network'
        }
    
    def _analyze_network_paths(self, devices):
        """Analyze network path redundancy"""
        return {
            'type': 'paths',
            'redundant_paths': len(devices) // 2,
            'single_points_of_failure': max(0, len(devices) - 3),
            'average_path_length': np.random.uniform(2.0, 4.0),
            'summary': 'Network has good path redundancy with few single points of failure'
        }
    
    def _analyze_network_redundancy(self, devices):
        """Analyze network redundancy"""
        return {
            'type': 'redundancy',
            'redundancy_score': np.random.uniform(0.6, 0.9),
            'critical_devices': [d['hostname'] for d in devices[:2]],
            'recommendations': ['Add backup link between Switch-01 and Router-02', 'Consider secondary uplink'],
            'summary': 'Network redundancy is good but can be improved with additional links'
        }
    
    def _analyze_network_bottlenecks(self, devices):
        """Analyze potential network bottlenecks"""
        return {
            'type': 'bottlenecks',
            'potential_bottlenecks': [devices[0]['hostname']] if devices else [],
            'congestion_points': ['Link between Router-01 and Switch-01'],
            'utilization_metrics': {device['hostname']: np.random.uniform(0.3, 0.8) for device in devices[:3]},
            'summary': 'Router-01 may become a bottleneck under high traffic conditions'
        }
    
    def _render_analysis_results(self, results, analysis_type):
        """Render topology analysis results"""
        try:
            st.markdown(f"### 📊 {analysis_type} Results")
            
            if results.get('summary'):
                st.info(results['summary'])
            
            if analysis_type == "Network Centrality":
                if results.get('centrality_scores'):
                    df = pd.DataFrame(list(results['centrality_scores'].items()), 
                                    columns=['Device', 'Centrality Score'])
                    st.bar_chart(df.set_index('Device'))
            
            elif analysis_type == "Path Analysis":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Redundant Paths", results.get('redundant_paths', 0))
                with col2:
                    st.metric("Single Points of Failure", results.get('single_points_of_failure', 0))
                with col3:
                    st.metric("Avg Path Length", f"{results.get('average_path_length', 0):.1f}")
            
            elif analysis_type == "Redundancy Analysis":
                st.metric("Redundancy Score", f"{results.get('redundancy_score', 0):.1%}")
                
                if results.get('critical_devices'):
                    st.markdown("**Critical Devices:**")
                    for device in results['critical_devices']:
                        st.write(f"• {device}")
                
                if results.get('recommendations'):
                    st.markdown("**Recommendations:**")
                    for rec in results['recommendations']:
                        st.write(f"• {rec}")
            
            elif analysis_type == "Bottleneck Detection":
                if results.get('utilization_metrics'):
                    df = pd.DataFrame(list(results['utilization_metrics'].items()),
                                    columns=['Device', 'Utilization'])
                    st.bar_chart(df.set_index('Device'))
                
                if results.get('congestion_points'):
                    st.markdown("**Potential Congestion Points:**")
                    for point in results['congestion_points']:
                        st.write(f"⚠️ {point}")
            
        except Exception as e:
            logger.error(f"❌ Error rendering analysis results: {e}")
            st.error("Error displaying analysis results")
    
    def _render_network_metrics(self, devices):
        """Render network topology metrics"""
        try:
            # Calculate basic metrics
            total_devices = len(devices)
            device_types = {}
            
            for device in devices:
                device_type = device.get('device_type', 'unknown')
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            # Display metrics
            st.metric("Total Devices", total_devices)
            st.metric("Device Types", len(device_types))
            st.metric("Network Density", f"{np.random.uniform(0.3, 0.8):.1%}")
            st.metric("Connectivity Index", f"{np.random.uniform(0.7, 0.95):.1%}")
            
            # Device type breakdown
            if device_types:
                st.markdown("**Device Types:**")
                for device_type, count in device_types.items():
                    st.write(f"• {device_type.title()}: {count}")
            
        except Exception as e:
            st.info("Network metrics not available")
    
    def _render_optimization_suggestions(self, devices):
        """Render network optimization suggestions"""
        suggestions = [
            "🔗 Consider adding redundant links between core routers",
            "⚡ Upgrade bandwidth on high-utilization links",
            "🛡️ Implement network segmentation for better security",
            "📊 Add monitoring to critical network paths",
            "🔄 Consider load balancing for improved performance"
        ]
        
        for suggestion in suggestions[:3]:  # Show top 3
            st.write(suggestion)
    
    def _render_path_analysis(self, devices):
        """Render network path analysis"""
        if len(devices) < 2:
            st.info("Need at least 2 devices for path analysis")
            return
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            source_device = device_selector(devices, key="path_source", label="Source:")
        
        with col2:
            target_device = device_selector(devices, key="path_target", label="Target:")
        
        with col3:
            if st.button("🛤️ Find Path"):
                if source_device and target_device and source_device['id'] != target_device['id']:
                    self._show_path_analysis(source_device, target_device)
                else:
                    st.warning("Please select two different devices")
    
    def _show_path_analysis(self, source, target):
        """Show path analysis between two devices"""
        st.markdown(f"### 🛤️ Path: {source['hostname']} → {target['hostname']}")
        
        # Simulate path finding
        sample_path = [
            source['hostname'],
            "Core-Switch-01",
            "Distribution-Router-01", 
            target['hostname']
        ]
        
        st.write("**Optimal Path:**")
        for i, hop in enumerate(sample_path):
            if i == 0:
                st.write(f"🎯 {hop} (Source)")
            elif i == len(sample_path) - 1:
                st.write(f"🏁 {hop} (Target)")
            else:
                st.write(f"↳ {hop}")
        
        # Path metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hop Count", len(sample_path) - 1)
        with col2:
            st.metric("Estimated Latency", f"{np.random.uniform(5, 25):.1f} ms")
        with col3:
            st.metric("Path Reliability", f"{np.random.uniform(0.95, 0.99):.1%}")
    
    def _stop_network_discovery(self):
        """Stop ongoing network discovery"""
        st.session_state.discovery_running = False
        st.warning("⏹️ Discovery stopped")
    
    def _show_discovery_report(self):
        """Show network discovery report"""
        st.info("🚧 Discovery reporting feature coming soon...")
        
        # Placeholder for discovery report
        st.markdown("### 🔜 Coming Soon:")
        st.markdown("""
        - **Discovery Summary**: Comprehensive discovery statistics
        - **Device Inventory**: Detailed device information
        - **Network Map**: Auto-generated topology map
        - **Export Options**: Multiple report formats
        """)
    
    def _export_topology_analysis(self):
        """Export topology analysis results"""
        try:
            results = st.session_state.get('analysis_results', {})
            
            if results:
                import json
                analysis_json = json.dumps(results, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download Analysis",
                    data=analysis_json,
                    file_name=f"topology_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No analysis results available for export")
                
        except Exception as e:
            logger.error(f"❌ Error exporting analysis: {e}")
            st.error("Error exporting topology analysis")
    
    def _save_topology_configuration(self, config):
        """Save topology configuration settings"""
        try:
            st.session_state.topology_config = config
            st.success("✅ Topology configuration saved successfully")
            
            notification_manager.add_notification(
                "Topology configuration updated",
                "success"
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving topology configuration: {e}")
            st.error("Error saving topology configuration")


def render_topology_page():
    """Main function to render topology page"""
    topology_page = TopologyPage()
    topology_page.render()
