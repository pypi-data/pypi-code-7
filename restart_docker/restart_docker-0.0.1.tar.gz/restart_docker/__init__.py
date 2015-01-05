#!/usr/bin/python3

import docker
import json
import logging
import sys

client = docker.Client()


# The original function is broken for our use case because it doesn't
# transmit the docker credentials when trying to ping the secure site.
def fixed_expand_registry_url(hostname, insecure=False):
    if hostname.startswith('http:') or hostname.startswith('https:'):
        return hostname
    if docker.utils.ping('https://' + hostname + '/v1/_ping'):
        return 'https://' + hostname
    elif insecure:
        return 'http://' + hostname
    else:
        return 'https://' + hostname
        raise errors.DockerException(
            "HTTPS endpoint unresponsive and insecure mode isn't enabled."
        )


docker.auth.auth.expand_registry_url = fixed_expand_registry_url


def resolve_binding(value):
    parts = value.split(':')
    if 1 == len(parts):
        return parts
    else:
        return (parts[0], parts[1])


class ContainerDescriptor:
    def __init__(self, filename, image_tag):
        self.image_tag = image_tag
        with open(filename, 'r') as file:
            config = json.load(file)
            self.container_name = config['container_name']
            self.image_name = config['image_name']
            self.environment = config.get('environment', {})
            self.ports = config.get('ports', {})

            logging.info("Configuration:")
            logging.info("    Filename: %s" % filename)
            logging.info("")
            logging.info("    Image Name: %s" % self.image_name)
            logging.info("    Image Tag: %s" % self.image_tag)
            logging.info("")
            logging.info("    Container Name: %s" % self.container_name)
            if self.environment:
                logging.info("    Environment:")
                for key in self.environment:
                    logging.info("        %s" % key)
            if self.ports:
                logging.info("    Ports:")
                for key in self.ports:
                    logging.info("        %s -> %s" % (self.ports[key], key))

    def create(self):
        logging.info("Creating container %s." % self.container_name)
        client.create_container(self.get_image_id(), detach=True,
                                environment=self.environment, tty=True,
                                name=self.container_name,
                                ports=list(self.ports.keys()))

    def destroy(self):
        client.remove_container(self.get_container_id(), force=True)

    def exists(self):
        try:
            self.get_container_id()
            return True
        except IndexError:
            return False

    def get_container_id(self):
        value = '/%s' % self.container_name
        containers = client.containers(all=True)
        for container in containers:
            for cname in container['Names']:
                if value == cname:
                    return container['Id']
        raise IndexError("Container %s not found." % self.container_name)

    def get_image_id(self):
        value = '%s:%s' % (self.image_name, self.image_tag)
        images = client.images(self.image_name)
        for image in images:
            for tag in image['RepoTags']:
                if tag == value:
                    return image['Id']
        raise IndexError("Image %s not found." % value)

    def outdated(self):
        inspect = client.inspect_container(self.get_container_id())
        if not inspect['Image'] == self.get_image_id():
            return True
        for key in self.environment:
            equality = "%s=%s" % (key, self.environment[key])
            if equality not in inspect['Config']['Env']:
                return True
        return False

    def start(self):
        logging.info("Starting container %s." % self.container_name)
        port_bindings = {k: resolve_binding(self.ports[k]) for k in self.ports}
        result = client.start(self.get_container_id(),
                              port_bindings=port_bindings,
                              restart_policy='always')

    def update(self):
        failed = False
        status = client.pull(self.image_name, tag=self.image_tag, stream=True)
        for line in status:
            event = json.loads(line.decode('UTF-8'))
            if 'error' in event:
                logging.error(event['error'])
                failed = True
            else:
                logging.info(event['status'])
        if failed:
            raise Exception(
                'Failed to update image: %s:%s' %
                (self.image_name, self.image_tag))


def main():
    logging.basicConfig(level=logging.INFO)

    if 3 != len(sys.argv):
        logging.error("Usage: %s <filename> <tag>" % sys.argv[0])
        exit(-1)

    cd = ContainerDescriptor(sys.argv[1], sys.argv[2])

    cd.update()

    if not cd.exists():
        cd.create()
        cd.start()
    elif cd.outdated():
        cd.destroy()
        cd.create()
        cd.start()
    else:
        logging.warning("Container up to date. Nothing to do.")
