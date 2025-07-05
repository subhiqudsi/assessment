import logging
import json
import threading
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from django.conf import settings


class ElasticsearchHandler(logging.Handler):
    def __init__(self, hosts, index_name='hr-system-logs', doc_type='_doc',
                 use_ssl=False, verify_certs=True, 
                 auth_type='basic', auth_details=None,
                 buffer_size=1000, flush_interval=1.0):
        super().__init__()
        
        self.index_name = index_name
        self.doc_type = doc_type
        self.buffer = []
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.es = None
        self._timer = None
        self._lock = threading.Lock()
        
        try:
            # Simple configuration for Elasticsearch client
            es_config = {
                'hosts': hosts,
                'timeout': 5,  # 5 second timeout
            }
            
            if auth_type == 'basic' and auth_details:
                username = auth_details.get('username')
                password = auth_details.get('password')
                if username and password:
                    es_config['basic_auth'] = (username, password)
            elif auth_type == 'api_key' and auth_details:
                api_key = auth_details.get('api_key')
                if api_key:
                    es_config['api_key'] = api_key
            
            self.es = Elasticsearch(**es_config)
            
            # Test connection with timeout - don't fail if ES is not ready
            try:
                if not self.es.ping():
                    print(f"Warning: Elasticsearch at {hosts} is not responding")
                    self.es = None
                else:
                    # Start periodic flush timer
                    self._start_flush_timer()
            except Exception as ping_error:
                print(f"Warning: Cannot ping Elasticsearch: {ping_error}")
                self.es = None
                
        except Exception as e:
            print(f"Warning: Failed to initialize Elasticsearch handler: {e}")
            self.es = None
    
    def emit(self, record):
        if not self.es:
            return
            
        try:
            log_entry = self.format_record(record)
            
            with self._lock:
                self.buffer.append({
                    '_index': f"{self.index_name}-{datetime.now().strftime('%Y.%m.%d')}",
                    '_source': log_entry
                })
                
                # Check if we should flush
                should_flush = (
                    record.levelname in ('ERROR', 'CRITICAL', 'WARNING') or 
                    len(self.buffer) >= self.buffer_size or
                    'Status updated' in record.getMessage() or 
                    'registration successful' in record.getMessage()
                )
            
            # Flush outside the lock to avoid blocking
            if should_flush:
                self.flush()
                
        except Exception as e:
            # Avoid infinite recursion by not using logging here
            print(f"Elasticsearch handler error: {e}")
            # Don't call handleError to avoid recursion
    
    def format_record(self, record):
        log_entry = {
            '@timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'message': record.getMessage(),
            'pathname': record.pathname,
        }
        
        # Add user information if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'username'):
            log_entry['username'] = record.username
            
        if hasattr(record, 'user'):
            log_entry['user'] = str(record.user)
            
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
            
        # Add any extra fields that might be useful
        if hasattr(record, 'candidate_id'):
            log_entry['candidate_id'] = record.candidate_id
            
        if hasattr(record, 'application_id'):
            log_entry['application_id'] = record.application_id
            
        if hasattr(record, 'action'):
            log_entry['action'] = record.action
            
        if record.exc_info:
            import traceback
            log_entry['exception'] = ''.join(traceback.format_exception(*record.exc_info))
            
        # Include any custom fields added to the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'pathname', 'process', 'processName', 'relativeCreated', 
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                if key not in log_entry:
                    try:
                        # Ensure the value is JSON serializable
                        json.dumps(value)
                        log_entry[key] = value
                    except (TypeError, ValueError):
                        log_entry[key] = str(value)
                    
        return log_entry
    
    def _start_flush_timer(self):
        """Start a timer to periodically flush the buffer"""
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.flush_interval, self._periodic_flush)
        self._timer.daemon = True
        self._timer.start()
    
    def _periodic_flush(self):
        """Periodically flush the buffer"""
        with self._lock:
            if self.buffer:
                self.flush()
        # Restart the timer
        if self.es:
            self._start_flush_timer()
    
    def flush(self):
        if not self.es or not self.buffer:
            return
            
        try:
            with self._lock:
                helpers.bulk(self.es, self.buffer)
                self.buffer = []
        except Exception as e:
            # Use print instead of logging to avoid recursion
            print(f"Failed to write logs to Elasticsearch: {e}")
            # Clear buffer to prevent infinite retry
            self.buffer = []
    
    def close(self):
        if self._timer:
            self._timer.cancel()
        self.flush()
        super().close()
