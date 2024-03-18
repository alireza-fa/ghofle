from typing import Dict

from apps.pkg.logger import category
from apps.pkg.storage.exceptions import GetFileUrlErr, GetFileErr, GetFilesErr, FilePutErr, DeleteFileErr
from apps.pkg.storage.storage import get_storage
from apps.pkg.logger.logger import new_logger


storage = get_storage()
log = new_logger()


def get_file_url(filename: str, log_properties: Dict) -> str:
    try:
        return storage.get_file_url(filename=filename)
    except GetFileUrlErr as err:
        log.error(message=f"error get file url, filename: {filename}, error: {err}",
                  category=category.STORAGE, sub_category=category.GET_FILE_URL, properties=log_properties)
        raise GetFileUrlErr(err)


def get_file(filename: str, log_properties: Dict):
    try:
        return storage.get_file(filename=filename)
    except GetFileErr as err:
        log.error(message=f"error get file, filename: {filename}, error: {err}",
                  category=category.STORAGE, sub_category=category.GET_FILE, properties=log_properties)
        raise GetFileErr(err)


def get_files(log_properties: Dict) -> Dict:
    try:
        return storage.get_files()
    except GetFilesErr as err:
        log.error(message=f"error get files, error: {err}",
                  category=category.STORAGE, sub_category=category.GET_FILES, properties=log_properties)
        raise GetFilesErr(err)


def put_file(file: object, log_properties: Dict) -> Dict:
    try:
        return storage.put_file(file=file)
    except FilePutErr as err:
        log.error(message=f"error put file, filename: {file.name}, error: {err}",
                  category=category.STORAGE, sub_category=category.PUT_FILE, properties=log_properties)
        raise FilePutErr(err)


def delete_file(filename: str, log_properties: Dict) -> bool:
    try:
        return storage.delete_file(filename=filename)
    except DeleteFileErr as err:
        log.error(message=f"error delete file, filename: {filename}, error: {err}",
                  category=category.STORAGE, sub_category=category.DELETE_FILE, properties=log_properties)
        raise DeleteFileErr(err)
