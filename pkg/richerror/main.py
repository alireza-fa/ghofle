from pkg.richerror.error import RichError, error_message, error_code, get_error_info


def generate_error():
    op = "richerror.main.generate_error"

    raise RichError(operation=op, message="an error occurred", code=2, error=None)


def generate_error_two():
    try:
        generate_error()
    except RichError as ex:
        raise RichError(operation="richerror.main.generate_error_two", error=ex)


def generate_error_three():
    try:
        generate_error_two()
    except RichError as ex:
        raise RichError(operation="richerror.main.generate_error_three", error=ex, message="error occurred 3")


if __name__ == "__main__":
    try:
        generate_error_three()
    except RichError as err:
        print("code is: ", error_code(err))
        print("message is: ", error_message(error=err))
        error_log = list()
