from typing import Dict

from pkg.logger import category
from pkg.richerror.error import RichError, get_error_info
from pkg.storage.exceptions import GetFileUrlErr, GetFileErr, GetFilesErr, FilePutErr, DeleteFileErr
from pkg.storage.storage import get_storage
from pkg.logger.logger import new_logger


storage = get_storage()
log = new_logger()


def get_file_url(filename: str, log_properties: Dict) -> str:
    op = "common.services.storage.get_file_url"

    try:
        return storage.get_file_url(filename=filename)
    except GetFileUrlErr as ex:
        log_properties[category.ERROR] = get_error_info(error=ex)
        log.error(message=f"error get file url, filename: {filename}, error: {ex}",
                  category=category.STORAGE, sub_category=category.GET_FILE_URL, properties=log_properties)
        raise RichError(operation=op, error=ex)


def get_file(filename: str, log_properties: Dict):
    op = "common.services.storage.get_file"

    try:
        return storage.get_file(filename=filename)
    except GetFileErr as ex:
        log_properties[category.ERROR] = get_error_info(error=ex)
        log.error(message=f"error get file, filename: {filename}, error: {ex}",
                  category=category.STORAGE, sub_category=category.GET_FILE, properties=log_properties)
        raise RichError(operation=op, error=ex)


def get_files(log_properties: Dict) -> Dict:
    op = "common.services.storage.get_files"

    try:
        return storage.get_files()
    except GetFilesErr as ex:
        log_properties[category.ERROR] = get_error_info(error=ex)
        log.error(message=f"error get files, error: {ex}",
                  category=category.STORAGE, sub_category=category.GET_FILES, properties=log_properties)
        raise RichError(operation=op, error=ex)


def put_file(file: object, log_properties: Dict) -> Dict:
    op = "common.services.storage.put_file"

    try:
        return storage.put_file(file=file)
    except FilePutErr as ex:
        log_properties[category.ERROR] = get_error_info(error=ex)
        log.error(message=f"error put file, filename: {file.name}, error: {ex}",
                  category=category.STORAGE, sub_category=category.PUT_FILE, properties=log_properties)
        raise RichError(operation=op, error=ex)


def delete_file(filename: str, log_properties: Dict) -> bool:
    op = "common.services.storage.delete_file"

    try:
        return storage.delete_file(filename=filename)
    except DeleteFileErr as ex:
        log_properties[category.ERROR] = get_error_info(error=ex)
        log.error(message=f"error delete file, filename: {filename}, error: {ex}",
                  category=category.STORAGE, sub_category=category.DELETE_FILE, properties=log_properties)
        raise RichError(operation=op, error=ex)
