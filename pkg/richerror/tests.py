from unittest import TestCase

from . import codes, constants
from .error import RichError, error_code, get_error_info


class RichErrorTest(TestCase):

    def test_error_one_layer(self):
        op = "richerror.tests.RichErrorTest.test_error_one_layer"
        message = "layer one error occurred"

        err = RichError(operation=op, message=message, code=12)

        self.assertEqual(str(err), message)
        self.assertEqual(error_code(error=err), 12)

    def test_error_two_layers(self):
        op = "richerror.tests.RichErrorTest.test_error_two_layers"
        message = "layer one error occurred"

        err1 = RichError(operation=op, message=message, code=12)
        err2 = RichError(operation=op, error=err1)
        self.assertEqual(str(err2), message)
        self.assertEqual(error_code(error=err2), 12)

    def test_error_three_layers(self):
        op = "richerror.tests.RichErrorTest.test_error_three_layers"
        message = "layer one error occurred"

        err1 = RichError(operation=op, message=message, code=12)
        err2 = RichError(operation=op, error=err1)
        err3 = RichError(operation=op, error=err2)

        self.assertEqual(str(err3), message)
        self.assertEqual(error_code(error=err3), 12)

    def test_error_code_with_exception_error(self):
        err_ex = Exception("an exception")

        self.assertEqual(error_code(err_ex), codes.UNKNOWN_CODE)

    def test_str__message_in_exception_error(self):
        message_ex = "an exception message"

        err_ex = Exception(message_ex)

        op = "richerror.tests.RichErrorTest.test_error_three_layers"
        err1 = RichError(operation=op, code=12, error=err_ex)

        self.assertEqual(str(err1), message_ex)

    def test_str_message_in_rich_error_with_exception_error(self):
        message_ex = "an exception message"

        err_ex = Exception(message_ex)

        op = "richerror.tests.RichErrorTest.test_str_message_in_rich_error_with_exception_error"
        message = "layer one error occurred"
        err1 = RichError(operation=op, code=12, message=message, error=err_ex)

        self.assertEqual(str(err1), message)
        self.assertEqual(error_code(err1), 12)

    def test_three_layer_message_in_layer_two(self):
        op = "richerror.tests.RichErrorTest.test_three_layer_message_in_layer_two"
        message = "layer two error occurred"

        err1 = RichError(operation=op, message="layer one message", code=12)
        err2 = RichError(operation=op, error=err1, message=message)
        err3 = RichError(operation=op, error=err2)

        self.assertEqual(str(err3), message)
        self.assertEqual(error_code(error=err3), 12)

    def test_get_error_info_one_layer(self):
        op = "richerror.tests.RichErrorTest.test_get_error_info_one_layer"
        message = "layer one error occurred"

        err1 = RichError(operation=op, message=message, code=12)
        err_info = get_error_info(error=err1)

        self.assertEqual(err_info, [{
            constants.Operation: op,
            constants.Code: 12,
            constants.Message: message,
        }])

    def test_get_error_info_layer_one_exception_error_two_layer(self):
        message_ex = "exception message"
        err_ex = Exception(message_ex)

        op = "richerror.tests.RichErrorTest.test_get_error_info_one_layer"
        message = "layer two error occurred"
        err1 = RichError(operation=op, message=message, code=12, error=err_ex)

        err_info = get_error_info(error=err1)

        self.assertEqual(err_info, [
            {
                constants.Operation: op,
                constants.Code: 12,
                constants.Message: message,
            },
            {
                constants.Operation: "",
                constants.Code: codes.UNKNOWN_CODE,
                constants.Message: message_ex
            }
        ])

    def test_get_error_info_layer_one_exception_error_three_layer(self):
        message_ex = "exception message"
        err_ex = Exception(message_ex)

        op = "richerror.tests.RichErrorTest.test_get_error_info_layer_one_exception_error_three_layer"
        message1 = "layer tow error occurred"
        message2 = "layer three error occurred"
        err1 = RichError(operation=op, message=message1, code=12, error=err_ex)
        err2 = RichError(operation=op, message=message2, code=15, error=err1)

        err_info = get_error_info(error=err2)

        self.assertEqual(err_info, [
            {
                constants.Operation: op,
                constants.Code: 15,
                constants.Message: message2,
            },
            {
                constants.Operation: op,
                constants.Code: 12,
                constants.Message: message1
            },
            {
                constants.Operation: "",
                constants.Code: codes.UNKNOWN_CODE,
                constants.Message: message_ex,
            }
        ])

    def test_get_error_info_layer_one_exception_error_three_layer2(self):
        message_ex = "exception message"
        err_ex = Exception(message_ex)

        op = "richerror.tests.RichErrorTest.test_get_error_info_layer_one_exception_error_three_layer2"
        err1 = RichError(operation=op, code=12, error=err_ex)
        err2 = RichError(operation=op, code=15, error=err1)

        err_info = get_error_info(error=err2)

        self.assertEqual(err_info, [
            {
                constants.Operation: op,
                constants.Code: 15,
                constants.Message: message_ex,
            },
            {
                constants.Operation: op,
                constants.Code: 12,
                constants.Message: message_ex
            },
            {
                constants.Operation: "",
                constants.Code: codes.UNKNOWN_CODE,
                constants.Message: message_ex,
            }
        ])

    def test_four_layer_error(self):
        op = "richerror.tests.RichErrorTest.test_four_layer_error"
        message = "layer one error occurred"

        err1 = RichError(operation=op, message=message, code=12)
        err2 = RichError(operation=op, error=err1)
        err3 = RichError(operation=op, error=err2)
        err4 = RichError(operation=op, error=err3)

        self.assertEqual(str(err4), message)
        self.assertEqual(error_code(error=err4), 12)
