from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def get_file(self, filename: str) -> object:
        pass

    @abstractmethod
    def get_files(self) -> object:
        pass

    @abstractmethod
    def put_file(self, file: object) -> str:
        pass

    @abstractmethod
    def delete_file(self, filename: str) -> bool:
        pass
