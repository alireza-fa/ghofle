from abc import ABC, abstractmethod
from typing import Dict


class Storage(ABC):

    @abstractmethod
    def get_file_url(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_file(self, filename: str) -> Dict:
        pass

    @abstractmethod
    def get_files(self) -> Dict:
        pass

    @abstractmethod
    def put_file(self, file: object) -> Dict:
        pass

    @abstractmethod
    def delete_file(self, filename: str) -> bool:
        pass
