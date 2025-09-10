"""
Network Topology Manager - Interactive topology visualization for network monitoring dashboard

This module provides comprehensive network topology visualization with real-time device status,
connection mapping, and interactive network diagrams using lab devices.
"""

import logging
import json
import sqlite3
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopologyManager:
    """
    Manages network topology visualization and device relationships
    
    Features:
    - Interactive network diagrams
    - Real-time device status integration
    - Connection discovery and mapping
    - Lab device topology visualization
    - Network path analysis
    """
    
    def __init__(self, device_manager=None, ssh_manager=None):
        """Initialize topology manager"""
        self.device_manager = device_manager
        self.ssh_manager = ssh_manager
        self.graph = nx.Graph()
        self.device_positions = {}
        self.connection_cache = {}
        self.config_cache = {}  # Cache for device configurations
        logger.info("🗺️ Topology Manager initialized")
    
    def discover_lab_topology(self) -> Dict[str, Any]:
        """
        Discover topology from lab devices with real-time status checking
        
        Returns:
            Dict: Discovered topology structure
        """
        try:
            logger.info("🔍 Discovering lab topology with connectivity testing...")
            
            # Get lab devices
            lab_devices = self._get_lab_devices()
            
            # Build topology from lab devices
            topology = {
                'nodes': [],
                'edges': [],
                'metadata': {
                    'discovery_time': datetime.now().isoformat(),
                    'total_devices': len(lab_devices),
                    'lab_environment': True
                }
            }
            
            # Add nodes for each device with real-time status checking
            for device in lab_devices:
                # Test connectivity to get real status
                real_status = self._test_device_connectivity(device)
                
                node = {
                    'id': device['hostname'],
                    'label': device['hostname'],
                    'type': self._determine_device_type(device['hostname']),
                    'status': real_status,
                    'ip': device.get('ip_address', '').split(':')[0],
                    'port': device.get('ip_address', '').split(':')[1] if ':' in device.get('ip_address', '') else '22',
                    'group': self._get_device_group(device['hostname']),
                    'last_checked': datetime.now().isoformat()
                }
                topology['nodes'].append(node)
                
            # Add logical connections based on typical network patterns
            connections = self._infer_lab_connections(lab_devices)
            for connection in connections:
                # Test connection health based on both endpoints
                from_status = next((n['status'] for n in topology['nodes'] if n['id'] == connection['from']), 'unknown')
                to_status = next((n['status'] for n in topology['nodes'] if n['id'] == connection['to']), 'unknown')
                
                edge = {
                    'from': connection['from'],
                    'to': connection['to'],
                    'type': connection['type'],
                    'status': 'active' if from_status == 'active' and to_status == 'active' else 'inactive',
                    'bandwidth': connection.get('bandwidth', '1Gbps')
                }
                topology['edges'].append(edge)
            
            active_count = len([n for n in topology['nodes'] if n['status'] == 'active'])
            logger.info(f"✅ Topology discovered: {len(topology['nodes'])} nodes ({active_count} active), {len(topology['edges'])} connections")
            return topology
            
        except Exception as e:
            logger.error(f"❌ Error discovering topology: {e}")
            return {'nodes': [], 'edges': [], 'metadata': {'error': str(e)}}
    
    def _get_lab_devices(self) -> List[Dict]:
        """Get lab devices from device manager"""
        if not self.device_manager:
            # Fallback: return known lab devices
            return [
                {'hostname': 'lab-router1', 'ip_address': '127.0.0.1:2221', 'status': 'unknown'},
                {'hostname': 'lab-switch1', 'ip_address': '127.0.0.1:2222', 'status': 'unknown'},
                {'hostname': 'lab-firewall1', 'ip_address': '127.0.0.1:2223', 'status': 'unknown'}
            ]
        
        # Get devices from device manager
        try:
            devices = self.device_manager.get_all_devices()
            # Filter for lab devices
            lab_devices = [d for d in devices if d.get('hostname', '').startswith('lab-')]
            return lab_devices
        except Exception as e:
            logger.warning(f"⚠️ Could not get devices from manager: {e}")
            return []
    
    def _test_device_connectivity(self, device: Dict) -> str:
        """
        Test connectivity to a device using SSH
        
        Args:
            device: Device information dictionary
            
        Returns:
            str: 'active' if reachable, 'inactive' if not
        """
        try:
            import socket
            import paramiko
            from contextlib import closing
            
            # Parse IP and port
            ip_address = device.get('ip_address', '')
            if ':' in ip_address:
                host, port = ip_address.split(':')
                port = int(port)
            else:
                host = ip_address
                port = 22
            
            # Quick socket test first
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                if result != 0:
                    logger.debug(f"🔴 {device['hostname']}: Socket connection failed")
                    return 'inactive'
            
            # Try SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                ssh.connect(
                    hostname=host,
                    port=port,
                    username='admin',
                    password='admin',
                    timeout=5,
                    auth_timeout=5
                )
                ssh.close()
                logger.debug(f"🟢 {device['hostname']}: SSH connection successful")
                return 'active'
                
            except paramiko.AuthenticationException:
                # Authentication failed but SSH is responding
                logger.debug(f"🟡 {device['hostname']}: SSH responding but auth failed")
                return 'active'
            except Exception as ssh_e:
                logger.debug(f"🔴 {device['hostname']}: SSH connection failed: {ssh_e}")
                return 'inactive'
                
        except Exception as e:
            logger.debug(f"🔴 Device connectivity test failed: {e}")
            return 'inactive'
    
    def test_device_connectivity_detailed(self, hostname: str, host: str, port: int) -> Dict[str, Any]:
        """
        Test connectivity to a device using separate parameters (for streamlit compatibility)
        
        Args:
            hostname: Device hostname
            host: IP address or hostname
            port: SSH port number
            
        Returns:
            Dict: {'status': 'success'/'failed', 'message': 'description'}
        """
        try:
            import socket
            import paramiko
            from contextlib import closing
            
            # Quick socket test first
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                if result != 0:
                    logger.debug(f"🔴 {hostname}: Socket connection failed")
                    return {'status': 'failed', 'message': 'Port not reachable'}
            
            # Try SSH connection
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                ssh.connect(
                    hostname=host,
                    port=port,
                    username='admin',
                    password='admin',
                    timeout=5,
                    auth_timeout=5
                )
                ssh.close()
                logger.debug(f"🟢 {hostname}: SSH connection successful")
                return {'status': 'success', 'message': 'SSH connection successful'}
                
            except paramiko.AuthenticationException:
                # Authentication failed but SSH is responding
                logger.debug(f"🟡 {hostname}: SSH responding but auth failed")
                return {'status': 'success', 'message': 'SSH responding (auth failed is expected)'}
            except Exception as ssh_e:
                logger.debug(f"🔴 {hostname}: SSH connection failed: {ssh_e}")
                return {'status': 'failed', 'message': f'SSH failed: {ssh_e}'}
                
        except Exception as e:
            logger.debug(f"🔴 {hostname}: Connectivity test failed: {e}")
            return {'status': 'failed', 'message': f'Connection failed: {e}'}
    
    def get_device_configuration(self, device_id: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get configuration from a device with caching
        
        Args:
            device_id: Device identifier (hostname)
            use_cache: Whether to use cached configuration
            
        Returns:
            Dict: Configuration data with status and content
        """
        try:
            # Check cache first (if enabled and not expired)
            cache_key = f"config_{device_id}"
            if use_cache and cache_key in self.config_cache:
                cached_data = self.config_cache[cache_key]
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if (datetime.now() - cache_time).seconds < 60:  # 60-second cache
                    logger.debug(f"📋 Using cached config for {device_id}")
                    return cached_data
            
            # Get device info
            device_info = self._get_device_info(device_id)
            if not device_info:
                return {
                    'status': 'error',
                    'message': f'Device {device_id} not found',
                    'device_id': device_id
                }
            
            # Get configuration using SSH manager
            if not self.ssh_manager:
                return {
                    'status': 'error',
                    'message': 'SSH manager not available',
                    'device_id': device_id
                }
            
            # Parse connection details
            ip_address = device_info.get('ip_address', '')
            if ':' in ip_address:
                host, port = ip_address.split(':')
                port = int(port)
            else:
                host = ip_address
                port = 22
            
            logger.info(f"📋 Getting configuration from {device_id} ({host}:{port})")
            
            # Get configuration via SSH
            result = self.ssh_manager.get_device_configuration(
                host=host,
                port=port,
                username='admin',
                password='admin'
            )
            
            if result.get('status') == 'success':
                config_data = {
                    'status': 'success',
                    'device_id': device_id,
                    'device_name': device_info.get('hostname', device_id),
                    'device_type': self._determine_device_type(device_id),
                    'ip_address': ip_address,
                    'config_content': result.get('config', ''),
                    'timestamp': datetime.now().isoformat(),
                    'lines_count': len(result.get('config', '').splitlines()),
                    'size_bytes': len(result.get('config', '').encode('utf-8'))
                }
                
                # Cache the result
                self.config_cache[cache_key] = config_data
                
                logger.info(f"✅ Configuration retrieved from {device_id}")
                return config_data
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Failed to get configuration'),
                    'device_id': device_id,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting configuration from {device_id}: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'device_id': device_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_device_info(self, device_id: str) -> Optional[Dict]:
        """Get device information by ID"""
        lab_devices = self._get_lab_devices()
        for device in lab_devices:
            if device.get('hostname') == device_id:
                return device
        return None
    
    def clear_config_cache(self):
        """Clear the configuration cache"""
        self.config_cache.clear()
        logger.info("🗑️ Configuration cache cleared")
    
    def _determine_device_type(self, hostname: str) -> str:
        """Determine device type from hostname"""
        if 'router' in hostname.lower():
            return 'router'
        elif 'switch' in hostname.lower():
            return 'switch'
        elif 'firewall' in hostname.lower():
            return 'firewall'
        elif 'server' in hostname.lower():
            return 'server'
        elif 'access' in hostname.lower() or 'ap' in hostname.lower():
            return 'access_point'
        else:
            return 'device'
    
    def _get_device_group(self, hostname: str) -> str:
        """Get device group for layout positioning"""
        if 'router' in hostname.lower():
            return 'core'
        elif 'switch' in hostname.lower():
            return 'distribution'
        elif 'firewall' in hostname.lower():
            return 'security'
        elif 'server' in hostname.lower():
            return 'servers'
        else:
            return 'access'
    
    def _infer_lab_connections(self, devices: List[Dict]) -> List[Dict]:
        """
        Infer logical connections between lab devices
        Based on typical network topology patterns
        """
        connections = []
        device_names = [d['hostname'] for d in devices]
        
        # Standard network topology: Router -> Switch -> Firewall
        if 'lab-router1' in device_names and 'lab-switch1' in device_names:
            connections.append({
                'from': 'lab-router1',
                'to': 'lab-switch1',
                'type': 'ethernet',
                'bandwidth': '1Gbps'
            })
        
        if 'lab-switch1' in device_names and 'lab-firewall1' in device_names:
            connections.append({
                'from': 'lab-switch1',
                'to': 'lab-firewall1',
                'type': 'ethernet',
                'bandwidth': '1Gbps'
            })
        
        # Add more connections if we have more devices
        for i, device in enumerate(devices):
            for j, other_device in enumerate(devices):
                if i >= j:  # Avoid duplicates and self-connections
                    continue
                
                # Add connection based on device types
                if self._should_connect(device['hostname'], other_device['hostname']):
                    connections.append({
                        'from': device['hostname'],
                        'to': other_device['hostname'],
                        'type': 'ethernet',
                        'bandwidth': '1Gbps'
                    })
        
        return connections
    
    def _should_connect(self, device1: str, device2: str) -> bool:
        """Determine if two devices should be connected"""
        # Already connected devices
        connected_pairs = [
            ('lab-router1', 'lab-switch1'),
            ('lab-switch1', 'lab-firewall1')
        ]
        
        # Check if already connected
        for pair in connected_pairs:
            if (device1 in pair and device2 in pair):
                return False
        
        # Add additional logic for new devices
        return False
    
    def create_interactive_diagram(self, topology_data: Dict) -> go.Figure:
        """
        Create interactive network topology diagram using Plotly
        
        Args:
            topology_data: Topology structure with nodes and edges
            
        Returns:
            go.Figure: Interactive Plotly figure
        """
        try:
            # Create NetworkX graph for layout calculation
            G = nx.Graph()
            
            # Add nodes
            for node in topology_data.get('nodes', []):
                G.add_node(node['id'], **node)
            
            # Add edges
            for edge in topology_data.get('edges', []):
                G.add_edge(edge['from'], edge['to'], **edge)
            
            # Calculate layout positions
            if len(G.nodes()) == 0:
                logger.warning("⚠️ No nodes to display")
                return self._create_empty_diagram()
            
            # Use spring layout for automatic positioning
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Prepare traces
            edge_traces = self._create_edge_traces(topology_data['edges'], pos)
            node_trace = self._create_node_trace(topology_data['nodes'], pos)
            
            # Create figure
            fig = go.Figure(data=edge_traces + [node_trace])
            
            # Update layout
            fig.update_layout(
                title={
                    'text': "🌐 Network Topology Map",
                    'x': 0.5,
                    'font': {'size': 20}
                },
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="Interactive Network Topology - Click and drag nodes",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="#666", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(0,0,0,0)',
                height=600
            )
            
            logger.info("✅ Interactive diagram created successfully")
            return fig
            
        except Exception as e:
            logger.error(f"❌ Error creating diagram: {e}")
            return self._create_empty_diagram()
    
    def _create_edge_traces(self, edges: List[Dict], pos: Dict) -> List[go.Scatter]:
        """Create edge traces for the network diagram"""
        edge_traces = []
        
        for edge in edges:
            x0, y0 = pos.get(edge['from'], (0, 0))
            x1, y1 = pos.get(edge['to'], (0, 0))
            
            # Determine edge color based on status
            edge_color = '#2E8B57' if edge.get('status') == 'active' else '#CD5C5C'
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=2, color=edge_color),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        return edge_traces
    
    def _create_node_trace(self, nodes: List[Dict], pos: Dict) -> go.Scatter:
        """Create node trace for the network diagram"""
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        node_symbols = []
        node_sizes = []
        
        # Color and symbol mapping for device types
        device_styles = {
            'router': {'color': '#FF6B6B', 'symbol': 'square', 'size': 30},
            'switch': {'color': '#4ECDC4', 'symbol': 'diamond', 'size': 25},
            'firewall': {'color': '#FFD93D', 'symbol': 'triangle-up', 'size': 25},
            'server': {'color': '#A8E6CF', 'symbol': 'circle', 'size': 20},
            'device': {'color': '#C7CEEA', 'symbol': 'circle', 'size': 15}
        }
        
        for node in nodes:
            x, y = pos.get(node['id'], (0, 0))
            node_x.append(x)
            node_y.append(y)
            
            # Node styling
            device_type = node.get('type', 'device')
            style = device_styles.get(device_type, device_styles['device'])
            
            node_colors.append(style['color'])
            node_symbols.append(style['symbol'])
            node_sizes.append(style['size'])
            
            # Node text and hover info
            status_emoji = "🟢" if node.get('status') == 'active' else "🔴"
            node_text.append(f"{status_emoji} {node['label']}")
            
            hover_info = (
                f"<b>{node['label']}</b><br>"
                f"Type: {device_type.title()}<br>"
                f"Status: {node.get('status', 'unknown').title()}<br>"
                f"IP: {node.get('ip', 'N/A')}<br>"
                f"Port: {node.get('port', 'N/A')}"
            )
            node_info.append(hover_info)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color="white"),
            marker=dict(
                size=node_sizes,
                color=node_colors,
                symbol=node_symbols,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        return node_trace
    
    def _create_empty_diagram(self) -> go.Figure:
        """Create empty diagram when no data available"""
        fig = go.Figure()
        fig.add_annotation(
            text="🚧 No topology data available<br>Start your lab devices to see the network map",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="#666")
        )
        fig.update_layout(
            title="🌐 Network Topology Map",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400
        )
        return fig
    
    def get_topology_stats(self, topology_data: Dict) -> Dict[str, Any]:
        """
        Calculate topology statistics
        
        Args:
            topology_data: Topology structure
            
        Returns:
            Dict: Topology statistics
        """
        nodes = topology_data.get('nodes', [])
        edges = topology_data.get('edges', [])
        
        # Device type counts
        device_types = {}
        active_devices = 0
        
        for node in nodes:
            device_type = node.get('type', 'unknown')
            device_types[device_type] = device_types.get(device_type, 0) + 1
            
            if node.get('status') == 'active':
                active_devices += 1
        
        # Connection stats
        active_connections = len([e for e in edges if e.get('status') == 'active'])
        
        # Network diameter (for small networks, approximate)
        diameter = min(len(nodes), 4) if nodes else 0
        
        stats = {
            'total_nodes': len(nodes),
            'total_connections': len(edges),
            'active_devices': active_devices,
            'active_connections': active_connections,
            'network_diameter': diameter,
            'device_types': device_types,
            'health_percentage': round((active_devices / len(nodes) * 100) if nodes else 0, 1)
        }
        
        return stats
    
    def create_topology_summary(self, topology_data: Dict) -> Dict[str, Any]:
        """
        Create comprehensive topology summary
        
        Args:
            topology_data: Topology structure
            
        Returns:
            Dict: Topology summary with devices and connections
        """
        summary = {
            'devices': [],
            'connections': [],
            'summary': self.get_topology_stats(topology_data)
        }
        
        # Device details
        for node in topology_data.get('nodes', []):
            device_info = {
                'name': node['label'],
                'type': node.get('type', 'unknown').title(),
                'status': node.get('status', 'unknown').title(),
                'ip_address': node.get('ip', 'N/A'),
                'port': node.get('port', 'N/A'),
                'group': node.get('group', 'unknown').title()
            }
            summary['devices'].append(device_info)
        
        # Connection details
        for edge in topology_data.get('edges', []):
            connection_info = {
                'from': edge['from'],
                'to': edge['to'],
                'type': edge.get('type', 'unknown').title(),
                'status': edge.get('status', 'unknown').title(),
                'bandwidth': edge.get('bandwidth', 'N/A')
            }
            summary['connections'].append(connection_info)
        
        return summary
