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
from dodai.util import find
import os
import sys
import random

class TestFindConfigFiles(object):
    """This test is used to make sure that the dodai.util.find actually
    finds all of the default config files.  This test will create a
    random project name using any unicode character.
    """
    MESSAGE = "The config file: '{filename}' with the encoding: '{encoding}' "\
              "doesn't exist."

    def __init__(self):
        self._encoding = None
        self.project_name, self.project_path = self.build_project_name()
        self.filenames = self.build_filenames(self.project_path)

    @property
    def encoding(self):
        """Property holding the system encoding
        """
        if not self._encoding:
            self._encoding = sys.getfilesystemencoding()
            if not self._encoding:
                self._encoding = sys.getdefaultencoding()
        return self._encoding

    def build_random_name(self):
        """Builds a random unicode string
        """
        out = []
        character_count = random.randint(3, 20)
        for x in range(0, character_count):
            character = self._random_character()
            out.append(character)
        return ''.join(out)

    def _random_character(self):
        """Build a random printable character
        """
        character = chr(random.randint(0, sys.maxunicode))
        if character.isprintable():
            return character
        else:
            return self._random_character()

    def build_project_name(self):
        """Build a random name for a project
        """
        project_name = self._build_project_name()
        project_path = self.build_project_path(project_name)
        while os.path.exists(project_path):
            project_name = self._build_project_name()
            project_path = self.build_project_path(project_name)
        return (project_name, project_path,)

    def _build_project_name(self):
        project_name = self.build_random_name()
        while project_name:
            try:
                project_name.encode(self.encoding)
            except UnicodeEncodeError:
                project_name = self.build_random_name()
            else:
                break
        return project_name

    def build_project_path(self, project_name):
        """Builds a string of the full path to the given project_name in
        the home directory.
        """
        project_path = "~/.{0}".format(project_name)
        project_path = os.path.expanduser(project_path)
        return project_path

    def build_filenames(self, project_path):
        """Builds all the possible full paths to all possible config files
        """
        out = []
        for root in find.ConfigFiles.FILENAME_ROOTS:
            for ext in find.ConfigFiles.FILENAME_EXTENSIONS:
                if ext:
                    name = "{0}.{1}".format(root, ext)
                    out.append(os.path.join(project_path, name))
                else:
                    out.append(os.path.join(project_path, root))
        return out

    def erase_project_path(self):
        """Erases the test directory and all of it's files created by
        this script
        """
        if os.path.exists(self.project_path):
            for root, dirs, files in os.walk(self.project_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.project_path)

    def build_project_config_files(self):
        """Creates the config directory and all config files that will
        be used by this test
        """
        if not os.path.exists(self.project_path):
            os.mkdir(self.project_path.encode(self.encoding))
        for config_file in self.filenames:
            f = open(config_file.encode(self.encoding),
                                        'w', encoding=self.encoding)
            f.close()

    def setup(self):
        """class wide setup function
        """
        self.erase_project_path()
        self.build_project_config_files()

    def teardown(self):
        """class wide teardown function
        """
        self.erase_project_path()

    def test_find_default_config_files(self):
        files = find.config_files(self.project_name)
        for filename, encoding in files:
            nt.ok_((filename, encoding) in files, msg=self.MESSAGE.format(
                    filename=filename, encoding=encoding))
