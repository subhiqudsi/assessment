from django.core.files.storage import FileSystemStorage
from .base import BaseStorage

class LocalStorage(BaseStorage):
    def __init__(self):
        self.storage = FileSystemStorage()

    def save(self, name, content):
        return self.storage.save(name, content)

    def url(self, name):
        return self.storage.url(name)

    def delete(self, name):
        return self.storage.delete(name)