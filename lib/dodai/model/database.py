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

from dodai.validate.base import SectionExists


from dodai.model.parse import ValidateFieldExistsAndIsPopulated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DodaiSqlalchemyConnection(object):
    """A dodai connection object that should be used in applications for
    interacting with a database with sqlalchemy
    """

    DEFAULT_KEY = "__default__"

    def __init__(self, name, url, **kwargs):
        self.name = name
        schema = kwargs.get('schema')
        if schema:
            self.schema = schema
        self.__url = url
        self.__create_engine = kwargs.get('create_engine') or create_engine
        self.__sessionmaker = kwargs.get('sessionmaker') or sessionmaker
        self.__kwargs = kwargs
        self.__engine = None
        self.__connection_cache = {}
        self.__active_connection_key = None
        self.__session_cache = {}
        self.__active_session_key = None

    @property
    def engine(self):
        """The sqlalchemy engine made from sqlalchemy.create_engine
        """
        if not self.__engine:
            self.__engine = self.__create_engine(url, **self.__kwargs)
        return self.__engine

    @property
    def connection_cache(self):
        """Dictionary of names with engine.connect()
        """
        if not self.__connection_cache:
            self.__connection_cache[self.DEFAULT_KEY] = self.engine.connect()
        return self.__connection_cache

    @property
    def active_connection_key(self):
        """The name of the active connection.  This name is used to return
        the connection when calling '.connection'.
        """
        if not self.__active_connection_key:
            self.__active_connection_key = self.DEFAULT_KEY
        return self.__active_connection_key

    @property
    def connection(self):
        """Returns the active connection from the connection_cache by
        the active_connection_key.
        """
        return self.connection_cache[self.active_connection_key]

    def set_active_connection_key(self, name=None):
        """Sets the active_connection_key to the given name.  If the given
        name does not exist in the connection_cache a new connection will
        be created and saved in the connection_cache with the given name.
        Then the active_connection_key will be set to the name.  If name is
        not given the active_connection_key will be set to the default value.
        """
        if name:
            if name not in self.connection_cache:
                self.connection_cache[name] = self.engine.connect()
            self.active_connection_key = name
        else:
            self.active_connection_key = self.DEFAULT_KEY

    @property
    def session_cache(self):
        """A dictionary of sqlalchemy sessions
        """
        if not self.__session_cache:
            session = self.__sessionmaker(bind=self.engine)
            self.__session_cache[self.DEFAULT_KEY] = session()
        return self.__session_cache

    @property
    def active_session_key(self):
        """The name of the active session.  This name identifies which
        session to pull when calling '.session'.
        """
        if not self.__active_session_key:
            self.__active_session_key = self.DEFAULT_KEY
        return self.__active_session_key

    @property
    def session(self):
        """Returns the active sqlalchemy session object by the key of
        active_session_key.
        """
        return self.session_cache[self.active_session_key]

    def set_active_session_key(self, name=None):
        """Sets the active_session_key to the given name.  If the given
        name does not exist in the session_cache a new session will
        be created and saved in the sessioin_cache with the given name.
        Then the actives_session_key will be set to the name.  If name is
        not given the active_session_key will be set to the default value.
        """
        if name:
            if name not in self.session_cache:
                session = self.__sessionmaker(bind=self.engine)
                self.session_cache[name] = session()
            self.active_session_key = name
        else:
            self.active_session_key = self.DEFAULT_KEY


class IsDatabaseSection(object):
    """
    Callable object used to determine if a config section is a valid
    database section.

    A config database section is defined by it's prefix in the config data.
    The default prefix is **db**

    The section can also have a key of **ignore** that when set to true will
    be skipped without processing.

    To use this class::

        from dodai.database import IsDatabaseSection

        # Immitate config file data
        sections = {
            'db.blue': {
                'dialect': 'sqlite',
                'path': '~/.foo/bar.db
                'ignore': 'false'
            },
            'db.yellow': {
                'dialect': 'sqlite',
                'path': '~/.foo1/bar.db
                'ignore': 'true'
            },
            'db.green': {
                'dialect': 'postgresql',
                'host': 'localhost',
                'username': 'foo',
                'password': 'bar',
                'port': '1234',
                'database': 'blah',
                'schema': 'test',
            }
        }

        is_database_section = IsDatabaseSection.load(sections)

        # Call to see if a section is valid
        if is_database_section('db.blue'):
            # Do something
    """

    PREFIX = 'db'
    IGNORE_KEY = 'ignore'
    IGNORE_NEGATIVE_VALUES = ('false', 'no', '0')
    IGNORE_MESSAGE = "The config section '{section_name}' has been ignored"
    DIALECT_KEY = 'dialect'

    def __init__(self, sections, section_exists, is_valid_dialect, prefix=None,
                 log=None, raise_errors=True):
        """
        :param sections: A dictionary that contains config data usually the
            result of parsing config files
        :param section_exists: A function (callable object) that validates
            that a section exists.  Should be like
            'dodai.validate.base.SectionExists'
        :param is_valid_dialect: A function (callable object) that validates
            that a section contains the dialect key and it's a valid key.
            should be like 'dodai.validate.dialect.IsValidDialect'
        :param prefix: The prefix of the section name that will identify
            the section as a database section.  Default is 'db'
        :param log: An instance of 'logger'
        :param raise_errors: If set to True then all errors will be raised
        """
        self._sections = sections
        self._section_exist = section_exist
        self._is_valid_dialect = is_valid_dialect
        self._prefix = prefix or self.PREFIX


    @classmethod
    def load(cls, sections, prefix=None, log=None, raise_errors=True):
        section_exists = SectionExists(sections, log=log,
                                       raise_errors=raise_errors)
        is_valid_dialect = IsValidDialect(sections, log=log,
                                          raise_errors=raise_errors)
        return cls(sections, section_exists, is_valid_dialect, prefix,
                   log, raise_errors)

    def __call__(self, section_name):
        if self._section_exist(section_name):
            if section_name.startswith(self._prefix):
                if self._should_ignore(section_name):
                    if self._is_valid_dialect(section_name, self.DIALECT_KEY):
                        return True
        return False

    def _should_ignore(self, section_name):
        if self.IGNORE_KEY in self._sections[section_name]:
            data = self._sections[section_name].get(self.IGNORE_KEY)
            if not data or data not in self.IGNORE_NEGATIVE_VALUES:
                if self._log:
                    msg = self.IGNORE_MESSAGE.format(
                            section_name = section_name
                    )
                    self._log.debug(msg)
                return True
        return False


class _BaseDatabaseConnectionValidator(object):

    def __init__(self, sections, is_database_section, log=None,
                 raise_erros=True):
        self._sections = sections
        self._is_database_section = is_database_section
        self._log = log

    @classmethod
    def load(cls, sections, prefix=None, log=None, raise_errors=True):
        is_database_section = IsDatabaseSection(sections, prefix, log,
                                                raise_errors)
        return cls(sections, is_database_section, log, raise_errors)



    def _validate_fields(self, section_name):
        if self._is_database_section(section_name):
            for field in self.REQUIRED:
                pass



class _BaseDatabaseConnectionValidator(object):
    """Base class that is used to wire up the actual validators and contains
    methods that are used by all validators.
    """

    def __init__(self, sections, find_database_section_trigger,
                    is_database_section, validate_field_exists):
        self._sections = sections
        self._find_database_section_trigger = find_database_section_trigger
        self._is_database_section = is_database_section
        self._validate_field_exists = validate_field_exists

    @classmethod
    def load(cls, sections):
        find_database_section_trigger = FindDatabaseSectionTrigger(sections)
        is_database_section = IsDatabaseSection(sections)
        validate_field_exists = ValidateFieldExistsAndIsPopulated(sections)
        return cls(sections, find_database_section_trigger,
                is_database_section, validate_field_exists)


    def _validate_fields(self, section_name):
        if self._is_database_section(section_name):
            pass



    def _validate_fields(self, section_name, raise_errors=True):
        """This is the first method that should be used by a validator.  It
        reqires the section_name; This is a section within a configfile. And,
        it will raise database configuration errors by default.  This will
        gracefully pass when a section doesn't contain database configuration
        data
        """

        # First we have to determine the database trigger which is
        # a key within the config section that identifies the section
        # as containing database connection information
        trigger = self._find_database_section_trigger(section_name)

        # Figure out if the trigger within the section actually
        # contains a valid dialect.  Also if the section has an
        # ignore key set to true, it will not be processed
        if self._is_database_section(section_name, trigger):

            # Make sure the dialect listed in the section can be
            # processed with the validator
            dialect = self._sections[section_name].get(trigger).lower()
            if dialect in self.DIALECTS:
                out = True

                # Loop through the child class' required fields
                for field_name in self.REQUIRED:

                    # Validate that the field actually exists and is populated
                    hold = self._validate_field_exists(section_name,
                                                       field_name,
                                                       raise_errors)
                    if not hold:
                        out = False
                return out


class _BaseNetworkDatabaseValidator(_BaseDatabaseConnectionValidator):
    """Base class that is used for adding more methods to network-databases for
    validating fields in a config file connection data.
    """
    PORT_ERROR = "In the section: '{section_name}' the port number of "\
                 "'{port}' is invalid.  This should be an integer between "\
                 "1 and 65535"

    def _validate_port(self, section_name, raise_errors=True):
        port = self._sections[section_name].get('port')
        try:
            port = int(port)
        except ValueError:
            self._port_error(section_name, port, raise_errors)
            return False
        else:
            if port > 1 and port > 65535:
                self._port_error(section_name, port, raise_errors)
                return False
        return True

    def _port_error(self, section_name, port, raise_errors):
        if raise_errors:
            message = self.PORT_ERROR.format(
                    section_name=section_name,
                    port=port)
            raise ValueError(message)


class FileDatabaseValidator(_BaseDatabaseConnectionValidator):
    """Callable used for validating file-database connection data
    """
    DIALECTS = ('sqlite', 'access')
    REQUIRED = ('filename',)

    def __call__(self, section_name, raise_errors=True):
        return self._validate_fields(section_name, raise_errors)


class NetworkDatabaseValidator(_BaseNetworkDatabaseValidator):
    """Callable used for validating network-database connection data.  These
    connection data must contain schema.
    """
    DIALECTS = ('drizzle', 'firebird', 'informix', 'maxdb', 'mssql', 'oracle',
                'postgresql', 'sybase')
    REQUIRED = ('hostname', 'port', 'username', 'password', 'database',
                'schema')

    def __call__(self, section_name, raise_errors=True):
        if self._validate_fields(section_name, raise_errors):
            return self._validate_port(section_name, raise_errors)


class NetworkDatabaseValidatorNoSchema(_BaseNetworkDatabaseValidator):
    """Callable used for validating network-database connection data.  These
    connection data does NOT contain schema.
    """
    DIALECTS = ('mysql',)
    REQUIRED = ('hostname', 'port', 'username', 'password', 'database')

    def __call__(self, section_name, raise_errors=True):
        if self._validate_fields(section_name, raise_errors):
            return self._validate_port(section_name, raise_errors)


class DatabaseSectionConnectionValidator(object):
    """Callable object that is used to validate a config section database
    information.
    """

    def __init__(self, find_section_database_trigger, is_database_section,
                 validators):
        self._find_section_database_trigger = find_section_database_trigger
        self._is_database_section = is_database_section
        self._validators = validators

    @classmethod
    def load(cls, sections, find_section_database_trigger=None):
        find_section_database_trigger = find_section_database_trigger or \
                                        FindDatabaseSectionTrigger(sections)
        is_database_section = IsDatabaseSection(sections)
        validators = (
            FileDatabaseValidator.load(sections),
            NetworkDatabaseValidator.load(sections),
            NetworkDatabaseValidatorNoSchema.load(sections)
        )
        return cls(find_section_database_trigger, is_database_section,
                   validators)

    def __call__(self, section_name, raise_errors=True):
        trigger_name = self._find_section_database_trigger(section_name)
        if self._is_database_section(section_name, trigger_name, raise_errors):
            for obj in self._validators:
                if obj(section_name, raise_errors):
                    return True


class GetAllDatabaseSections(object):
    """Callable object that returns a dictionary of valid database section
    data.
    """

    GROUP_NAME = "group"
    ENVIRONMENT_NAME = "environment"

    def __init__(self, sections, validate):
        self._sections = sections
        self._validate = validate
        self._cache = {
            'groups': {},
            'names': {}
        }

    @classmethod
    def load(cls, sections, find_section_database_trigger=None):
        find_section_database_trigger = find_section_database_trigger or \
                                        FindDatabaseSectionTrigger(sections)
        validate = DatabaseSectionConnectionValidator.load(sections,
                                        find_section_database_trigger)
        return cls(sections, validate)

    def __call__(self, raise_errors=True):
        if not self._cache['names']:
            self._build_cache(raise_errors)
        return self._cache

    def _build_cache(self, raise_errors):
        """Loops through the section data and populates the cache
        """
        for section_name in self._sections.keys():
            if self._validate(section_name, raise_errors):
                self._set_cache(section_name)

    def _set_cache(self, section_name):
        """Takes the given section_name and builds figures out where in
        the cache dictionary to put the section data.
        """
        group_name = self._get_group_name(section_name)
        if group_name:
            environment_name = self._get_environment_name(section_name)
            if environment_name:
                if group_name not in self._cache['groups']:
                    self._cache['groups'][group_name] = {}
                if environment_name not in self._cache['groups'][group_name]:
                    self._cache['groups'][group_name][environment_name] = \
                                                                section_name

        if section_name not in self._cache['names']:
            self._cache['names'][section_name] = self._sections[section_name]

    def _get_group_name(self, section_name):
        if self.GROUP_NAME in self._sections[section_name]:
            if self._sections[section_name][self.GROUP_NAME]:
                return self._sections[section_name][self.GROUP_NAME]
        return None

    def _get_environment_name(self, section_name):

        if self.ENVIRONMENT_NAME in self._sections[section_name]:
            if len(self._sections[section_name][self.ENVIRONMENT_NAME]):
                return self._sections[section_name][self.ENVIRONMENT_NAME]
        return None


class SqlalchemyUrlBuilder(object):

    def __init__(self, sections, find_section_database_trigger):
        self._find_section_database_trigger = find_section_database_trigger
        self._sections = sections

    def __call__(self, section_name):
        out = []
        self._dialect(section_name, out)
        self._driver(section_name, out)
        self._filename(section_name, out)
        self._username(section_name, out)
        self._password(section_name, out)
        self._hostname(section_name, out)
        self._database(section_name, out)

        out = ''.join(out)
        return out

    def _dialect(self, section_name, out):
        dialect = self._find_section_database_trigger(section_name)
        out.append(dialect)

    def _driver(self, section_name, out):
        driver = self._sections[section_name].get('driver')
        if driver:
            out.append('+')
            out.append(driver)

        out.append('://')

    def _filename(self, section_name, out):
        filename = self._sections[section_name].get('filename')
        if filename:
            out.append('/')
            out.append(filename)

    def _username(self, section_name, out):
        username = self._sections[section_name].get('username')
        if username:
            out.append(username)

    def _password(self, section_name, out):
        password = self._sections[section_name].get('password')
        if password:
            out.append(':')
            out.append(password)

    def _hostname(self, section_name, out):
        hostname = self._sections[section_name].get('hostname')
        if hostname:
            out.append('@')
            out.append(hostname)

    def _port(self, section_name, out):
        port = self._sections[section_name].get('port')
        if port:
            out.append(':')
            out.append(port)

    def _database(self, section_name, out):
        database = self._sections[section_name].get('database')
        if database:
            out.append('/')
            out.append(database)


class DodaiDatabaseObject(object):

    def __init__(self, url, **kwargs):
        self.__url = url
        self.__ignore__ = None
        self.__engine = None
        self.__session_cache = {}
        self._active_session_ = None
        self.__setup_kwargs(kwargs)

    @property
    def __ignore(self):
        if not self.__ignore__:
            out = self(self.__dict__.keys())
            out = out + ['username', 'user', 'password']
            self.__ignore__ = tuple(out)
        return self.__ignore__

    def __setup_kwargs(self, kwargs):
        for key in kwargs.keys():
            if key not in self.__ignore:
                setattr(self, key, kwargs[key])

    @property
    def engine(self):
        if not self.__engine:
            self.__engine = create_engine(self.__url)
        return self.__engine

    def make_session(self):
        """Makes a new session with this object's engine
        """
        Session = sessionmaker(bind=self.engine)
        return Session()

    @property
    def session_cache(self):
        if not self.__session_cache:
            self.__session_cache['__default__'] = self.make_session()
        return self.__session_cache

    def set_active_session(self, name):
        if name not in self.session_cache:
            session = self.make_session()
            self.session_cache[name] = session
        return self.session_cache[name]

    @property
    def active_session(self):
        if not self._active_session_:
            self._active_session_ = '__default__'
        return self._active_session_

    @property
    def session(self):
        out = self.session_cache[self.active_session]
        return out






class GetDatabase(object):

    ENVIRONMENT_SEARCH_SECTIONS = ('server', 'basic', 'default', 'system',
                                   'main')
    ENVIRONMENT_FIELD_NAMES = ('environment', 'env',)
    ENVIRONMENT_DEFAULT = 'dev'

    def __init__(self, sections, validate, database_sections,
                 as_sqlalchemy_url):
        self._sections = sections
        self._validate = validate
        self._database_sections = database_sections
        self._as_sqlalchemy_url = as_sqlalchemy_url
        self._environment_ = None
        self._url_cache = {}

    @classmethod
    def load(cls, sections):
        find_section_database_trigger = FindDatabaseSectionTrigger(sections)
        validate = DatabaseSectionConnectionValidator.load(
                                find_section_database_trigger, sections)
        get_all_database_sections = GetAllDatabaseSections(sections, validate)
        database_sections = get_all_database_sections()
        as_sqlalchemy_url = SqlalchemyUrlBuilder(sections,
                                                 find_section_database_trigger)
        return cls(sections, validate, database_sections)

    @property
    def environment(self):
        if not self._environment_:
            for section_name in self.ENVIRONMENT_SEARCH_SECTIONS:
                if section_name in self._sections:
                    for field_name in self.ENVIRONMENT_FIELD_NAMES:
                        if field_name in self._sections[section_name]:
                            if len(self._sections[section_name][field_name]):
                                self._environment_ = \
                                    self._sections[section_name][field_name]
                                break

        if not self._environment_:
            self._environment_ = self.ENVIRONMENT_DEFAULT

        return self._environment_

    def __call__(self, name, environment=None):
        name = self._find_name(name, environment)

    def _find_name(self, name, environment):
        environment = environment or self.environment

        if name in self._database_sections['groups']:
            if environment in self._database_sections['groups'][name]:
                if len(self._database_sections['groups'][name][environment]):
                    name = self._database_sections['groups'][name][environment]

        if name in self._database_sections['names']:
            return name
