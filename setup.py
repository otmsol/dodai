#
#    Copyright 2011 Leonard Thomas Mike Crute
#
#    This file is part of Dodai.
#
#    Dodai is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dodai is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dodai.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from setuptools import setup
from setuptools import find_packages
from subprocess import Popen
from subprocess import PIPE

try:
    # This is probably Linux
    from ctypes.util import _findLib_ldconfig as find_library
except ImportError:
    # This is something else (maybe Mac OS X?)
    from ctypes.util import find_library

class _BaseLibCheck(object):

    def _has_library(self, lib):
        if find_library(lib):
            return True
        return False

    def _which(self, name):
        cmd = ['which', name]
        return Popen(cmd, stdout=PIPE).communicate()[0]

    def _is_package(self, package):
        if package.strip().lower().startswith(self.PACKAGE.lower()):
            return True
        return False


class PostgressLibCheck(_BaseLibCheck):

    PACKAGE = 'psycopg2'
    LIB = 'pq'

    def __call__(self, package):
        if self._is_package(package):
            if self._has_library(self.LIB):
                return True
            return False


class MysqlLibCheck(_BaseLibCheck):

    PACKAGE = 'mysql-python'
    LIB = 'mysqlpp'

    def __call__(self, package):
        if self._is_package(package):
            # Seems that mysql-python doesn't work in python 3 yet
            if sys.version < '3.0':
                if self._has_library(self.LIB):
                    if self._which('mysql_config'):
                        return True
            return False


class OracleLibCheck(_BaseLibCheck):

    PACKAGE = 'cx_oracle'
    LIB = 'clntsh'

    def __call__(self, package):
        if self._is_package(package):
            if 'ORACLE_HOME' in os.environ:
                if os.environ['ORACLE_HOME']:
                    return True
            else:
                if self._has_library(self.LIB):
                    self._set_oracle_home()
                    return True
            return False

    def _set_oracle_home(self):
        path = find_library(self.LIB)
        os.environ['ORACLE_HOME'] = os.path.dirname(path)


class OrderedDictLibCheck(_BaseLibCheck):

    PACKAGE = 'ordereddict'

    def __call__(self, package):
        if self._is_package(package):
            if sys.version < '2.7':
                return True
            return False


class ArgparseLibCheck(_BaseLibCheck):

    PACKAGE = 'argparse'

    def __call__(self, package):
        if self._is_package(package):
            if sys.version < '2.7':
                return True
            return False


class InstallRequires(object):

    def __init__(self, chain):
        self._chain = chain

    def __call__(self, packages):
        out = []
        for package in packages:
            result = self._check_package(package)
            if result is not None:
                if result:
                    out.append(package)
            else:
                out.append(package)
        return out

    def _check_package(self, package):
        result = None
        for obj in self._chain:
            result = obj(package)
            if result is not None:
                return result
        return result

    @classmethod
    def load(cls):
        chain = (
            PostgressLibCheck(),
            MysqlLibCheck(),
            OracleLibCheck(),
            OrderedDictLibCheck(),
            ArgparseLibCheck(),
        )
        return cls(chain)


ARGS = {
    'name': 'dodai',
    'version': '0.5.0',
    'install_requires': [
        'SQLAlchemy',
        'ordereddict',
        'psycopg2',
        'mysql-python',
        'cx_Oracle'
    ],
    'platforms': [
        'Linux',
        'Darwin',
    ],
    'author': 'Leonard Thomas',
    'author_email': '1970inazuma@gmail.com',
    'url': 'http://code.google.com/p/dodai',
    'download_url': 'http://code.google.com/p/dodai/downloads/list',
    'license': 'GPLv3',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS 9',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: PL/SQL',
        'Programming Language :: PROGRESS',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'description': "Module code for quick easy access to parsed text based "\
        "config file data and configured database engines.",
    'long_description': "This module provides code for quick easy access to "\
        "parsed text based config file data and configured database "\
        "engines.  All config file data is returned ordered and transformed "\
        "to unicode objects and database connections are returned as "\
        "sqlalchemy objects.",
    'zip_safe': False,
    'packages': find_packages('lib'),
    'package_dir': {'':'lib'},
}


if __name__ == '__main__':

    if sys.version < '2.6':
        message = "{package} is not able to install:  The version of python "\
                  "that is being used, '{version}', is not compatable with "\
                  "{package}.  {package} will only install with Python "\
                  "version {package_version} or greater"
        message = message.format(package=ARGS['name'], version=sys.version,
                                 package_version='2.6')
        sys.stderr.write(message)
        sys.exit(1)

    install_requires = InstallRequires.load()
    ARGS['install_requires'] = install_requires(ARGS['install_requires'])

    setup(**ARGS)
