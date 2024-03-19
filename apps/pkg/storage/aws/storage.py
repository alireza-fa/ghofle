from datetime import datetime, timedelta
from typing import Dict
from uuid import uuid4

import boto3.session
from django.conf import settings

import functools

from apps.pkg.storage.base import Storage
from apps.pkg.storage.exceptions import FilePutErr, GetFilesErr, GetFileErr, GetFileUrlErr, DeleteFileErr


class AwsStorage(Storage):

    def __init__(self, access_key: str, secret_key: str, bucket_name: str,
                 endpoint_url: str, service_name: str, expire_link: int):
        self.bucket_name = bucket_name
        self.expire_link = expire_link
        session = boto3.session.Session()
        self.conn = session.client(
            service_name=service_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url
        )

    def get_file_url(self, filename: str) -> str:
        try:
            url = self.conn.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': filename
                },
                ExpiresIn=int(self.expire_link),
                HttpMethod='GET'
            )
            return url
        except Exception as err:
            raise GetFileUrlErr(err)

    def get_file(self, filename: str) -> Dict:
        try:
            response = self.conn.get_object(
                Bucket=self.bucket_name,
                Key=filename,
                ResponseExpires=datetime.now() + timedelta(seconds=60),
            )

            return response
        except Exception as err:
            raise GetFileErr(err)

    def get_files(self) -> object:
        try:
            result = self.conn.list_objects_v2(
                Bucket=self.bucket_name
            )
            if result['KeyCount']:
                return result['Contents']
        except Exception as err:
            raise GetFilesErr(err)

    def put_file(self, file: object) -> Dict:
        try:
            key = f"{uuid4()}.{file.name.split('.')[-1]}",
            data = self.conn.put_object(
                Bucket=self.bucket_name,
                Key=key[0],
                Body=file
            )
            if data["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {
                    "filename": key[0],
                    "size": file.size,
                }

        except Exception as err:
            raise FilePutErr(err)

    def delete_file(self, filename: str):
        try:
            self.conn.delete_object(
                Bucket=self.bucket_name, Key=filename
            )
        except Exception as err:
            raise DeleteFileErr(err)


@functools.cache
def get_aws_storage_instance():
    return AwsStorage(
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        service_name=settings.AWS_SERVICE_NAME,
        expire_link=settings.AWS_EXPIRE_LINK,
    )
