from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    def save(self, name, content):
        pass

    @abstractmethod
    def url(self, name):
        pass

    @abstractmethod
    def delete(self, name):
        pass
