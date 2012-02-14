#
# Copyright (C) 2011 Leonard Thomas
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

from nose import tools as nt
from dodai.model.parse import Parse
from dodai.tst.base import TstProject

class TestParse(TstProject):

    def test_sections(self):
        """Make sure all the sections have been created
        """
        parse = Parse(self.project_name)
        data = parse()
        for section, dct in self.data.items():
            nt.ok_(section in data)

    def test_variables(self):
        """Make sure all of the variables have been created
        """
        parse = Parse(self.project_name)
        data = parse()
        for section, dct in self.data.items():
            for key, val in dct.items():
                nt.ok_(key in data[section])

    def test_values(self):
        """Make sure all of the variables listed in the config files
        actually exist and are correct
        """
        parse = Parse(self.project_name)
        data = parse()
        for section, dct in self.data.items():
            for key, val in dct.items():
                nt.eq_(data[section][key], str(val))
