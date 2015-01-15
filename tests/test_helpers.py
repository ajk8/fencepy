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

    def test_str2bool(self):
        for true in ('True', 'true', 'TRUE', 'T', 't', 'Yes', 'yes', 'YES', 'Y', 'y', '1', 'truE', 'yEs'):
            self.assertTrue(helpers.str2bool(true))
        for false in ('False', 'false', 'FALSE', 'F', 'f', 'No', 'no', 'NO', 'N', 'n', '0', 'faLsE', 'nO'):
            self.assertFalse(helpers.str2bool(false))
        for error in ('bad', '10', None, 1, 'truee'):
            with raises(ValueError):
                helpers.str2bool(error)
