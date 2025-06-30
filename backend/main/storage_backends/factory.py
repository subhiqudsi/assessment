from django.conf import settings

from .local import LocalStorage
from .s3 import S3Storage

def get_storage_backend():
    backend = getattr(settings, 'STORAGE_BACKEND', 'local')

    if backend == 's3':
        return S3Storage()
    elif backend == 'local':
        return LocalStorage()
    else:
        raise ValueError(f"Unsupported storage backend: {backend}")
