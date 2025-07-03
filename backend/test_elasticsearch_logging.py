import logging
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

import django
django.setup()

# Get the logger
logger = logging.getLogger('hr_system')

# Test various log levels and fields
logger.info("Testing Elasticsearch logging integration")

# Test with user information
logger.info("User login successful", extra={
    'user_id': 123,
    'username': 'john.doe',
    'ip_address': '192.168.1.100',
    'action': 'login'
})

# Test with candidate information
logger.info("New candidate application submitted", extra={
    'candidate_id': 456,
    'application_id': 789,
    'username': 'jane.smith',
    'action': 'application_submit'
})

# Test warning with user context
logger.warning("Failed login attempt", extra={
    'username': 'unknown_user',
    'ip_address': '10.0.0.50',
    'action': 'login_failed',
    'attempt_count': 3
})

# Test error logging
try:
    1 / 0
except Exception as e:
    logger.error("Division by zero error occurred", extra={
        'user_id': 999,
        'username': 'admin',
        'action': 'calculation_error'
    }, exc_info=True)

print("\nLogs have been sent to:")
print("- File: logs/hr_system.log")
print("- Console: Above output")
print("- Elasticsearch: hr-system-logs-YYYY.MM.DD index")
print("\nNote: Elasticsearch handler will only work if Elasticsearch is running on localhost:9200")
print("You can configure Elasticsearch connection using environment variables:")
print("- ELASTICSEARCH_HOSTS (default: localhost:9200)")
print("- ELASTICSEARCH_USE_SSL (default: False)")
print("- ELASTICSEARCH_VERIFY_CERTS (default: True)")
print("- ELASTICSEARCH_AUTH_TYPE (default: basic)")
print("- ELASTICSEARCH_USERNAME")
print("- ELASTICSEARCH_PASSWORD")
print("- ELASTICSEARCH_API_KEY (if using API key auth)")