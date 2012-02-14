# Copyright (C) 2011  Leonard Thomas
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
from dodai.util import find
import os
import sys

def test_find_home_directory():
    """Basic test to make sure the home directory is returned.  Also checks
    to see if the passed in project_name is appended to the path in the
    returned value.
    """
    dir = find.home_direcotry()
    nt.ok_(os.path.exists(dir))

    project_name = 'test'
    dir = find.home_direcotry(project_name)
    project_name = ".{0}".format(project_name)
    nt.ok_(dir.endswith(project_name))

def test_find_system_config_directory():
    """Test to make sure the system config directory is returned.  Also checks
    to see if the passed in project_name is appended to the path in the
    returned value.
    """
    dir = find.system_config_directory()
    nt.ok_(os.path.exists(dir))

    project_name = 'test'
    dir = find.system_config_directory(project_name)
    nt.ok_(dir.endswith(project_name))

def test_find_project_config_directory():
    """Test to make sure the project directory is returned.  Also checks
    to be sure that 'config is appended to the returned value.
    """
    dir = find.project_config_directory(False)
    nt.ok_(os.path.exists(dir))

    dir = find.project_config_directory()
    nt.ok_(dir.endswith('config'))

def test_find_config_directories():
    """Test to make sure that three config directories are returned.
    """
    dirs = find.config_directories('test')
    nt.eq_(len(dirs), 3)

def test_find_config_files():
    """Test to make sure that the config files are being found
    """
    path_base = "~/test__dodai__config.test"
    path = os.path.expanduser(path_base)
    if os.path.exists(path):
        os.remove(path)
    f = open(path, 'w')
    f.close()
    files = find.config_files('test__dodai_config', path)
    nt.ok_(len(files) > 0)
    nt.eq_(files[0][0], path)
    if os.path.exists(path):
        os.remove(path)

def test_find_multiple_config_files():
    """Test to make sure that the multiple config files are being found
    """
    config_files = ['~/test__dodai__config.test', '~/test__dodai__config.cfg']
    non_exist_file = '~/test__dodai_config'
    good_files = []
    # touch the files
    for config_file in config_files:
        path = os.path.expanduser(config_file)
        good_files.append(path)
        if os.path.exists(path):
            os.remove(path)
        f = open(path, 'w')
        f.close()

    # Add a non existing file
    filenames = config_files + [non_exist_file]
    non_exist_file = os.path.exists(non_exist_file)
    files = find.config_files('test__dodai__config_', filenames, 'utf-8')
    for filename in good_files:
        nt.ok_((filename, 'utf-8') in files)
    nt.ok_((non_exist_file, 'utf-8') not in files)
    for filename in good_files:
        os.remove(filename)
