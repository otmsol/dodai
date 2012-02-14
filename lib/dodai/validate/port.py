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

class IsValidPort(BaseValidate):

    MSG = "In the config section '{section_name}' the '{key}' of '{val}' "\
          "is not a valid port number.  The value of '{key}' should be an "\
          "integer between 1 and 65535"

    LOG_TYPE = "critical"
    KEY = 'port'

    def __call__(self, section_name, key=None):
        key = key or self.KEY
        if self._validate_field(section_name, key):

            val = self._sections[section_name].get(key)
            try:
                val = int(val)
            except ValueError:
                return self._raise_error(section_name, key, val)
            else:
                if val < 1 or val > 65535:
                    return self._raise_error(section_name, key, val)
            return True
        return False

    def _raise_error(self, section_name, key, val):
        self._process_error(section_name=section_name, key=key, val=val)
        return False
