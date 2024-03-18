from apps.pkg.storage.aws.storage import get_aws_storage_instance
from apps.pkg.storage.base import Storage


def get_storage() -> Storage:
    return get_aws_storage_instance()
