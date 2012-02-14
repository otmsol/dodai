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

import os
import sys
import random
import configparser
from collections import OrderedDict
from dodai.util import find

class TstProjectBase(object):

    def _build_random_text(self, min=5, max=15):
        """Build random text
        """
        out = []
        character_count = random.randint(min, max)
        for x in range(0, character_count):
            out.append(self._build_random_character())
        return ''.join(out)

    def _build_random_character(self):
        """Build a random printable character
        """
        character = chr(random.randint(0, sys.maxunicode))
        if (character.isprintable()
                and character.isalnum()
                and character not in (' ', '=', '%')):
            return character
        else:
            return self._build_random_character()


class TstProjectSection(TstProjectBase):
    """Callable object used to create a section of data
    """
    SECTION_TYPES = ('basic', 'db', 'db_file')
    PROTOCOLS = ('postgresql', 'mysql', 'oracle', 'mssql')

    def __init__(self, project_config_directory, data, db_data, encoding):
        self.project_config_directory = project_config_directory
        self.data = data
        self.db_data = db_data
        self.encoding = encoding

    def __call__(self, section_type):
        section_name = self._build_section_name()
        if section_type in self.SECTION_TYPES:
            if 'basic' == section_type:
                return self._build_basic(section_name)
            elif 'db' == section_type:
                return self._build_db(section_name)
            elif 'db_file' == section_type:
                return self._build_db_file(section_name)
        return OrderedDict()

    def _build_section_name(self):
        section_name = self._build_random_text()
        if section_name in self.data:
            return self._build_section_name()
        else:
            return section_name

    def _build_db(self, section_name):
        out = OrderedDict()
        out[section_name] = OrderedDict()
        out[section_name]['db_dialect'] = random.choice(self.PROTOCOLS)
        out[section_name]['hostname'] = self._build_random_text(5, 10)
        out[section_name]['port'] = random.randint(1, 65535)
        out[section_name]['username'] = self._build_random_text(5, 10)
        out[section_name]['password'] = self._build_random_text(5, 10)
        out[section_name]['database'] = self._build_random_text(5, 10)
        out[section_name]['schema'] = self._build_random_text(5, 10)
        return out

    def _build_db_file(self, section_name):
        out = OrderedDict()
        out[section_name] = OrderedDict()
        out[section_name]['db_dialect'] = 'sqlite'
        out[section_name]['filename'] = self._build_db_filename()
        return out

    def _build_db_filename(self):
        """Generates a random sqlite filename
        """
        dir = os.path.join(self.project_config_directory, 'data')
        if not os.path.exists(dir):
            os.mkdir(dir)
        name = "{0}.sqlite".format(self._build_random_text())
        path = os.path.join(dir, name)
        if os.path.exists(path):
            return self._build_db_filename()
        else:
            f = open(path, 'w', encoding=self.encoding)
            f.close()
            return path

    def _build_basic(self, section_name):
        out = OrderedDict()
        out[section_name] = OrderedDict()
        key_count = random.randint(3, 10)
        for x in range(0, key_count):
            key = self._build_basic_key(section_name, out)
            val = self._build_random_text(3, 250)
            out[section_name][key] = val
        return out

    def _build_basic_key(self, section_name, out):
        key = self._build_random_text()
        if key in out[section_name]:
            return self._build_basic_key(section_name, out)
        else:
            return key


class TstProjectConfigFile(TstProjectBase):
    """Callable object used to create a config file
    """

    def __init__(self, project_config_directory, data, db_data, encoding):
        self.project_config_directory = project_config_directory
        self.data = data
        self.db_data = db_data
        self.encoding = encoding
        self._build_section = TstProjectSection(self.project_config_directory,
                                                self.data, self.db_data,
                                                self.encoding)

    def __call__(self, filename):
        data = self._build()
        config = configparser.ConfigParser()
        config.update(data)
        filename = os.path.join(self.project_config_directory, filename)
        with open(filename, 'w', encoding=self.encoding) as configfile:
            config.write(configfile)

    def _build(self):
        data = OrderedDict()
        section_count = random.randint(10, 25)
        for x in range(0, section_count):
            section_type = random.choice(TstProjectSection.SECTION_TYPES)
            section_data = self._build_section(section_type)
            data.update(section_data)
            if section_type in ('db', 'db_file'):
                self.db_data.update(section_data)
            self.data.update(section_data)
        return data


class TstProject(TstProjectBase):
    """Object used to generate a random project along with all of it's config
    files for testing.
    """
    def __init__(self):
        self._encoding_ = None
        self._project_name_ = None
        self._project_config_directory_ = None
        self._project_config_files_ = []
        self.data = OrderedDict()
        self.db_data = OrderedDict()
        self._build_config_file_ = None

    @property
    def _build_config_file(self):
        """Property holding callable class that builds a config file
        """
        if not self._build_config_file_:
            self._build_config_file_ = TstProjectConfigFile(
                    self.project_config_directory, self.data, self.db_data,
                    self.encoding)
        return self._build_config_file_

    @property
    def encoding(self):
        """Property holding the system's character encoding
        """
        if not self._encoding_:
            self._encoding_ = sys.getfilesystemencoding()
            if not self._encoding_:
                self._encoding_ = sys.getdefaultencoding()
        return self._encoding_

    @property
    def project_name(self):
        """Property holding the randomly generated project name
        """
        if not self._project_name_:
            self._project_name_ = self._build_project_name()
        return self._project_name_

    @property
    def project_config_directory(self):
        """Property holding the project's config directory path in the
        home directory
        """
        if not self._project_config_directory_:
            self._project_config_directory_ = find.home_direcotry(
                            project_name=self.project_name)
        return self._project_config_directory_

    @property
    def project_config_files(self):
        """Property holding the project's config file names
        """
        if not self._project_config_files_:
            file_count = random.randint(3,
                                        len(find.ConfigFiles.FILENAME_ROOTS))
            files = random.sample(find.ConfigFiles.FILENAME_ROOTS, file_count)
            for filename in files:
                extension = random.choice(find.ConfigFiles.FILENAME_EXTENSIONS)
                if extension:
                    filename = "{0}.{1}".format(filename, extension)
                self._project_config_files_.append(filename)
        return self._project_config_files_

    def _build_project_name(self):
        """Builds the name of the project.  This also checks to insure that
        no directory exists for this project already exists.  If the
        directory already exists, a new name will be generated
        """
        project_name = self._build_random_text()
        dir = find.home_direcotry(project_name=project_name)
        if os.path.exists(dir):
            return self._build_project_name()
        else:
            self._mkdir(project_name)
            return project_name

    def _mkdir(self, project_name):
        """Creates the project config directory in the home directory.
        Also creates a empty file which is used to identify this as a test
        directory.
        """
        path = find.home_direcotry(project_name=project_name)
        os.mkdir(path)
        filename = os.path.join(path, '___dodai_test___')
        f = open(filename, 'w')
        f.close()

    def clean_up(self):
        """This recursively removes any dodai test config directories
        """
        path = find.home_direcotry()
        dirs = []
        for name in os.listdir(path):
            if name.startswith("."):
                filepath = os.path.join(path, name)
                filename = os.path.join(filepath, '___dodai_test___')
                if os.path.exists(filename):
                    dirs.append(filepath)

        for dir in dirs:
            for root, dirs, files in os.walk(dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(dir)

    def setup(self):
        """This is the main function used to build all of the test config
        files
        """

        self.clean_up()

        # Reset all the class variables
        self._project_name_ = None
        self._project_config_directory_ = None
        self._project_config_files_ = []
        self.data = OrderedDict()
        self.db_data = OrderedDict()
        self._build_config_file_ = None

        # Loop through each config file name and build the names
        for config_file in self.project_config_files:
            self._build_config_file(config_file)

    def teardown(self):
        """Used after all of the testing is done to clean up directories
        by deleting them.
        """
        # Clean up any test config directories that may exist
        self.clean_up()

