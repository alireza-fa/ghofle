from django.test import SimpleTestCase

from apps.utils.file import change_filename


class TestFile(SimpleTestCase):
    def test_change_filename(self):
        new_filename = change_filename(filename="nothing.png")
        self.assertEqual(new_filename.split(".")[-1], "png")
