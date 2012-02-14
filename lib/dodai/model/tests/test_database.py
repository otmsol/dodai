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
from dodai.model.parse import Parse
from dodai.model.database import IsDatabaseSection
from dodai.model.database import GetDatabase
from dodai.model.database import GetAllDatabaseSections


class _BaseTest(unittest.TestCase):

    def setUp(self):
        self.is_database_section = IsDatabaseSection(self.sections)

    @property
    def sections(self):
        if not hasattr(self, '_sections_') or not self._sections_:
            self._sections_ = {
                'default': {
                    'environment': 'prod'
                },
                'db.blue': {
                    'dialect': 'postgresql',
                    'driver': 'psycopg2',
                    'group': 'frontend',
                    'environment': 'prod',
                    'host': 'localhost',
                    'port': '1234',
                    'username': 'abcd',
                    'password': 'abc123',
                    'schema': 'test'
                },
                'db.green': {
                    'dialect': 'mysql',
                    'ignore': 'false',
                    'group': 'frontend',
                    'environment': 'dev',
                    'host': 'localhost',
                    'port': '12345',
                    'username': 'abcd',
                    'password': 'abc123',
                    'schema': 'test'
                },
                'db.purple': {
                    'dialect': 'sqlite',
                    'ignore': 'no',
                    'filepath': '/a/b/c'
                },
                'db.red': {
                    'dialect': 'oracle',
                    'ignore': 'true'
                },
                'db.yellow': {
                    'dialect': 'bad_dialect',
                    'host': 'nothing',
                    'username': 'foo',
                    'password': 'bar'
                },
                'db.orange': {
                    'host': 'localhost',
                    'password': 'foo',
                    'username': 'bar'
                }
            }
        return self._sections_


class TestValidDatabaseSections(_BaseTest):
    def runTest(self):
        for name in ('db.blue', 'db.green', 'db.purple',):
            msg = "Processed: '{0}'".format(name)
            self.assertTrue(self.is_database_section(name), msg=msg)


class TestIgnoreDatabaseSectios(_BaseTest):
    def runTest(self):
        for name in ('default', 'db.red'):
            self.assertFalse(self.is_database_section(name))


class TestBadDatabaseSections(_BaseTest):
    def runTest(self):
        with self.assertRaises(ValueError):
            self.is_database_section('db.yellow')

        with self.assertRaises(KeyError):
            self.is_database_section('db.orange')
            self.is_database_section('iro')




if __name__ == '__main__':
    unittest.main()
