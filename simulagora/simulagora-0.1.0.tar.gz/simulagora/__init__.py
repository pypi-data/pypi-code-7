"""
HTTP client for Simulagora Web Services.

The main class of this module is `Simulagora` which is the Simulagora client.

The other class, AccountManager, is an helper to deal with you Simulagora
account(s) using a configuration file to store the connection infos.
"""

import os
import os.path as osp
import sys
import errno
import stat
import logging
import ConfigParser
import json
from itertools import chain, product
import hashlib
from base64 import b64encode, b64decode
from urlparse import urlparse
from pprint import pprint

import requests

from cwclientlib import cwproxy, builders


class ConfigFilePermissionError(Exception):
    """Custom exception for the configuration file permission errors.
    """
    pass


class ConfigFileFormatError(Exception):
    """Custom exception for the configuration file format errors.
    """
    pass


class AccountManager(object):
    """Account manager for Simulagora

    Manage account definitions for the Simulagora client, and read/ write them
    to/ from a configuration file (~/.simulagorarc by default).

    See example code below to create a configuration file with your account
    details.

    >>> from simulagora import AccountManager
    >>> amgr = AccountManager()
    >>> amgr.create_account("default_account", "https://www.simulagora.com",
                            "your_auth_token_name", "your_auth_token_secret")
    >>> amgr.write_config_file() # saves in ~/.simulagorarc by default
    """

    default_config_filepath = osp.join(osp.expanduser('~'), '.simulagorarc')
    config_file_perms = 33152

    def __init__(self):
        self.simulagora_account = ConfigParser.ConfigParser()

    def read_config_file(self, config_filepath=None):
        """Load a config file from ``config_filepath`` (or the default config
        file path if it was not passed), and return its path on success.

        Raises:
        - OSError if the file was not found.
        - ConfigFilePermissionError if the file is not readable and writable by
          its owner only.
        - ConfigFileFormatError if the file was not correctly formatted.
        """
        if config_filepath is None:
            config_filepath = self.default_config_filepath
        fstat = os.stat(config_filepath)
        if fstat.st_mode != self.config_file_perms:
            msg = 'file permission should be owner read/write only'
            raise ConfigFilePermissionError(msg)
        self.simulagora_account.read(config_filepath)
        for account_id in self.accounts:
            if (set(self.simulagora_account.options(account_id))
                    != set(('url', 'token_id', 'secret'))):
                raise ConfigFileFormatError('bad infos for account %r'
                                            % account_id)
        return config_filepath

    def create_account(self, account_id, url, token_id, secret):
        """Create an account which id is ``accound_id`` and url, token_id and
        secret are the one passed as arguments.

        Raises:
        - ConfigParser.DuplicateSectionError if an account with id
          ``account_id`` already exists.
        """
        self.simulagora_account.add_section(account_id)
        self.simulagora_account.set(account_id, 'url', url)
        self.simulagora_account.set(account_id, 'token_id', token_id)
        self.simulagora_account.set(account_id, 'secret', secret)

    def update_account(self, account_id, url=None, token_id=None, secret=None):
        """Update parameters (url, token_id and secret) specified as keyword
        arguments of the account ``accound_id``.
        """
        if url is not None:
            self.simulagora_account.set(account_id, 'url', url)
        if token_id is not None:
            self.simulagora_account.set(account_id, 'token_id', token_id)
        if secret is not None:
            self.simulagora_account.set(account_id, 'secret', secret)

    def remove_account(self, account_id):
        """Remove the account ``account_id`` from the config file.
        Does nothing when the account does not exist.
        """
        self.simulagora_account.remove_section(account_id)

    def write_config_file(self, config_filepath=None):
        """Write the account definitions in a config file, which path is
        ``config_filepath`` or the default config path.
        """
        if config_filepath is None:
            config_filepath = self.default_config_filepath
        with open(config_filepath, 'a') as config_file:
            self.simulagora_account.write(config_file)
        os.chmod(config_filepath, stat.S_IREAD | stat.S_IWRITE)

    def account_infos(self, account_id=None):
        """Return the url, token_id, secret of the account ``account_id`` or
        the first one if ``account_id`` was not passed.

        Raises ConfigParser.NoSectionError if no such account was found.
        """
        if account_id is None:
            try:
                account_id = self.simulagora_account.sections()[0]
            except IndexError:
                raise ConfigParser.NoSectionError('no account saved at all')
        return tuple(self.simulagora_account.get(account_id, key)
                     for key in ('url', 'token_id', 'secret'))

    @property
    def accounts(self):
        """Return the list the accounts.
        """
        return self.simulagora_account.sections()


def _compute_md5_as_b64(path):
    """Compute the md5 of the file at `path` and return it b64 encoded.
    """
    md5 = hashlib.md5()
    chunksize = 128 * md5.block_size # pylint: disable=no-member
    with open(path, 'rb') as fdesc:
        for chunk in iter(lambda: fdesc.read(chunksize), ''):
            md5.update(chunk)
    return b64encode(md5.digest())


def _s3_upload_file(fpath, dest_url, form):
    """Upload a file on S3.

    fpath: str
       filepath
    dest_url: str
       Amazon S3 url (e.g. https://s3.amazonaws.com/uploads/EID/)
    form: dict
       Form including authorizations to post (from Simulagora)
    """
    form['Content-MD5'] = _compute_md5_as_b64(fpath)
    parsed_url = urlparse(dest_url)
    fname = osp.basename(fpath)
    form['key'] = parsed_url.path[1:] + '/' + fname + '.0'
    s3_url = '%s://%s' % (parsed_url.scheme, parsed_url.netloc)
    with open(fpath) as fdesc:
        return requests.post(s3_url, data=form, files={'file': ('file', fdesc)})


def _get_s3_base_url(post_form):
    """Return the S3 base_url an upload must be posted to, from the
    authorization form Simulagora delivers for this purpose.
    """
    policy = json.loads(b64decode(post_form['policy']))
    key = 'success_action_redirect'
    for cond in policy['conditions']:
        if isinstance(cond, dict):
            value = cond.get(key)
            if value is not None:
                url = urlparse(value)
                return '://'.join([url.scheme, url.netloc])
    raise ValueError("Policy does not have the key 'success_action_redirect'")


def _todicts(data, *keys):
    """Return the `data` list of list as a list of dict, each value of the inner
    list being the value of the key in `keys` which as the same index.
    """
    return [dict(zip(keys, row)) for row in data]


def doe_parameters(**parameter_descr):
    """Yield the cartesian product of all parameter descriptions passed.

    As an example::
    >>> print list(simulagora.helper_doe(p1=(0.3, 0.4), p2=(12, 17, 18)))
    [{'p2': 12, 'p1': 0.3}, {'p2': 12, 'p1': 0.4},
     {'p2': 17, 'p1': 0.3}, {'p2': 17, 'p1': 0.4},
     {'p2': 18, 'p1': 0.3}, {'p2': 18, 'p1': 0.4}]

    """
    for params in product(*parameter_descr.values()):
        yield dict(zip(parameter_descr.keys(), params))


class Simulagora(cwproxy.CWProxy):
    """Client for the Simulagora web services.
    """

    def __init__(self, account_id=None, account_manager=None, **kwargs):
        """Constructor of the Simulagora class.

        If no argument is given:
            the constructor will search to load the first account from the
            config file

        If the keyword argument 'token_id' is found the contructor will search
        for 'url' and 'secret' for keywords to open a new session on Simulagora
        (a ValueError will be raised if 'secret' or 'url' not found).

        If 'account_id' (positional argument) is found, it will be used as a
        section of the .simulagorarc config file to authenticate against
        Simulagora.

        If 'account_manager' is given, it is used to search the authentication
        data, otherwise, it is created for you and populated with the content of
        your .simulagorarc config file.

        To generate your own .simulagorarc file, see AccountManager class doc.
        """
        if 'token_id' in kwargs:
            token_id = kwargs['token_id']
            try:
                url = kwargs['url']
                secret = kwargs['secret']
            except KeyError, exc:
                raise ValueError('%r arg must be passed along with "token_id"',
                                 exc.args[0])
        else:
            if account_manager is None:
                manager = AccountManager()
                manager.read_config_file()
            url, token_id, secret = manager.account_infos(account_id)
        auth = cwproxy.SignedRequestAuth(token_id, secret)
        super(Simulagora, self).__init__(url, auth=auth)
        self._store_keyring_cache = None

    # Helpers for listing entities

    def studies(self):
        """Get the list of readable studies.
        """
        rql = 'Any SEID, N WHERE X is ProcessingStudy, X eid SEID, X name N'
        return _todicts(self.rql(rql).json(), 'eid', 'name')

    def runs(self, study=None):
        """Display the list of runs.

        Show run eids, name of the executable and the state.
        """
        rql = ('Any R, EXN, RST'
               ' WHERE R is Run, R in_state S, S name RST,'
               ' R executable X, X name EXN')
        if study is not None:
            rql += ', R in_study ST, ST eid %d' % study
        runs = _todicts(self.rql(rql).json(),
                        'eid', 'executable_name', 'state')
        queries = []
        for run in runs:
            args = {'r': run['eid']}
            for parameter_type in ('String', 'Int', 'Float'):
                rql = ('Any PDN,PVV WHERE PV value_of_run R, R eid %%(r)s, '
                       'PV value PVV, PV param_def PD, PD name PDN, '
                       'PV is ParameterValue%s' % parameter_type)
                queries.append((rql, args))
        data = self.rqlio(queries).json()
        for run_index, run in enumerate(runs):
            run_parameters = data[3*run_index:3*(run_index+1)]
            run['input_parameters'] = dict(
                    chain(*run_parameters)) # pylint: disable=star-args
        return runs

    def executables(self):
        """Return the list of available executables.
        """
        query = 'Any X,N WHERE X is Executable, X name N'
        return _todicts(self.rql(query).json(), 'eid', 'name')

    def server_types(self):
        """Return the list of available virtual machines which can be launched.
        """
        rql = ('Any X, N, CPU, RAM, CPNAME '
               'WHERE X is CloudServerType, X name N, X cpu_core_nb CPU, '
               'X ram RAM, X provided_by Y, Y name CPNAME')
        return _todicts(self.rql(rql).json(),
                        'eid', 'name', 'cpu', 'ram', 'cloud provider')

    def images(self):
        """Return the list of available machine images.
        """
        query = 'Any X, T WHERE X is CloudServerImage, X title T'
        return _todicts(self.rql(query).json(), 'eid', 'title')

    @property
    def last_image(self):
        """Return the more recent machine image.
        """
        query = ('Any X, T ORDERBY X DESC LIMIT 1'
                 ' WHERE X is CloudServerImage, X title T')
        return _todicts(self.rql(query).json(), 'eid', 'title')[0]

    def files_in_folder(self, folder):
        """Return a list of dicts describing the files under the folder which
        eid is ``folder``.
        The keys of the dict are: eid, md5_hash, mimetype, name, size, uri.
        """
        query = ('Any X,U,S,H,T WHERE X is DistantFile, X uri U, X size S, '
                 'X md5_hash H, X mimetype T, X filed_under F, F eid %d')
        descrs = _todicts(self.rql(query % folder).json(),
                          'eid', 'uri', 'size', 'md5_hash', 'mimetype')
        for descr in descrs:
            descr['name'] = descr['uri'].rsplit('/')[-1]
        return descrs

    def state(self, eid):
        """Return the current state of a specific Entity. Mostly useful to get
        the state of a run.
        """
        rql = 'Any ST WHERE X eid %d, X in_state S, S name ST' % eid
        return self.rql(rql).json()[0][0]

    # Entity creation (folders, studies, runs) and manipulation

    def _create_single_entity(self, etype, **kwargs):
        """Create an entity of type `etype` and attribute/ relation values
        `kwargs`. Returns its unique identifier (eid).
        """
        query = builders.create_entity(etype, **kwargs)
        resp = self.rqlio([query])
        resp.raise_for_status()
        return resp.json()[-1][0][0]

    def create_folder(self, name):
        """Create a folder which name is the one passed as an argument.
        Return its unique identifier (an integer).
        """
        return self._create_single_entity('Folder', name=name)

    def create_study(self, name):
        """Create a study which name is the one passed as an argument.
        Return its unique identifier (an integer).
        """
        return self._create_single_entity('ProcessingStudy', name=name)

    def create_run(self, in_study, executable, server_type,
                   input_files=None, parameters=None, image=None):
        """Create a run and return its unique identifier (an integer).

        All entities arguments should be pass by there eid (e.g. in_study,
        executable, server_type, image).
        ``input_files`` should be a list of eids.
        ``parameters`` should be a dictionnary (like {'p2': 12, 'p1': 0.3}).
        """
        if parameters is None:
            parameters = {}
        if image is None:
            image = self.last_image['eid']
        param_defs = self.parameter_defs(executable)
        queries = []
        # create run
        rql = ('INSERT Run R:'
               ' R in_study S, R executable E, R store_keyring K,'
               ' R run_on M, R use_image I '
               'WHERE S eid %(s)s, E eid %(e)s, M eid %(m)s, I eid %(i)s,'
               ' K eid %(k)s')
        args = {'k': self._store_keyring,
                's': in_study,
                'e': executable,
                'm': server_type,
                'i': image,
                }
        queries.append((rql, args))
        # attaching files
        if input_files:
            rql = ('SET R input_file F WHERE R eid %%(r)s, F eid IN (%s)'
                   % ', '.join([str(ifile) for ifile in input_files]))
            queries.append((rql, {'r': '__r0'}))
        # insert parameter values
        for name, value in parameters.items():
            pdef = param_defs[name]
            rql = ('INSERT ParameterValue%s P: P param_def PD, P value %%(v)s,'
                   ' P value_of_run R'
                   ' WHERE PD eid %%(pd)s, R eid %%(r)s' % pdef['value_type'])
            queries.append((rql, {'v': value, 'pd': pdef['eid'], 'r': '__r0'}))
        return self.rqlio(queries).json()[0][0][0]

    def start_run(self, run):
        """Start the given Run. Return the unique identifier of the transition
        between the previous and the new state of the run.
        """
        query = [builders.build_trinfo(run, 'wft_run_queue')]
        resp = self.rqlio(query)
        resp.raise_for_status()
        # Eid of the transition.
        eid = resp.json()[-1][0][0]
        return eid

    # High level entity creation helper

    def create_doe(self, study, executable, server_type,
                   parameter_set, input_folder=None):
        """ Create a design of experiment in the given `study`, using
        the given `executable` and the input data from `folder`. The created
        runs will be executed on the given `server_type`.

        All entities arguments (e.g. study, executable, [input_folder],
        server_type) should be pass by there name.

        The executable input parameters will receive the values given in
        a list of dictionnaries `parameter_set`, see helper_doe doc.
        As an example::

        parameter_set = [{'p2': 12, 'p1': 0.3}, {'p2': 12, 'p1': 0.4},
                         {'p2': 17, 'p1': 0.3}, {'p2': 17, 'p1': 0.4},
                         {'p2': 18, 'p1': 0.3}, {'p2': 18, 'p1': 0.4}]
        """
        runs = []
        study = self.find_one('ProcessingStudy', name=study)
        executable = self.find_one('Executable', name=executable)
        server_type = self.find_one('CloudServerType', name=server_type)
        files = None
        if input_folder is not None:
            result = self.rqlio(
                [('Any X WHERE X is DistantFile, X filed_under F, F name %(n)s',
                  {'n': input_folder})]).json()
            files = [row[0] for row in result[0]]
        for params in parameter_set:
            runs.append(
                self.create_run(in_study=study, executable=executable,
                                parameters=params, server_type=server_type,
                                input_files=files))
        return runs

    # Input/ output data file related methods

    def download_results(self, run, dest_path='.'):
        """Download all result files of `run` into `dest_path` (which defaults
        to the current working directory).

        Use log level INFO (at least) to know what file is being downloaded.
        """
        urls = self._ajax_controller('results_url', run).json()
        for url in urls:
            tmp_path = urlparse(url)
            local_filename = '/'.join(tmp_path.path.split('/')[5:])
            try:
                os.makedirs(osp.join(dest_path, osp.dirname(local_filename)))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
            logging.info("downloading %s", local_filename)
            req = requests.get(url, stream=True)
            with open(local_filename, 'wb') as fdesc:
                for chunk in req.iter_content(chunk_size=4096):
                    if chunk: # filter out keep-alive new chunks
                        fdesc.write(chunk)
                        fdesc.flush()

    def upload_files(self, folder, *filepaths):
        """Given the destination `folder` by eid, upload the files which paths
        are passed afterwards into this folder.

        folder: int (None by default)
           The eid of the destination Simulagora Folder.
        filepaths: str or list
           The paths of the files to be uploaded
        """
        # 0. Create an Upload instance
        upload_name = '_'.join([osp.basename(filepaths[0]), 'upload'])
        upload_eid = self._create_upload(upload_name, folder)
        logging.debug("uploading files: upload eid is %s", upload_eid)
        # 1. Get the form to have the permission to POST to S3
        post_form = self._ajax_controller('upload_form', upload_eid).json()
        logging.debug("uploading files: received upload form %s", post_form)
        base_s3_url = _get_s3_base_url(post_form)
        dest_url = base_s3_url + '/uploads/%s' % upload_eid
        # 2. Upload the file to S3
        description = []
        for fpath in filepaths:
            _s3_upload_file(fpath, dest_url, post_form)
            filesize = osp.getsize(fpath)
            description.append({'name': osp.basename(fpath),
                                'total': filesize,
                                'chunks': 1})
        # 3. Post the upload description to Simulagora
        self._ajax_controller('upload_description', upload_eid,
                              description).raise_for_status()
        logging.debug("uploading files: description posted: %s", description)
        # 4. Make the finished upload Simulagora dedicated controller call
        self._ajax_controller('upload_successful',
                              upload_eid).raise_for_status()
        logging.debug("uploading files: upload eid %s successful", upload_eid)

    ## Lower level read-only helpers

    def find(self, etype, **kwargs):
        """This low level request aims at getting the list of unique
        identifiers (integers) of Simulagora entities of type `type` which also
        match the conditions on their attributes described by `kwargs`, of the
        form "attribute_name=attribute_value".
        """
        # XXX to be moved to cwclientlib
        rql = ['Any X WHERE X is %s' % etype]
        args = {}
        for key, value in kwargs.items():
            if isinstance(value, dict) and 'eid' in value:
                value = value['eid']
            args[key] = value
            rql.append('X %s %%(%s)s' % (key, key))
        rql = ','.join(rql)
        result = self.rqlio([(rql, args)]).json()
        return result[0]

    def find_one(self, etype, **kwargs):
        """This low level request aims at getting the unique identifier
        (an integers) of a single Simulagora entity of type `type` supposed to
        match the conditions on its attributes described by `kwargs` (of the
        form "attribute_name=attribute_value").

        An AssertionError is raised if the number of entities found is not
        exactly 1.
        """
        # XXX to be moved to cwclientlib
        data = self.find(etype, **kwargs)
        assert len(data) != 0, 'no such entity found in the database'
        assert len(data) == 1, ('more than one entity matches your request '
                                '(%d found)' % len(data))
        return data[0][0]

    def parameter_defs(self, executable):
        """Return a dictionary describing the input and output parameters of
        `executable`. The keys of the dictionary are the parameter names, the
        value being itself a dictionary with keys:

        - eid: unique identifier of the parameter definition itself
        - name: the name of the parameter
        - value_type: the type (int, float, string) of the values that the
          parameter can take
        - param_type: the type (input, output) of the parameter
        - description: the textual description of the parameter
        """
        rql = ('Any P,N,VT,PT,D WHERE E is Executable, E eid %d, '
               'P parameter_of E, P name N, P value_type VT, '
               'P param_type PT, P description D') % executable
        result = self.rql(rql)
        result.raise_for_status()
        pdefs = _todicts(result.json(), 'eid', 'name', 'value_type',
                         'param_type', 'description')
        return dict((pdef['name'], pdef) for pdef in pdefs)

    ## Internal helpers: do not use, they can disappear or change!

    @property
    def _store_keyring(self):
        """Cached helper that returns the CloudStoreKeyring first instance.
        """
        if self._store_keyring_cache is None:
            self._store_keyring_cache = self.rql(
                'Any X WHERE X is CloudStoreKeyring').json()[0][0]
        return self._store_keyring_cache

    def _create_upload(self, name, folder):
        """Create an Upload entity with name `name` which files will be filed
        under folder `folder`. Return the eid of the new Upload entity.
        """
        queries = [('INSERT Upload U: U name %(name)s, U upload_folder F,'
                    ' U keyring K WHERE K eid %(k)s, F eid %(f)s',
                    {'name': name, 'k': self._store_keyring, 'f': folder})]
        rset = self.rqlio(queries).json()[0]
        if not rset:
            raise ValueError('Upload creation failed. Are you sure folder id %r'
                             ' really exists ?' % folder)
        return rset[0][0]

    def _ajax_controller(self, fname, *args):
        """Helper to call an ajax function named `fname` with arguments `args`.
        """
        params = {'url': self.base_url + '/ajax',
                  'headers': cwproxy.build_request_headers(),
                  'verify': self._ssl_verify,
                  'auth': self.auth,
                  'data': {'fname': fname,
                           'arg': [json.dumps(x) for x in args]}}
        return requests.post(**params) # pylint: disable=star-args
