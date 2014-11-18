from __future__ import print_function
import re
import datetime
import json
import os
import urlparse
import ssl

from tabulate import tabulate
import tutum
from dateutil import tz
import ago
import docker
import requests
from tutumcli.exceptions import NonUniqueIdentifier, ObjectNotFound, BadParameter, DockerNotFound
from exceptions import StreamOutputError

from . import __version__


def tabulate_result(data_list, headers):
    print(tabulate(data_list, headers, stralign="left", tablefmt="plain"))


def from_utc_string_to_utc_datetime(utc_datetime_string):
    if not utc_datetime_string:
        return None
    utc_date_object = datetime.datetime.strptime(utc_datetime_string, "%a, %d %b %Y %H:%M:%S +0000")

    return utc_date_object


def get_humanize_local_datetime_from_utc_datetime_string(utc_datetime_string):
    def get_humanize_local_datetime_from_utc_datetime(utc_target_datetime):
        local_now = datetime.datetime.now(tz.tzlocal())
        if utc_target_datetime:
            local_target_datetime = utc_target_datetime.replace(tzinfo=tz.gettz("UTC")).astimezone(tz=tz.tzlocal())
            return ago.human(local_now - local_target_datetime, precision=1)
        return ""

    utc_target_datetime = from_utc_string_to_utc_datetime(utc_datetime_string)
    return get_humanize_local_datetime_from_utc_datetime(utc_target_datetime)


def is_uuid4(identifier):
    uuid4_regexp = re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}', re.I)
    match = uuid4_regexp.match(identifier)
    return bool(match)


def add_unicode_symbol_to_state(state):
    if state in ["Running", "Partly running", "Deployed"]:
        return u"\u25B6 " + state
    elif state in ["Init", "Stopped"]:
        return u"\u25FC " + state
    elif state in ["Starting", "Stopping", "Scaling", "Terminating", "Deploying"]:
        return u"\u2699 " + state
    elif state in ["Start failed", "Stopped with errors"]:
        return u"\u0021 " + state
    elif state == "Terminated":
        return u"\u2718 " + state
    return state


def get_docker_client():
    try:
        DOCKER_TLS_VERIFY = bool(os.environ.get('DOCKER_TLS_VERIFY', False))

        if not DOCKER_TLS_VERIFY:
            tls_config = False
        else:
            cert_path = os.environ.get('DOCKER_CERT_PATH')
            if cert_path:
                ca_cert_path = os.path.join(cert_path, "ca.pem")
                client_cert = (os.path.join(cert_path, "cert.pem"), os.path.join(cert_path, "key.pem"))
                tls_config = docker.tls.TLSConfig(
                    ssl_version=ssl.PROTOCOL_TLSv1,
                    client_cert=client_cert,
                    verify=ca_cert_path,
                    assert_hostname=False)
            else:
                tls_config = False

        base_url = os.getenv("DOCKER_HOST")
        if tls_config and base_url.startswith("tcp://"):
            base_url = base_url.replace("tcp://", "https://")

        docker_client = docker.Client(base_url=base_url, tls=tls_config)
        docker_client.version()
        return docker_client
    except Exception as e:
        raise DockerNotFound("Cannot connect to docker (is it running?)")


def build_dockerfile(filepath, ports, command):
    with open(filepath, "w") as dockerfile:
        base_image = "FROM tutum/buildstep\n\n"
        expose_ports = " ".join(["EXPOSE", ports]) + "\n\n" if ports else ""
        if isinstance(command, list):
            command = ','.join(command)
            command = '[%s]' % command
        cmd = " ".join(["CMD", command])

        for line in [base_image, expose_ports, cmd]:
            if line:
                dockerfile.write(line)


def stream_output(output, stream):
    def print_output_event(event, stream, is_terminal):
        if 'errorDetail' in event:
            raise StreamOutputError(event['errorDetail']['message'])

        terminator = ''

        if is_terminal and 'stream' not in event:
            # erase current line
            stream.write("%c[2K\r" % 27)
            terminator = "\r"
            pass
        elif 'progressDetail' in event:
            return

        if 'time' in event:
            stream.write("[%s] " % event['time'])

        if 'id' in event:
            stream.write("%s: " % event['id'])

        if 'from' in event:
            stream.write("(from %s) " % event['from'])

        status = event.get('status', '')

        if 'progress' in event:
            stream.write("%s %s%s" % (status, event['progress'], terminator))
        elif 'progressDetail' in event:
            detail = event['progressDetail']
            if 'current' in detail:
                percentage = float(detail['current']) / float(detail['total']) * 100
                stream.write('%s (%.1f%%)%s' % (status, percentage, terminator))
            else:
                stream.write('%s%s' % (status, terminator))
        elif 'stream' in event:
            stream.write("%s%s" % (event['stream'], terminator))
        else:
            stream.write("%s%s\n" % (status, terminator))

    is_terminal = hasattr(stream, 'fileno') and os.isatty(stream.fileno())
    all_events = []
    lines = {}
    diff = 0

    for chunk in output:
        event = json.loads(chunk)
        all_events.append(event)

        if 'progress' in event or 'progressDetail' in event:
            image_id = event['id']

            if image_id in lines:
                diff = len(lines) - lines[image_id]
            else:
                lines[image_id] = len(lines)
                stream.write("\n")
                diff = 0

            if is_terminal:
                # move cursor up `diff` rows
                stream.write("%c[%dA" % (27, diff))

        print_output_event(event, stream, is_terminal)

        if 'id' in event and is_terminal:
            # move cursor back down
            stream.write("%c[%dB" % (27, diff))

        stream.flush()

    return all_events


def fetch_remote_container(identifier, raise_exceptions=True):
    try:
        if is_uuid4(identifier):
            try:
                return tutum.Container.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find a container with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.Container.list(uuid__startswith=identifier) or \
                                      tutum.Container.list(unique_name=identifier)
            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find a container with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one container has the same identifier, please use the long uuid")

    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
            return e
        raise e


def fetch_remote_service(identifier, raise_exceptions=True):
    try:
        if is_uuid4(identifier):
            try:
                return tutum.Service.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find a service with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.Service.list(uuid__startswith=identifier) or \
                                      tutum.Service.list(unique_name=identifier)

            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find a service with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one service has the same identifier, please use the long uuid")
    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
            return e
        raise e


def fetch_remote_node(identifier, raise_exceptions=True):
    try:
        if is_uuid4(identifier):
            try:
                return tutum.Node.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find a node with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.Node.list(uuid__startswith=identifier)
            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find a node with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one node has the same identifier, please use the long uuid")

    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
            return e
        raise e


def fetch_remote_nodecluster(identifier, raise_exceptions=True):
    try:
        if is_uuid4(identifier):
            try:
                return tutum.NodeCluster.fetch(identifier)
            except Exception:
                raise ObjectNotFound("Cannot find a node cluster with the identifier '%s'" % identifier)
        else:
            objects_same_identifier = tutum.NodeCluster.list(uuid__startswith=identifier) or \
                                      tutum.NodeCluster.list(name=identifier)
            if len(objects_same_identifier) == 1:
                return objects_same_identifier[0]
            elif len(objects_same_identifier) == 0:
                raise ObjectNotFound("Cannot find a node cluster with the identifier '%s'" % identifier)
            raise NonUniqueIdentifier("More than one node cluster has the same identifier, please use the long uuid")

    except (NonUniqueIdentifier, ObjectNotFound) as e:
        if not raise_exceptions:
            return e
        raise e


def parse_links(links, target):
    def _format_link(_link):
        link_regexp = re.compile('^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+$')
        match = link_regexp.match(_link)
        if match:
            temp = _link.split(":", 1)
            return {target: temp[0], 'name': temp[1]}
        raise BadParameter("Link variable argument %s does not match with (name:alias)."
                           " Example: mysql:db" % _link)

    return [_format_link(link) for link in links] if links else []


def parse_published_ports(port_list):
    def _get_port_dict(_port):
        port_regexp = re.compile('^([0-9]{1,5}:)?([0-9]{1,5})(/tcp|/udp)?$')
        match = port_regexp.match(_port)
        if bool(match):
            outer_port = match.group(1)
            inner_port = match.group(2)
            protocol = match.group(3)
            if protocol is None:
                protocol = "tcp"
            else:
                protocol = protocol[1:]

            port_spec = {'protocol': protocol, 'inner_port': inner_port, 'published': True}

            if outer_port is not None:
                port_spec['outer_port'] = outer_port[:-1]
            return port_spec
        raise BadParameter("publish port %s does not match with '[host_port:]container_port[/protocol]'."
                           " E.g: 80:80/tcp" % _port)

    parsed_ports = []
    if port_list is not None:
        parsed_ports = []
        for port in port_list:
            parsed_ports.append(_get_port_dict(port))
    return parsed_ports


def parse_exposed_ports(port_list):
    def _get_port_dict(_port):
        if isinstance(_port, int) and 0 <= _port < 65535:
            port_spec = {'protocol': 'tcp', 'inner_port': '%d' % _port, 'published': False}
            return port_spec
        raise BadParameter("expose port %s is not a valid port number" % _port)

    parsed_ports = []
    if port_list is not None:
        parsed_ports = []
        for port in port_list:
            parsed_ports.append(_get_port_dict(port))
    return parsed_ports


def parse_envvars(envvar_list):
    def _is_envvar(_envvar):
        envvar_regexp = re.compile('^[a-zA-Z_]+[a-zA-Z0-9_]*=[^?!=]+$')
        match = envvar_regexp.match(_envvar)
        if bool(match):
            _envvar = _envvar.split("=", 1)
            return {'key': _envvar[0], 'value': _envvar[1]}
        raise BadParameter("Environment Variable argument %s does not match with 'KEY=VALUE'."
                           " Example: ENVVAR=foo" % _envvar)

    parsed_envvars = []
    if envvar_list is not None:
        for envvar in envvar_list:
            parsed_envvars.append(_is_envvar(envvar))
    return parsed_envvars


def try_register(username, password):
    email = raw_input("Email: ")

    headers = {"Content-Type": "application/json", "User-Agent": "tutum/%s" % __version__}
    data = {'username': username, "password1": password, "password2": password, "email": email}

    try:
        r = requests.post(urlparse.urljoin(tutum.base_url, "register/"), data=json.dumps(data), headers=headers)
        if r.status_code == 201:
            return True, "Account created. Please check your email for activation instructions."
        elif r.status_code == 429:
            return False, "Too many retries. Please login again later."
        else:
            messages = r.json()['register']
            if isinstance(messages, dict):
                _text = []
                for key in messages.keys():
                    _text.append("%s: %s" % (key, '\n'.join(messages[key])))
                _text = '\n'.join(_text)
            else:
                _text = messages
            return False, _text
    except Exception:
        return False, r.text

