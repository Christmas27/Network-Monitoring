#!/usr/bin/env python3
"""
Data Processing Utilities for Network Monitoring Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
import re

logger = logging.getLogger(__name__)

class DataProcessor:
    """Data processing utilities for dashboard components"""
    
    @staticmethod
    def clean_device_data(devices: List[Dict]) -> pd.DataFrame:
        """Clean and standardize device data"""
        if not devices:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(devices)
            
            # Standardize column names
            column_mapping = {
                'id': 'device_id',
                'hostname': 'hostname',
                'ip_address': 'ip_address',
                'device_type': 'device_type',
                'status': 'status',
                'last_seen': 'last_seen',
                'updated_at': 'updated_at'
            }
            
            # Rename columns if they exist
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and old_name != new_name:
                    df = df.rename(columns={old_name: new_name})
            
            # Ensure required columns exist
            required_columns = ['hostname', 'ip_address', 'device_type', 'status']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 'Unknown'
            
            # Clean IP addresses
            df['ip_address'] = df['ip_address'].apply(DataProcessor.clean_ip_address)
            
            # Standardize device types
            df['device_type'] = df['device_type'].apply(DataProcessor.standardize_device_type)
            
            # Standardize status
            df['status'] = df['status'].apply(DataProcessor.standardize_status)
            
            # Convert timestamps
            timestamp_columns = ['last_seen', 'updated_at', 'created_at']
            for col in timestamp_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error cleaning device data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def clean_ip_address(ip_str: str) -> str:
        """Clean and validate IP address"""
        if not ip_str or pd.isna(ip_str):
            return "Unknown"
        
        # Remove whitespace
        ip_str = str(ip_str).strip()
        
        # Handle localhost variants
        if ip_str in ['localhost', '127.0.0.1', '::1']:
            return '127.0.0.1'
        
        # Extract IP from IP:PORT format
        if ':' in ip_str and not ip_str.startswith('['):
            ip_part = ip_str.split(':')[0]
        else:
            ip_part = ip_str
        
        # Basic IP validation
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if ip_pattern.match(ip_part):
            return ip_part
        
        return ip_str
    
    @staticmethod
    def standardize_device_type(device_type: str) -> str:
        """Standardize device type values"""
        if not device_type or pd.isna(device_type):
            return "unknown"
        
        device_type = str(device_type).lower().strip()
        
        # Device type mapping
        type_mapping = {
            'router': 'router',
            'switch': 'switch',
            'firewall': 'firewall',
            'server': 'server',
            'access_point': 'access_point',
            'ap': 'access_point',
            'wireless': 'access_point',
            'linux': 'server',
            'windows': 'server',
            'cisco': 'router',
            'juniper': 'router',
            'arista': 'switch',
            'palo alto': 'firewall',
            'fortinet': 'firewall'
        }
        
        return type_mapping.get(device_type, 'unknown')
    
    @staticmethod
    def standardize_status(status: str) -> str:
        """Standardize status values"""
        if not status or pd.isna(status):
            return "unknown"
        
        status = str(status).lower().strip()
        
        # Status mapping
        status_mapping = {
            'up': 'online',
            'down': 'offline',
            'online': 'online',
            'offline': 'offline',
            'active': 'online',
            'inactive': 'offline',
            'reachable': 'online',
            'unreachable': 'offline',
            'maintenance': 'maintenance',
            'maint': 'maintenance'
        }
        
        return status_mapping.get(status, 'unknown')
    
    @staticmethod
    def process_monitoring_data(metrics: List[Dict]) -> pd.DataFrame:
        """Process monitoring metrics data"""
        if not metrics:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(metrics)
            
            # Convert timestamp columns
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['cpu_usage', 'memory_usage', 'response_time', 'uptime']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill NaN values with appropriate defaults
            df = df.fillna({
                'cpu_usage': 0,
                'memory_usage': 0,
                'response_time': 0,
                'uptime': 0,
                'status': 'unknown'
            })
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error processing monitoring data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def process_security_alerts(alerts: List[Dict]) -> pd.DataFrame:
        """Process security alerts data"""
        if not alerts:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(alerts)
            
            # Convert timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Standardize severity levels
            if 'severity' in df.columns:
                df['severity'] = df['severity'].apply(DataProcessor.standardize_severity)
            
            # Ensure required columns
            required_cols = ['device_id', 'alert_type', 'severity', 'message']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 'Unknown'
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error processing security alerts: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def standardize_severity(severity: str) -> str:
        """Standardize security severity levels"""
        if not severity or pd.isna(severity):
            return "info"
        
        severity = str(severity).lower().strip()
        
        severity_mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'info': 'info',
            'information': 'info',
            'warning': 'medium',
            'error': 'high',
            'alert': 'high'
        }
        
        return severity_mapping.get(severity, 'info')
    
    @staticmethod
    def calculate_availability(uptime_data: List[Dict], time_window: int = 24) -> float:
        """Calculate device availability percentage"""
        if not uptime_data:
            return 0.0
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(uptime_data)
            
            if 'timestamp' not in df.columns or 'status' not in df.columns:
                return 0.0
            
            # Filter data within time window
            cutoff_time = datetime.now() - timedelta(hours=time_window)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[df['timestamp'] >= cutoff_time]
            
            if df.empty:
                return 0.0
            
            # Calculate uptime percentage
            total_records = len(df)
            online_records = len(df[df['status'] == 'online'])
            
            return (online_records / total_records) * 100 if total_records > 0 else 0.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating availability: {e}")
            return 0.0
    
    @staticmethod
    def aggregate_metrics_by_device(metrics: pd.DataFrame) -> Dict[str, Dict]:
        """Aggregate metrics by device"""
        if metrics.empty:
            return {}
        
        try:
            aggregated = {}
            
            if 'device_id' not in metrics.columns:
                return {}
            
            for device_id in metrics['device_id'].unique():
                device_metrics = metrics[metrics['device_id'] == device_id]
                
                aggregated[device_id] = {
                    'avg_cpu': device_metrics['cpu_usage'].mean() if 'cpu_usage' in device_metrics else 0,
                    'avg_memory': device_metrics['memory_usage'].mean() if 'memory_usage' in device_metrics else 0,
                    'avg_response_time': device_metrics['response_time'].mean() if 'response_time' in device_metrics else 0,
                    'total_uptime': device_metrics['uptime'].sum() if 'uptime' in device_metrics else 0,
                    'record_count': len(device_metrics),
                    'last_update': device_metrics['timestamp'].max() if 'timestamp' in device_metrics else None
                }
            
            return aggregated
            
        except Exception as e:
            logger.error(f"❌ Error aggregating metrics: {e}")
            return {}
    
    @staticmethod
    def filter_recent_data(df: pd.DataFrame, hours: int = 24, timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """Filter data to recent time period"""
        if df.empty or timestamp_col not in df.columns:
            return df
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            return df[df[timestamp_col] >= cutoff_time]
            
        except Exception as e:
            logger.error(f"❌ Error filtering recent data: {e}")
            return df
    
    @staticmethod
    def generate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for a DataFrame"""
        if df.empty:
            return {}
        
        try:
            stats = {
                'total_records': len(df),
                'unique_devices': df['device_id'].nunique() if 'device_id' in df.columns else 0,
                'date_range': {
                    'start': df['timestamp'].min() if 'timestamp' in df.columns else None,
                    'end': df['timestamp'].max() if 'timestamp' in df.columns else None
                }
            }
            
            # Add numeric column statistics
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                stats[f'{col}_stats'] = {
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'std': df[col].std()
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error generating summary stats: {e}")
            return {}
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, filename: str) -> bool:
        """Export DataFrame to CSV file"""
        try:
            df.to_csv(filename, index=False)
            logger.info(f"✅ Data exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def format_bytes(bytes_value: float) -> str:
        """Format bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(np.floor(np.log(bytes_value) / np.log(1024)))
        p = np.power(1024, i)
        s = round(bytes_value / p, 2)
        
        return f"{s} {size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
