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


class _BaseExists(object):

    LOG_TYPE = "debug"
    RAISE = ValueError

    def __init__(self, sections, log=None, log_type=None, raise_errors=True):
        self._sections = sections
        self._log = log
        self._log_type = log_type or self.LOG_TYPE
        self._raise_errors = raise_errors
        self._log_this_ = None

    def _process_error(self, **kwargs):
        if self._log or self._raise_errors:
            msg = self.MSG.format(**kwargs)
            if self._log:
                self._log_this(msg)
            if self._raise_errors:
                raise self.RAISE(msg)
        return False

    @property
    def _log_this(self):
        if not self._log_this_:
            if self._log:
                self._log_this_ = getattr(self._log, self._log_type)
        return self._log_this_


class SectionExists(_BaseExists):

    MSG = "The config section of '{section_name}' does not exist"

    RAISE = KeyError

    def __call__(self, section_name):
        if section_name in self._sections:
            return True
        else:
            return self._process_error(section_name=section_name)


class KeyExists(_BaseExists):

    MSG = "In the config section '{section_name}' the field of '{key}' does "\
          "not exist"

    RAISE = KeyError

    def __call__(self, section_name, key):
        if key in self._sections[section_name]:
            return True
        else:
            return self._process_error(section_name=section_name, key=key)


class ValueExists(_BaseExists):

    MSG = "In the config section '{section_name}' the '{key}' is not set or "\
          "is empty"

    def __call__(self, section_name, key):
        data = self._sections[section_name].get(key)
        if data:
            return True
        else:
            return self._process_error(section_name=section_name, key=key)


class BaseValidate(_BaseExists):

    def __init__(self, sections, section_exists, key_exists, value_exists,
                 log=None, log_type=None, raise_errors=True):
        super(BaseValidate, self).__init__(sections, log, log_type,
                                           raise_errors)
        self._section_exists = section_exists
        self._key_exists = key_exists
        self._value_exists = value_exists

    @classmethod
    def load(cls, sections, log=None, log_type=None, raise_errors=True):
        section_exists = SectionExists(sections, log, log_type, raise_errors)
        key_exists = KeyExists(sections, log, log_type, raise_errors)
        value_exists = ValueExists(sections, log, log_type, raise_errors)
        return cls(sections, section_exists, key_exists, value_exists, log,
                   log_type, raise_errors)

    def _validate_field(self, section_name, key):
        if self._section_exists(section_name):
            if self._key_exists(section_name, key):
                if self._value_exists(section_name, key):
                    return True
        return False
