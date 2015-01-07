from unittest import TestCase
from py.test import raises
from fencepy import helpers


class TestHelpers(TestCase):

    def test_pseudo_merge_dict(self):
        dto = {
            'a': 'aa',
            'b': ['bb', 'cc'],
            'e': {'f': 'ff'}
        }
        dfrom = {
            'b': ['cc', 'dd'],
            'e': {'g': {'h': 'hh'}}
        }
        expected = {
            'a': 'aa',
            'b': ['cc', 'dd'],
            'e': {
                'f': 'ff',
                'g': {'h': 'hh'}
            }
        }

        helpers.pseudo_merge_dict(dto, dfrom)
        self.assertEqual(dto, expected)

    def test_pseudo_merge_dict_bad_dfrom(self):
        dto = {
            'a': 'aa',
            'b': ['bb', 'cc'],
        }
        dfrom = ['i', 'will', 'not', 'merge']
        with raises(ValueError):
            helpers.pseudo_merge_dict(dto, dfrom)

    def test_pseudo_merge_dict_bad_dto(self):
        dto = ['i', 'will', 'not', 'merge']
        dfrom = {
            'b': ['cc', 'dd'],
            'e': {'f': 'ff'}
        }
        with raises(ValueError):
            helpers.pseudo_merge_dict(dto, dfrom)
