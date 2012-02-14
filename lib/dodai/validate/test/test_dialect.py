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
from dodai.validate.dialect import IsValidDialect


class TestValidateDialect(unittest.TestCase):

    def setUp(self):
        self._validate = IsValidDialect.load(self.sections)

    @property
    def sections(self):
        if not hasattr(self, '_sections_') or not self._sections_:
            self._sections_ = {
                'blue': {
                    'dialect': 'postgresql',
                },
                'red': {
                    'dialect': 'foo'
                },
            }
        return self._sections_

    def test_is_valid(self):
        self.assertTrue(self._validate('blue'))

    def test_not_valid(self):
        with self.assertRaises(ValueError) as e:
            self._validate('red')
