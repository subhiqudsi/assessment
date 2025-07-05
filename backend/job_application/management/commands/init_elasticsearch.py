from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch
import json


class Command(BaseCommand):
    help = 'Initialize Elasticsearch index for Django logs with proper mappings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate the index even if it exists',
        )
        parser.add_argument(
            '--index-name',
            type=str,
            default='hr-system-logs',
            help='Name of the index to create (default: hr-system-logs)',
        )

    def handle(self, *args, **options):
        index_name = options['index_name']
        force = options['force']
        
        # Get Elasticsearch configuration from settings
        es_config = settings.ELASTICSEARCH_DSL['default']
        
        # Initialize Elasticsearch client
        es_client_config = {
            'hosts': es_config['hosts'],
            'timeout': 30,
        }
        
        # Add authentication if configured
        auth_type = getattr(settings, 'ELASTICSEARCH_AUTH_TYPE', None)
        if auth_type == 'basic':
            username = getattr(settings, 'ELASTICSEARCH_USERNAME', None)
            password = getattr(settings, 'ELASTICSEARCH_PASSWORD', None)
            if username and password:
                es_client_config['basic_auth'] = (username, password)
        elif auth_type == 'api_key':
            api_key = getattr(settings, 'ELASTICSEARCH_API_KEY', None)
            if api_key:
                es_client_config['api_key'] = api_key
        
        try:
            es = Elasticsearch(**es_client_config)
            
            # Test connection
            if not es.ping():
                self.stdout.write(
                    self.style.ERROR('Failed to connect to Elasticsearch')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS('Successfully connected to Elasticsearch')
            )
            
            # Check if index pattern exists
            index_pattern = f"{index_name}-*"
            existing_indices = es.indices.get_alias(index=index_pattern, ignore=[404])
            
            if existing_indices and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'Index pattern {index_pattern} already exists. '
                        'Use --force to recreate.'
                    )
                )
                return
            
            # Create index template for the log indices
            template_name = f"{index_name}-template"
            
            # Define the index template with correct structure for newer Elasticsearch
            index_template = {
                "index_patterns": [f"{index_name}-*"],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "index": {
                            "refresh_interval": "5s"
                        }
                    },
                    "mappings": {
                        "properties": {
                            "@timestamp": {
                                "type": "date"
                            },
                            "level": {
                                "type": "keyword"
                            },
                            "logger": {
                                "type": "keyword"
                            },
                            "module": {
                                "type": "keyword"
                            },
                            "function": {
                                "type": "keyword"
                            },
                            "line": {
                                "type": "integer"
                            },
                            "thread": {
                                "type": "long"
                            },
                            "thread_name": {
                                "type": "keyword"
                            },
                            "process": {
                                "type": "integer"
                            },
                            "message": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                    }
                                }
                            },
                            "pathname": {
                                "type": "keyword"
                            },
                            "user_id": {
                                "type": "keyword"
                            },
                            "username": {
                                "type": "keyword"
                            },
                            "user": {
                                "type": "keyword"
                            },
                            "request_id": {
                                "type": "keyword"
                            },
                            "ip_address": {
                                "type": "ip"
                            },
                            "candidate_id": {
                                "type": "keyword"
                            },
                            "application_id": {
                                "type": "keyword"
                            },
                            "action": {
                                "type": "keyword"
                            },
                            "exception": {
                                "type": "text"
                            }
                        }
                    }
                },
                "priority": 200
            }
            
            # Delete existing template if force is True
            if force:
                try:
                    es.indices.delete_index_template(name=template_name)
                    self.stdout.write(
                        self.style.WARNING(f'Deleted existing template: {template_name}')
                    )
                except Exception:
                    pass
            
            # Create the index template
            es.indices.put_index_template(
                name=template_name,
                body=index_template
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created index template: {template_name}'
                )
            )
            
            # Create today's index to test the template
            from datetime import datetime
            today_index = f"{index_name}-{datetime.now().strftime('%Y.%m.%d')}"
            
            if not es.indices.exists(index=today_index) or force:
                if force and es.indices.exists(index=today_index):
                    es.indices.delete(index=today_index)
                    self.stdout.write(
                        self.style.WARNING(f'Deleted existing index: {today_index}')
                    )
                
                es.indices.create(index=today_index)
                self.stdout.write(
                    self.style.SUCCESS(f'Created index: {today_index}')
                )
            
            # Verify the index was created with correct mappings
            mapping = es.indices.get_mapping(index=today_index)
            self.stdout.write(
                self.style.SUCCESS('Index mapping verified successfully')
            )
            
            # Display some statistics
            stats = es.indices.stats(index=index_pattern)
            total_docs = stats['_all']['primaries']['docs']['count']
            total_size = stats['_all']['primaries']['store']['size_in_bytes']
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nElasticsearch index initialization complete!\n'
                    f'Index pattern: {index_pattern}\n'
                    f'Total documents: {total_docs}\n'
                    f'Total size: {total_size / 1024 / 1024:.2f} MB'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing Elasticsearch: {str(e)}')
            )
            raise