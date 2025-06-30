from storages.backends.s3boto3 import S3Boto3Storage
from .base import BaseStorage

class S3Storage(BaseStorage):
    def __init__(self):
        self.storage = S3Boto3Storage()

    def save(self, name, content):
        return self.storage.save(name, content)

    def url(self, name):
        return self.storage.url(name)

    def delete(self, name):
        return self.storage.delete(name)
