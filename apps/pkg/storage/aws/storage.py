from django.conf import settings

import functools

from apps.pkg.storage.base import Storage


class AwsStorage(Storage):

    def __init__(self, access_key: str, secret_key: str, bucket_name: str, endpoint_url: str, service_name: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.service_name = service_name

    def get_file(self, filename: str) -> object:
        pass

    def get_files(self) -> object:
        pass

    def put_file(self, file: object) -> str:
        pass

    def delete_file(self, filename: str) -> bool:
        pass


@functools.cache
def get_aws_storage_instance():
    return AwsStorage(
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        service_name=settings.AWS_SERVICE_NAME,
    )
