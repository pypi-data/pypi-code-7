from client import ApiClient


class QuantGoAPIClient(object):
    """QuantGo user API client class. To initialize it you need to pass your
    access key and secret key. To retrieve these keys go to QuantGo console
    Query API Keys tab.

    :Example:

    access_key = '<insert your access key>'
    secret_key = '<insert your secret key>'
    from qg_cli.qgclient import QuantGoAPIClient
    qgclient = QuantGoAPIClient(access_key, secret_key)
    """

    def __init__(self, access_key, secret_key):
        self._access_key = access_key
        self._secret_key = secret_key
        self._api_client = ApiClient(access_key=self._access_key,
                                     secret_key=self._secret_key)

    def create_keypair(self, key_name):
        """Allows to create keypair in your VQL account. Returns json blob
        with result key name, key material and fingerprint.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.create_keypair('mykey')
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)

        :param string key_name: desired key pair name.
        """
        return self._api_client.call('create-keypair', key_name=key_name)

    def delete_keypair(self, key_name):
        """Allows to delete previously created key pair. As result returns
        json blob saying about successful command execution or contains error
        description.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.delete_keypair('mykey')
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)

        :param string key_name: key pair name to delete.
        """
        return self._api_client.call('delete-keypair', key_name=key_name)

    def describe_instances(self, instance_ids=None, filters=None):
        """Returns detailed information about user instances. Parameters
        instance_ids and filters allows to filter result data. Without
        parameters returns information about all user instances.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_instances(instance_ids=['i-6e82144d'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)

        :param string, list instance_ids: instance id or list of instance ids
        to filter.
        :param dict filters: filtering parameters. Please refer to aws
        describe-instances documetnation for details.
        """
        return self._api_client.call('describe-instances',
                                     instance_ids=instance_ids,
                                     filters=filters)

    def describe_regions(self):
        """Returns available AWS regions.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_regions()
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('describe-regions')

    def run_instances(self, image_id, count, key_name, login_protocol,
                      instance_type='m1.small',
                      **kwargs):
        """Allows to create user instance. For QuantGo specific AMI ids refer
        to QuantGo console. For detailed information on allowed parameters
        please refer to AWS run-instances command documentation.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.run_instances('ami-74e1851c', 1, 'mykey', 'ssh',
                                      'm1.small')
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)

        :param string image_id: AMI id.
        :param int count: number of instances to start.
        :param string key_name: key name to use for instance.
        :param string login_protocol: either ssh or rdp. Indicates which
        protocol is used to connect to instance.
        :param string instance_type: instance type. list_instance_types api
        method returns available instance types.
        """
        return self._api_client.call('run-instances', image_id=image_id,
                                     count=count, key_name=key_name,
                                     login_protocol=login_protocol,
                                     instance_type=instance_type,
                                     **kwargs)

    def start_instances(self, instance_ids):
        """Starts given instances. Argument instance_ids could be either list
        of instance id string. Returns json blob with  message about
        successfull command execution or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.start_instances('i-77655498')
        # also you may pass list of instance ids:
        # client.start_instances(['i-77655498', 'i-a8653eb1'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('start-instances',
                                     instance_ids=instance_ids)

    def stop_instances(self, instance_ids):
        """Stops given instances. Argument instance_ids could be either list
        of instance id string. Returns json blob with message about
        successfull command execution or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.stop_instances('i-77655498')
        # also you may pass list of instance ids:
        # client.stop_instances(['i-77655498', 'i-a8653eb1'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('stop-instances',
                                     instance_ids=instance_ids)

    def terminate_instances(self, instance_ids):
        """Terminate given instances. Argument instance_ids could be either
        list of instance id string. Returns json blob with  message about
        successfull command execution or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.terminate_instances('i-77655498')
        # also you may pass list of instance ids:
        # client.terminate_instances(['i-77655498', 'i-a8653eb1'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('terminate-instances',
                                     instance_ids=instance_ids)

    def reboot_instances(self, instance_ids):
        """Reboots given instances. Argument instance_ids could be either list
        of instance id string. Returns message about successfull command
        execution or error. Please note that it may not work with linux based
        instances. Use stop/start instances command as workaround.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.reboot_instances('i-77655498')
        # also you may pass list of instance ids:
        # client.reboot_instances(['i-77655498', 'i-a8653eb1'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('reboot-instances',
                                     instance_ids=instance_ids)

    def create_volume(self, size=None, snapshot_id=None):
        """Allows to create volume inside VQL. Takes either size or snapshot_id
        as parameters. Returns message about successful volume creation or
        error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.create_volume(size=20)
        import json; print json.dumps(json.loads(result), indent=2)

        :param int size: volume size in GIBs
        :param string snapshot_id: desired snapshot id to clone volume from.
        """
        if not size and snapshot_id is None:
            raise ValueError('Please set size or snapshot_id parameters.')
        if size:
            kwargs = {'size': size}
        else:
            kwargs = {'snapshot_id': snapshot_id}
        return self._api_client.call('create-volume', **kwargs)

    def delete_volume(self, volume_id):
        """Allows to delete volume. Returns message about successful volume
        deletion or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.delete_volume('vol-9048b3dc')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string volume_id: volume id you wish to delete.
        """
        return self._api_client.call('delete-volume', volume_id=volume_id)

    def attach_volume(self, volume_id, instance_id, device):
        """Allows to attach volume to instance. Returns message about
        successful volume attachment or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.attach_volume('vol-9048b3dc', 'i-1ec7a5e0', '/dev/sdh')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string volume_id: volume id you wish to attach.
        :param string instance_id: instance id you wish to attach volume to.
        :param string device: device to expose to instance. Please refer to AWS
        documentation on attach-volume command for more details on device
        parameter value.
        """
        return self._api_client.call('attach-volume', volume_id=volume_id,
                                     instance_id=instance_id, device=device)

    def detach_volume(self, volume_id, instance_id, device, force=False):
        """Allows to detach volume from instance. Returns message about
        successful volume detachment or error.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.detach_volume('vol-9048b3dc', 'i-1ec7a5e0', '/dev/sdh')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string volume_id: volume id you wish to attach.
        :param string instance_id: instance id you wish to attach volume to.
        :param string device: device name.
        :param bool force: force detachment indicator. Defaulted to False.
        """
        return self._api_client.call('detach-volume', volume_id=volume_id,
                                     instance_id=instance_id, device=device,
                                     force=force)

    def describe_volumes(self, volume_ids=None, filters=None):
        """Returns detailed information about user volumes. Parameters
        volume_ids and filters allows to filter result data. Without
        parameters returns information about all user volumes.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_volumes(volume_ids=['vol-9048b3dc'])
        # pretty print result
        import json; print json.dumps(json.loads(result), indent=2)

        :param string, list volume_ids: volume id or list of volume ids
        to filter.
        :param dict filters: filtering parameters. Please refer to aws
        describe-volumes documetnation for details.
        """
        return self._api_client.call('describe-volumes', volume_ids=volume_ids,
                                     filters=filters)

    def get_login_ports(self, instance_id):
        """Returns information about user instance login addresses/ports
        information.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.get_login_ports('i-1ec7a5e0')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you wish to get information of.
        """
        return self._api_client.call('get-login-ports',
                                     instance_id=instance_id)

    def get_console_output(self, instance_id):
        """Returns data from instance console.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.get_console_output('i-1ec7a5e0')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you wish to get information of.
        """
        return self._api_client.call('get-console-output',
                                     instance_id=instance_id)

    def create_tags(self, resource_id, tags):
        """Allows to create user tags on given resource.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.create_tags('i-1ec7a5e0',
                                    [{"Key": "Name", "Value": "MyInstance"}])
        import json; print json.dumps(json.loads(result), indent=2)

        :param string resource_id: resource id you wish to create tag.
        :param list tags: list of tags definitions. Please refer to AWS
        create-tags command to learn more about tags.
        """
        return self._api_client.call('create-tags', resource_id=resource_id,
                                     tags=tags)

    def delete_tags(self, resource_id, tags=None):
        """Allows to delete tags from given resource.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.delete_tags('i-1ec7a5e0',
                                    [{"Key": "Name", "Value": "MyInstance"}])
        import json; print json.dumps(json.loads(result), indent=2)

        :param string resource_id: resource id you wish to delete tag.
        :param list tags: list of tags definitions. Please refer to AWS
        create-tags command to learn more about tags.
        """
        return self._api_client.call('delete-tags', resource_id=resource_id,
                                     tags=tags)

    def describe_tags(self, resource_id):
        """Returns information about user tags added on resource.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_tags('i-1ec7a5e0')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string resource_id: resource id you wish to get tags
        information.
        """
        return self._api_client.call('describe-tags', resource_id=resource_id)

    def set_instance_type(self, instance_id, instance_type):
        """Allows to change instance type.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_tags('i-1ec7a5e0', 't1.micro')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you wish to change type.
        :param string instance_type: instance type you want to change to.
        """
        return self._api_client.call('set-instance-type',
                                     instance_id=instance_id,
                                     instance_type=instance_type)

    def set_instance_name(self, instance_id, instance_name):
        """Shortcut for Name tag. Allows to create instance name tag.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.set_instance_name('i-1ec7a5e0', 'MyShinyInstance')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you wish to set name.
        :param string instance_name: instance name.
        """
        return self._api_client.call('set-instance-name',
                                     instance_id=instance_id,
                                     instance_name=instance_name)

    def delete_instance_name(self, instance_id):
        """Allows to delete instance name tag.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.delete_instance_name('i-1ec7a5e0')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you wish to delete name.
        """
        return self._api_client.call('delete-instance-name',
                                     instance_id=instance_id)

    def describe_key_pairs(self, key_name=None):
        """Returns user key pairs information. Please note it includes only
        key pair names and fingerprints as Amazon and QuantGo cannot store
        you key material data.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.describe_key_pairs()
        import json; print json.dumps(json.loads(result), indent=2)

        :param string key_name: key pair name you wish to get information about
        """
        return self._api_client.call('describe-key-pairs',
                                     key_name=key_name)

    def list_instance_types(self):
        """Returns available instance types list.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.list_instance_types()
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('list-instance-types')

    def list_gateway_types(self):
        """Returns available gateway types list.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.list_gateway_types()
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('list-gateway-types')

    def get_gateway_type(self):
        """Returns current gateway type.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.get_gateway_type()
        import json; print json.dumps(json.loads(result), indent=2)
        """
        return self._api_client.call('get-gateway-type')

    def set_gateway_type(self, instance_type):
        """Allows to change gateway type. For available gateway types please
        refer to api command get_gateway_types.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.set_gateway_type('m2.medium')
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_type: desired gateway type.
        """
        return self._api_client.call('set-gateway-type',
                                     instance_type=instance_type)

    def get_windows_password_data(self, instance_id):
        """Returns encrypted password data for given instance. Applicable only
        for Windows based instances.

        :Example:

        from qg_cli.qgclient import QuantGoAPIClient
        client = QuantGoAPIClient(access_key, secret_key)
        result = client.get_gateway_type()
        import json; print json.dumps(json.loads(result), indent=2)

        :param string instance_id: instance id you want to get password data
        from.
        """
        return self._api_client.call('get-windows-password-data',
                                     instance_id=instance_id)
