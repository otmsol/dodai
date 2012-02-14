#
# Copyright (C) 2012 Leonard Thomas
#
# This file is part of Dodai.
#
# Dodai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dodai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dodai.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from dodai.validate.base import SectionExists
from dodai.validate.base import KeyExists
from dodai.validate.base import ValueExists


class MockLogger(object):

    def __init__(self):
        self.debug_val = None
        self.critical_val = None

    def debug(self, msg):
        self.debug_val = msg

    def critical(self, msg):
        self.critical_val = msg


class BaseTestBaseValidate(unittest.TestCase):

    @property
    def sections(self):
        if not hasattr(self, '_sections_') or not self._sections_:
            self._sections_ = {
                'blue': {
                    'foo': 'bar',
                    'check': ''
                }
            }
        return self._sections_


class TestSectionExists(BaseTestBaseValidate):

    def setUp(self):
        self._validate = SectionExists(self.sections)

    def test_valid_section(self):
        msg = "the section of 'blue' does not exist"
        self.assertTrue(self._validate('blue') , msg)

    def test_missing_section(self):
        with self.assertRaises(KeyError) as e:
            self._validate('iro')


class TestSectionExistsWithLogger(BaseTestBaseValidate):

    def setUp(self):
        self.log = MockLogger()
        self._validate = SectionExists(self.sections, log=self.log,
                                       log_type='critical')

    def test_valid_section(self):
        msg = "the section of 'blue' does not exist"
        self.assertTrue(self._validate('blue') , msg)

    def test_missing_section(self):
        with self.assertRaises(KeyError) as e:
            self._validate('iro')

        self.assertIsNotNone(self.log.critical_val)


class TestKeyExists(BaseTestBaseValidate):

    def setUp(self):
        self._validate = KeyExists(self.sections)

    def test_valid_key(self):
        self.assertTrue(self._validate('blue', 'foo'))

    def test_missing_key(self):
        with self.assertRaises(KeyError):
            self._validate('blue', 'iro')


class TestValueExists(BaseTestBaseValidate):

    def setUp(self):
        self._validate = ValueExists(self.sections)

    def test_value_exists(self):
        self.assertTrue(self._validate('blue', 'foo'))

    def test_missing_value(self):
        with self.assertRaises(ValueError):
            self._validate('blue', 'check')
