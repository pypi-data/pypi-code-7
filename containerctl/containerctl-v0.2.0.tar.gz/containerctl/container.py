"""Manage containers."""
import os
import pystache
import re
import subprocess
import yaml
from .errors import ConfigError, ContainerError, TestError
from .tools import Tool
from .version import Version, get_best_version, get_all_versions, latest as latest_version

config_defaults = {
    'user': None,
    'name': None,
    'prebuild': None,
    'path': None,
    'running': None,
    'testing': None,
}


def first_file(path, filenames):
    """Returns the first file from `filenames` with read access found in `path`."""
    for filename in filenames:
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
            return filepath
    return None


def read_config(configfile):
    """
    Return container configuration from a file. See `Container.from_path` for a description of the
    config file syntax.
    """
    try:
        with open(configfile) as f:
            filedata = yaml.load(f)
    except IOError as e:
        raise ConfigError("failed to open '{}': {}".format(configfile, e))
    except yaml.YAMLError as e:
        raise ConfigError("failed to parse '{}': {}".format(configfile, e))
    if not isinstance(filedata, dict):
        raise ConfigError("failed to parse '{}': contains invalid data".format(configfile))

    config = config_defaults.copy()
    config.update(filedata)

    name = config['name']
    if not name:
        raise ConfigError("name is empty or missing")
    if not isinstance(name, (str, unicode)):
        raise ConfigError("name must be a string")
    if '/' in name:
        config['user'], config['name'] = name.split('/', 1)

    for key in ('user', 'prebuild', 'path'):
        if config[key] is not None and not isinstance(config[key], (str, unicode)):
            raise ConfigError("{} must be a string".format(key))

    if config['running'] is not None and not isinstance(config['running'], dict):
        raise ConfigError("running must be a dictionary")
    if config['testing'] is not None and not isinstance(config['testing'], dict):
        raise ConfigError("testing must be a dictionary")

    return config


class Container(object):
    """Manage a container."""

    @classmethod
    def from_path(cls, path=None, verify=None, **override):
        """
        Return a container found at the provided directory `path`. Expects a container config file
        to exist in `path`. If `path` is `None` (the default) the output of `os.getcwd()` will be
        used for `path`. Verification may be enabled by setting `verify` to `True`. Verification
        causes only verified versions to be built or pushed. Most methods and properties will raise
        a `ContainerError` if called with verification enabled when not verified version is
        present.

        The container config file must be named `container.yml` or `.container.yml`. The first
        readable file found, in that order, is used. The config file must contain valid YAML. Valid
        keys are:

        * `path` - The path to the directory containing that container's Dockerfile and other
            configuration. This is set to the `path` value determined by this function if absent
            from the config file.
        * `user` - The user part of the container's full tag.
        * `name` - The name part of the container's full tag. If this value contains a `/` it will
            be stripped of the string up to and including the `/`. The `user` value will be set to
            the stripped portion exclufing the `/`. This will override any value explicitly set in
            `user`.
        * `prebuild` - A script to run before calling `docker build` on the container.
        * `running` - A fig cofiguration to use when running the container.
        * `testing` - Additional fig configuration to use when testing the container. A `test`
            container must exist for the test command to run.

        The `prebuild`, `running`, and `testing` values may have values substituted using the
        Mustache template syntax. Valid substitutions are `name`, `user`, `version`, and `tag`.

        An example may look like this:

            name: nginx
            prebuild: ./prebuild {{version}}
            running:
                site:
                    image: example/site
                nginx:
                    image: {{tag}}
                    ports:
                    - 80
                    volumes_from:
                    - site
            testing:
                test:
                    build: tests
                    links:
                    - nginx:www.example.net

        Config values may be passed as keyword arguments. In this case they override the values
        provided in the config file.

        A `ConfigError is raised if: `path` is not a directory; a single container configuration is
        expected and zero or more than one are found; no config file is found; or the config file
        is invalid.

        A `ContainerError` may be raised by `__init__` which is called in this method.
        """
        if path is None:
            path = os.getcwd()
        if not os.path.isdir(path):
            raise ConfigError("path '{}' is not a directory".format(path))

        configfile = first_file(path, ('container.yml', '.container.yml'))
        if not configfile:
            raise ConfigError("config file not found")

        config = read_config(configfile)
        if config.get('path') is None:
            config['path'] = path
        if 'version' in config:
            # manually defined verions are assumed to be verified
            config['version'] = Version(config['version'], True)
        config.update(override)
        config['verify'] = verify
        return cls.from_dict(config)

    @classmethod
    def from_dict(cls, data):
        """Build a container object from a dictionary."""
        return cls(
            data.get('path'),
            data.get('user'),
            data.get('name'),
            data.get('version'),
            data.get('verify'),
            data.get('prebuild'),
            data.get('running'),
            data.get('testing'),
        )

    def __init__(self, path, user, name, version=None, verify=None, prebuild=None,
                 running=None, testing=None):
        """
        Initialize the container. The `path` should be a directory containing the container's
        Dockerfile. The `user` and `name` is combined to create the image repo. The `name` should
        match the directory containing the container's Dockerfile.

        The `version` value is used to tag the container on build. If `version` is `None` the
        version will be detected using `containerctl.version` module. If `verify` is set to `True`
        then only verified versions will be used to tag the container. If no verified versions are
        present then a `ContainerError` will be raised when building or pushing.

        The `prebuild` param is a command to run before calling `docker build` on the container. If
        `prebuild` is `None` and an executable file called `prebuild` exists in `path` it will be
        executed as the prebuild script.

        If the `running` param is provided it will be written as YAML to be used as the fig
        configuration when running this container. Otherwise a very simple fig.yml file will be
        written to execute the container.

        If the `testing` param is provided it be used to update the `running` value when the test
        command is called. The test command requires that a container named `test` exists in the
        `testing` section.
        """
        def aslist(val):
            if isinstance(val, (list, tuple)):
                return list(val)
            return [val]

        if not name:
            raise ContainerError("container name must not be empty")
        if not os.path.isdir(path):
            raise ContainerError("container {} has invalid path '{}'".format(name, path))

        self.path = os.path.abspath(path)
        self.user = user
        self.name = name

        self.verify = verify
        self._version = version
        self._prebuild = prebuild
        self._running = running
        self._testing = testing

        fig_project = (self.user or '') + self.name
        self._fig_config = os.path.join(self.path, 'fig.yml')

        self._fig = Tool('fig', '-p', fig_project, '-f', self._fig_config, cwd=self.path)
        self._fig_remove = self._fig('rm', '--force', '-v')
        self._docker = Tool('docker', cwd=self.path)

        # some CI systems do not allow image removal
        self.allow_remove = True
        if os.getenv('CIRCLECI', None):
            self.allow_remove = False

    def _format(self, value):
        """
        Format a string value with the `user`, `name`, `version`, and `tag`. Keyword args may be
        provided to override these values or add additonal values for substitution.

        Some simple filters are available for each value. These can be given by appending the value
        name with '|filter' where filter is the name of the filter. These filters currently exist:

            fig - Convert the value into a name suitable for a fig container.
        """
        if not value:
            return ''

        patterns = [
            ('fig', re.compile(r'[^a-zA-Z0-9]'), ''),
        ]

        context = {
            'user': self.user or '',
            'name': self.name or '',
            'version': self.version.value if self.version else '',
            'tag': self.tag,
        }

        for pname, pmatch, psub in patterns:
            for key, item in context.items():
                item = pmatch.sub(psub, item)
                context[key + '|' + pname] = item
        return pystache.render(value, context)

    def _get_prebuild(self):
        """Return the prebuild command."""
        if self._prebuild:
            return self._format(self._prebuild)
        else:
            cmd = os.path.join(self.path, 'prebuild')
            if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
                return cmd
        return None

    def _get_fig_cfg(self, test):
        """Return the formatted fig configuration."""
        fig = self._running
        if not fig:
            name = self._format('{{name|fig}}')
            fig = {
                name: {
                    'image': '{{tag}}',
                }
            }

        if test and self._testing:
            fig.update(self._testing)

        def fmt(data):
            res = {}
            for k, v in data.iteritems():
                if isinstance(v, (str, unicode)):
                    res[k] = self._format(v)
                elif isinstance(v, dict):
                    res[k] = fmt(v)
                else:
                    res[k] = v
            return res
        return fmt(fig)

    def _write_fig_cfg(self, test):
        """Write the fig configuration to `fig.yml`."""
        configfile = os.path.join(self.path, 'fig.yml')
        try:
            with open(configfile, 'w') as f:
                fig = self._get_fig_cfg(test)
                f.write(yaml.safe_dump(fig, explicit_start=False, default_flow_style=False))
        except IOError:
            raise ContainerError("unable to write to '{}'".format(configfile))
        except yaml.YAMLError as e:
            raise ContainerError("failed to encode config: {}", e)

    def _get_tag(self, version):
        """Return the tag for a particular version."""
        tag = self.name
        if self.user:
            tag = '/'.join((self.user, tag))
        if version:
            tag = ':'.join((tag, version.value))
        return tag

    def to_dict(self, raw=False):
        """
        Return the container as a dictionary. If `raw` is `True` then the un-evaluated
        configuraiton is returned.
        """
        def rel(base, path):
            if path and path.startswith(base):
                path = '.' + path[len(base):]
            return path

        cwd = os.getcwd()
        if raw:
            data = {'name': self.name}
            if self.user:
                data['user'] = self.user
            if self.verify:
                data['verify'] = self.verify
            if self._version:
                data['version'] = self._version.value
            if self._prebuild:
                data['prebuild'] = self._prebuild
            if self._running:
                data['running'] = self._running
            if self._testing:
                data['testing'] = self._testing

            path = rel(cwd, self.path)
            if path and path != '.':
                data['path'] = path
        else:
            version = self.version
            versions = self.versions
            data = {
                'tag': self.tag,
                'tags': {self._get_tag(v): v.verified for v in versions},
                'user': self.user,
                'name': self.name,
                'verify': self.verify,
                'version': self.version.value if version else None,
                'versions': {v.value: v.verified for v in versions},
                'running': self._get_fig_cfg(False),
                'testing': self._get_fig_cfg(True),
                'is-built': self.is_built(),
                'is-running': self.is_running(),
                'is-verified': self.is_verified(),
            }
            path = rel(cwd, self.path)
            if path and path != '.':
                data['path'] = path
            prebuild = rel(cwd, self._get_prebuild())
            if prebuild and prebuild != '.':
                data['prebuild'] = prebuild
        return data

    @property
    def version(self):
        """
        Return the best version for the container or `None` if unable to detect any version.
        Executes version detection if not explicitly defined in the constructor. Raises
        `VersionError` on detection failure.
        """
        if self._version:
            return self._version
        return get_best_version(self, self.verify)

    @property
    def versions(self):
        """
        Return all available versions of the container. Executes version detection if the version
        is not explicitly defined in the constructor. Raises `VersionError` on detection
        failure.
        """
        if self._version:
            return [self._version]
        versions = get_all_versions(self)
        if self.verify:
            versions = filter(lambda v: v.verified, versions)
        return list(versions)

    @property
    def tag(self):
        """Return the full container tag. This is tagged with the 'best' version."""
        return self._get_tag(self.version)

    @property
    def tags(self):
        """Return a list of all container tags."""
        return [self._get_tag(v) for v in self.versions]

    @property
    def dockerfile(self):
        """Return the expected path to the Dockerfile for this container."""
        return os.path.join(self.path, 'Dockerfile')

    def is_built(self):
        """
        Return True if the container has been built previously. This does not guarantee that the
        existing image is up to date.
        """
        try:
            built = True
            docker_inspect = self._docker('inspect')
            for tag in self.tags:
                built = built and docker_inspect(tag).quiet(True) == 0
            return built
        except OSError:
            msg = "{} build check failed: docker command is not available"
            raise ContainerError(msg.format(self.tag))

    def is_running(self):
        """Return True if the container is running."""
        if not os.path.isfile(self._fig_config):
            return False

        try:
            out, _, exitcode = self._fig('ps', '-q').capture()
        except OSError as e:
            msg = "{} running check failed: {}"
            raise ContainerError(msg.format(self.tag, e))

        if exitcode != 0:
            msg = "{} running check failed: fig returned non-zero exit code"
            raise ContainerError(msg.format(self.tag))
        if out.strip():
            return True
        return False

    def is_verified(self):
        """Return True if this version of the container is verified."""
        version = self.version
        return version and version.verified

    def prebuild(self):
        """Execute container prebuild step."""
        cmd = self._get_prebuild()
        if not cmd:
            return

        env = os.environ.copy()
        env = env.update({
            'CONTAINER_PATH': self.path,
            'CONTAINER_USER': self.user,
            'CONTAINER_NAME': self.name,
            'CONTAINER_VERSION': self.version,
            'CONTAINER_TAG': self.tag,
        })

        try:
            subprocess.check_call(["bash", "-c", cmd], cwd=self.path, env=env)
        except subprocess.CalledProcessError:
            msg = "{} prebuild failed: command returned non-zero exit code"
            raise ContainerError(msg.format(self.tag))
        except OSError:  # pragma: no cover
            msg = "{} prebuild failed: command is not available"
            raise ContainerError(msg.format(self.tag))

    def build(self, prebuild=None, nocache=None, latest=None):
        """
        Build the container. If `prebuild` is `True` (the default) the container's prebuild scripts
        are run. The Docker cache may be invalidated prior to the build by setting `nocache` to
        `True`. The image will be tagged with each version output by `versions`. It may also be
        tagged as 'latest' by setting `latest` to `True`.

        Raises `ContainerError` on failure. Failures include:
        - No Dockerfile.
        - Unverified version when `verify` is `True`.
        - Call to `docker build` fails.
        - The `docker` command is not found.

        Return a list of built tags.
        """
        if prebuild is None:
            prebuild = True
        if nocache is None:
            nocache = False

        if not os.path.exists(self.dockerfile):
            raise ContainerError("{} build failed: no Dockerfile".format(self.tag))
        if self.verify and not self.is_verified():
            raise ContainerError("{} build failed: not verified".format(self.tag))

        tags = self.tags
        if latest:
            tags.append(self._get_tag(latest_version))
        if not tags:
            raise ContainerError("{} build failed: no tags to build".format(self.tag))
        image = tags.pop()

        if prebuild:
            self.prebuild()

        docker_build = self._docker('build')
        if self.allow_remove:
            docker_build = docker_build('--rm', '--force-rm')
        if nocache:
            docker_build = docker_build('--no-cache')

        try:
            if docker_build('-t', image, '.').call() != 0:
                msg = "{} build failed: docker build returned non-zero exit code"
                raise ContainerError(msg.format(self.tag))

            docker_tag = self._docker('tag', image)
            for tag in tags:
                if docker_tag(tag).call() != 0:
                    msg = "{} build failed: docker tag returned non-zero exit code"
                    raise ContainerError(msg.format(self.tag))
            return tags + [image]
        except OSError as e:
            msg = "{} build failed: {}"
            raise ContainerError(msg.format(self.tag, e))

    def push(self, latest=None):
        """
        Push the built container to its registry. Also push the 'latest' tag if `latest` is
        True. Return a list of pushed tags.
        """
        if self.verify and not self.is_verified():
            raise ContainerError("{} push failed: not verified".format(self.tag))
        if not self.is_built():
            raise ContainerError("{} push failed: image not built".format(self.tag))

        tags = self.tags
        if latest:
            tags.append(self._get_tag(latest_version))
        if not tags:
            raise ContainerError("{} push failed: no tags to push".format(self.tag))

        try:
            docker_push = self._docker('push')
            for tag in tags:
                if docker_push(tag).call() != 0:
                    msg = "{} push failed: docker returned non-zero exit code"
                    raise ContainerError(msg.format(self.tag))
            return tags
        except OSError as e:
            msg = "{} push failed: {}"
            raise ContainerError(msg.format(self.tag, e))

    def remove(self, latest=None):
        """
        Remove the container from docker. If `latest` is `True` also remove the container tagged as
        'latest'. Return a list of two-tuples containing the tag name and `True` if removed. Raise
        a `ContainerError` if the docker command is missing.
        """
        tags = self.tags
        if latest:
            tags.append(self._get_tag(latest_version))

        removed = []
        try:
            docker_rmi = self._docker('rmi')
            for tag in tags:
                exitcode = docker_rmi(tag).call()
                removed.append((tag, exitcode == 0))
            return removed
        except OSError as e:
            msg = "{} remove failed: {}"
            raise ContainerError(msg.format(self.tag, e))

    def run(self, detach=None):
        """
        Run the container. Calls `fig up` to start the container and its dependencies. After
        running the containers are removed using `fig rm`. If `detach` is set to `True` then the
        containers will be run in the background.  They must be stopped by calling `kill` for the
        `fig rm` cleanup to take place.
        """
        if self.verify and not self.is_verified():
            raise ContainerError("{} run failed: not verified".format(self.tag))

        self._write_fig_cfg(False)
        fig_up = self._fig('up')
        if detach:
            fig_up = fig_up('-d')

        try:
            try:
                if fig_up.call() != 0:
                    msg = "{} run failed: fig returned non-zero exit code"
                    raise ContainerError(msg.format(self.tag))
            finally:
                if not detach and self.allow_remove:
                    self._fig_remove.quiet()
        except OSError as e:
            msg = "{} run failed: {}"
            raise ContainerError(msg.format(self.tag, e))

    def kill(self):
        """
        Kill the running container. Calls `fig kill` to stop the container and its dependencies.
        Once stopped a `fig rm` is issued to clean up the stopped containers.
        """
        try:
            try:
                if self._fig('kill').call() != 0:
                    msg = "{} kill failed: fig returned non-zero exit code"
                    raise ContainerError(msg.format(self.tag))
            finally:
                if self.allow_remove:
                    self._fig_remove.quiet()
        except OSError as e:
            msg = "{} kill failed: {}"
            raise ContainerError(msg.format(self.tag, e))

    def test(self, rebuild=None):
        """
        Run the test container. If `rebuild` is `True` the test container will be rebuilt before
        running.

        Raise `TestError` if the test has an exit code other then 0. Raise ContainerError on all
        other failures.
        """
        config = self._get_fig_cfg(True)
        if 'test' not in config:
            msg = "{} test failed: no test container"
            raise ContainerError(msg.format(self.tag))

        self._write_fig_cfg(True)
        services = set(config.keys()) - set(['test'])

        try:
            # rebuild the test container if requested
            if rebuild and 'build' in config['test']:
                if self._fig('build', 'test').call() != 0:
                    msg = "{} test failed: failed to rebuild test container"
                    raise ContainerError(msg.format(self.tag))

            try:
                # bring up all available services
                if self._fig('up', '-d', *services).call() != 0:
                    msg = "{} test failed: failed to start dependencies"
                    raise ContainerError(msg.format(self.tag))

                # run the test container
                fig_run = self._fig('run')
                if self.allow_remove:
                    fig_run = fig_run('--rm')
                exitcode = fig_run('test').call()
                if exitcode != 0:
                    msg = "{} test failed: returned non-zero exit code {}"
                    raise TestError(msg.format(self.tag, exitcode), exitcode)
            finally:
                self._fig('kill').call()
                if self.allow_remove:
                    self._fig_remove.quiet()
        except OSError as e:
            msg = "{} test failed: {}"
            raise ContainerError(msg.format(self.tag, e))
