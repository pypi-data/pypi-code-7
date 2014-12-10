# Copyright (c) 2014 Scopely, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from boto.ec2.blockdevicemapping import BlockDeviceMapping, \
    EBSBlockDeviceType, BlockDeviceType


def block_device_to_boto(block_device_map):
    """
    Accepts block device map in a format:

        block_device_map:
          - device_name: /dev/sda1
            ebs:
              delete_on_termination: True
              volume_size: 60
              volume_type: gp2

    Returns boto object
    """
    if block_device_map:
        bdm = BlockDeviceMapping()
        for device in block_device_map:
            if 'ebs' in device:
                bdm[device['device_name']] = EBSBlockDeviceType(
                    no_device=device.get('no_device'),
                    delete_on_termination=device['ebs'].get(
                        'delete_on_termination', True),
                    size=device['ebs'].get('volume_size', None),
                    volume_type=device['ebs'].get('volume_type', None)
                )
            if 'virtual_name' in device:
                bdm[device['device_name']] = BlockDeviceType(
                    ephemeral_name=device['virtual_name'],
                    no_device=device.get('no_device')
                )
        return bdm
    return None


def block_device_to_cf(block_device_map, override_gp2=True):
    """
    Accepts block device map in a format:

        block_device_map:
          - device_name: /dev/sda1
            ebs:
              delete_on_termination: True
              volume_size: 60
              volume_type: gp2

    Returns a CloudFormation-style dictionary
    """

    def convert_keys(dct):
        if isinstance(dct, dict):
            return {
                "".join([
                    part.capitalize() for part in key.split('_')
                ]): convert_keys(value)
                for key, value in dct.items()
            }
        if override_gp2 and dct == "gp2":
            # don't allow gp2 in ASG for now, until CF supports it
            return "standard"
        return dct

    if block_device_map:
        return [convert_keys(dct) for dct in block_device_map]
    return None
