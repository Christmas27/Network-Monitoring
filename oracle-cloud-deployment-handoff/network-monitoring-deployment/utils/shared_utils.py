#!/usr/bin/env python3
"""
Shared Utilities for Network Monitoring Dashboard
"""

import streamlit as st
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import psutil
import socket
import subprocess
import platform
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """System performance monitoring utilities"""
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free = disk.free / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'available_gb': memory_available,
                    'total_gb': memory_total,
                    'used_gb': memory_total - memory_available
                },
                'disk': {
                    'percent': disk_percent,
                    'free_gb': disk_free,
                    'total_gb': disk_total,
                    'used_gb': disk_total - disk_free
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            return {}
    
    @staticmethod
    def check_port_availability(host: str, port: int, timeout: float = 3.0) -> bool:
        """Check if a port is available on a host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def ping_host(host: str, timeout: int = 3) -> Dict[str, Any]:
        """Ping a host and return response time"""
        try:
            # Determine ping command based on OS
            if platform.system().lower() == "windows":
                cmd = f"ping -n 1 -w {timeout*1000} {host}"
            else:
                cmd = f"ping -c 1 -W {timeout} {host}"
            
            start_time = time.time()
            result = subprocess.run(cmd.split(), 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=timeout+2)
            response_time = (time.time() - start_time) * 1000
            
            return {
                'host': host,
                'success': result.returncode == 0,
                'response_time_ms': response_time,
                'output': result.stdout,
                'error': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'host': host,
                'success': False,
                'response_time_ms': timeout * 1000,
                'output': '',
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'host': host,
                'success': False,
                'response_time_ms': 0,
                'output': '',
                'error': str(e)
            }

class CacheManager:
    """Simple caching utilities for dashboard components"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes
        self.default_ttl = default_ttl
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.default_ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with TTL"""
        ttl = ttl or self.default_ttl
        self.cache[key] = (value, time.time())
    
    def invalidate(self, key: str) -> None:
        """Invalidate cached value"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()

# Global cache instance
dashboard_cache = CacheManager()

class NotificationManager:
    """Notification system for dashboard events"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 50
    
    def add_notification(self, 
                        message: str, 
                        type: str = "info", 
                        duration: int = 5,
                        persistent: bool = False):
        """Add a notification"""
        notification = {
            'id': len(self.notifications),
            'message': message,
            'type': type,
            'timestamp': datetime.now(),
            'duration': duration,
            'persistent': persistent,
            'shown': False
        }
        
        self.notifications.append(notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
    
    def get_pending_notifications(self) -> List[Dict]:
        """Get notifications that haven't been shown"""
        pending = [n for n in self.notifications if not n['shown']]
        
        # Mark as shown
        for n in pending:
            n['shown'] = True
        
        return pending
    
    def show_notifications(self):
        """Display pending notifications in Streamlit"""
        notifications = self.get_pending_notifications()
        
        for notification in notifications:
            msg = f"**{notification['timestamp'].strftime('%H:%M:%S')}** - {notification['message']}"
            
            if notification['type'] == 'success':
                st.success(msg)
            elif notification['type'] == 'warning':
                st.warning(msg)
            elif notification['type'] == 'error':
                st.error(msg)
            else:
                st.info(msg)

# Global notification manager
notification_manager = NotificationManager()

def show_loading_spinner(text: str = "Loading..."):
    """Show loading spinner with text"""
    return st.spinner(text)

def format_timestamp(timestamp: Optional[datetime] = None, 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return str(timestamp)
    
    return timestamp.strftime(format_str)

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time difference"""
    now = datetime.now()
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return "Unknown"
    
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, default=str, indent=2)
    except (TypeError, ValueError):
        return default

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    return filename or 'unnamed_file'

def create_directory_if_not_exists(path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"❌ Error creating directory {path}: {e}")
        return False

def get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    try:
        size = Path(file_path).stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except Exception:
        return "Unknown"

def retry_operation(func: Callable, 
                   max_retries: int = 3, 
                   delay: float = 1.0,
                   backoff: float = 2.0) -> Any:
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
            time.sleep(delay)
            delay *= backoff

class BackgroundTask:
    """Simple background task runner"""
    
    def __init__(self):
        self.tasks = {}
    
    def run_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Run a task in background thread"""
        def task_wrapper():
            try:
                result = func(*args, **kwargs)
                self.tasks[task_id] = {
                    'status': 'completed',
                    'result': result,
                    'error': None,
                    'timestamp': datetime.now()
                }
            except Exception as e:
                self.tasks[task_id] = {
                    'status': 'failed',
                    'result': None,
                    'error': str(e),
                    'timestamp': datetime.now()
                }
        
        # Mark task as running
        self.tasks[task_id] = {
            'status': 'running',
            'result': None,
            'error': None,
            'timestamp': datetime.now()
        }
        
        # Start thread
        thread = threading.Thread(target=task_wrapper)
        thread.daemon = True
        thread.start()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        return self.tasks.get(task_id, {'status': 'not_found'})
    
    def is_task_running(self, task_id: str) -> bool:
        """Check if task is running"""
        return self.tasks.get(task_id, {}).get('status') == 'running'

# Global background task manager
background_tasks = BackgroundTask()

def show_debug_info():
    """Show debug information in sidebar"""
    if st.checkbox("🐛 Debug Info"):
        with st.expander("System Information"):
            metrics = PerformanceMonitor.get_system_metrics()
            if metrics:
                st.write(f"**CPU:** {metrics['cpu']['percent']:.1f}%")
                st.write(f"**Memory:** {metrics['memory']['percent']:.1f}%")
                st.write(f"**Disk:** {metrics['disk']['percent']:.1f}%")
        
        with st.expander("Session State"):
            st.json(dict(st.session_state))
        
        with st.expander("Cache Status"):
            st.write(f"**Cached Items:** {len(dashboard_cache.cache)}")
            for key in dashboard_cache.cache.keys():
                st.write(f"- {key}")

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
    }
    
    .error-card {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
    }
    
    .stButton > button {
        border-radius: 5px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stSelectbox > div > div {
        border-radius: 5px;
    }
    
    .stTextInput > div > div {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
