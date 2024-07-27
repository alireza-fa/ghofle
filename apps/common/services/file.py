from apps.common.models import File
from apps.common.services.storage import put_file, delete_file
from pkg.logger import category
from pkg.logger.logger import new_logger


logger = new_logger()


def create_file(file_type: int, file: bytearray) -> File:
    properties = {
        "FileType": file_type,
        "Filename": file.name,
        "Size": file.size,
    }
    try:
        upload_info = put_file(file=file, log_properties={"FileType": file_type})

        file = File.objects.create(
            file_type=file_type,
            filename=upload_info["filename"],
            size=upload_info["size"],
        )

        properties["Id"] = file.id
        properties["Filename"] = file.filename
        properties["size"] = file.size
        logger.info(message="create a new file. file type: %d, size: %d" % (file_type, file.size),
                    category=category.FILE, sub_category=category.CREATE_FILE, properties=properties)

        return file
    except Exception as err:
        properties["Error"] = str(err)
        logger.error(message="an error occurred when trying to create a new file",
                     category=category.FILE, sub_category=category.CREATE_FILE, properties=properties)
        raise err


def get_file_by_filename(filename: str) -> File:
    return File.objects.get(filename=filename)


def delete_file_by_filename(filename: str):
    properties = {"Filename": filename}

    file = get_file_by_filename(filename=filename)

    delete_file(filename=filename, log_properties=properties)

    logger.info(message="deleted file with filename: %s" % file.filename,
                category=category.FILE, sub_category=category.DELETE_FILE, properties=properties)

    file.delete()
