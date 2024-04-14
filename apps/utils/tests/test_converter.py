from django.test import SimpleTestCase

from apps.utils.converter import persian_to_english


class TestConverter(SimpleTestCase):
    def test_persian_to_english(self):
        valid_number = persian_to_english(number="gfr345tt0")
        self.assertEqual(valid_number, "3450")

        valid_number = persian_to_english(number="۰۹۸۰888")
        self.assertEqual(valid_number, "0980888")

        valid_number = persian_to_english(number="سلامmo9لس۸u$@#!_۰")
        self.assertEqual(valid_number, "980")
