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

from dodai.validate.base import BaseValidate

class IsValidDialect(BaseValidate):

    MSG = "In the section '{section_name}', the '{key}' of: '{val}' is not "\
          "valid.  Please choose from the following: {dialects}"


    DIALECTS = ('access', 'drizzle', 'firebird', 'informix', 'maxdb', 'mysql',
                'mssql', 'oracle', 'postgresql', 'sqlite', 'sybase')

    LOG_TYPE = "critical"
    KEY = 'dialect'

    def __call__(self, section_name, key=None):
        key = key or self.KEY
        if self._validate_field(section_name, key):
            val = self._sections[section_name].get(key)
            if val not in self.DIALECTS:
                return self._process_error(section_name=section_name, key=key,
                                    val=val, dialects=repr(self.DIALECTS))
            return True
        return False

