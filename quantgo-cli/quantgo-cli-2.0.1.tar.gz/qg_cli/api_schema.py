# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

"""Command schemas"""

commands = {
    "create-keypair": {
        "additionalProperties": False,
        "name": "CreateUserKeypair",
        "description": "Creates key pair used to access instances.",
        "properties": {
            "key-name": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "KeyName",
                "description": "Name of key pair.",
                "required": True,
                "type": "array"
            }
        },
        "type": "object"
    },
    "delete-keypair": {
        "additionalProperties": False,
        "name": "DeleteUserKeypair",
        "description": "Deletes specified key pair.",
        "properties": {
            "key-name": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "KeyName",
                "description": "Name of key pair.",
                "required": True,
                "type": "array"
            }
        },
        "type": "object"
    },
    "describe-instances": {
        "additionalProperties": False,
        "name": "DescribeUserInstances",
        "description": "Allows to see information about instances.",
        "properties": {
            "filters": {
                "items": [
                    {
                        "additionalProperties": False,
                        "name": "Filters",
                        "properties": {
                            "name": {
                                "name": "Name",
                                "required": True,
                                "type": "string"
                            },
                            "value": {
                                "name": "Value",
                                "required": True,
                                "type": "string"
                            }
                        },
                        "required": True,
                        "type": "object"
                    }
                ],
                "required": False,
                "description": "Filters to apply to list of results.",
                "type": "array"
            },
            "instance-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "InstanceIds",
                "description": "Instances IDs.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "describe-regions": {
        "additionalProperties": False,
        "name": "DescribeRegions",
        "type": "string",
        "description": "Returns names of available regions."
    },
    "run-instances": {
        "additionalProperties": False,
        "name": "RunUserInstances",
        "description": "Allows to start instances with specified parameters.",
        "properties": {
            "count": {
                "name": "Count",
                "required": True,
                "description": "Number of instances to start.",
                "type": "integer"
            },
            "image-id": {
                "name": "ImageId",
                "description": "Image name to use when creating instance.",
                "required": True,
                "type": "string"
            },
            "instance-initiated-shutdown-behavior": {
                "default": "stop",
                "enum": [
                    "stop",
                    "terminate"
                ],
                "name": "InstanceInitiatedShutdownBehavior",
                "description": "Define whether instance would be terminated when stopped.",
                "required": False,
                "type": "string"
            },
            "instance-type": {
                "default": "m1.small",
                "enum": [
                      "t1.micro",
                      "c1.medium",
                      "c1.xlarge",
                      "m1.small",
                      "m1.medium",
                      "m1.large",
                      "m1.xlarge",
                      "m2.xlarge",
                      "m2.2xlarge",
                      "m2.4xlarge",
                      "m3.xlarge",
                      "m3.2xlarge"
                ],
                "name": "InstanceType",
                "description": "Instance type. Refer to amazon documentation to get more details on instance types.",
                "required": False,
                "type": "string"
            },
            "key-name": {
                "name": "KeyName",
                "description": "Name of key pair to use when accessing instance.",
                "required": True,
                "type": "string"
            },
            "login-protocol": {
                "enum": [
                    "ssh",
                    "rdp",
                    "22",
                    "linux",
                    "windows",
                    "3389"
                ],
                "name": "LoginProtocol",
                "description": "Define protocol to use when accessing instance.",
                "required": True,
                "type": "string"
            },
            "user-data": {
                "default": None,
                "name": "UserData",
                "description": "The Base64-encoded MIME user data to be made available to the instance(s).",
                "required": False,
                "type": "string"
            },
            "kernel-id": {
                "default": None,
                "name": "KernelId",
                "description": "The ID of the kernel with which to launch the instance.",
                "required": False,
                "type": "string"
            },
            "ramdisk-id": {
                "default": None,
                "name": "RamdiskId",
                "description": "The ID of the ramdisk with which to launch the instance.",
                "required": False,
                "type": "string"
            },
            "disable-api-termination": {
                "default": False,
                "name": "DisableAPITermination",
                "description": "Disables ability to terminate instance using API.",
                "required": False,
                "type": "boolean"
            }
        },
        "type": "object"
    },
    "start-instances": {
        "additionalProperties": False,
        "name": "StartUserInstances",
        "description": "Allows to start user instances.",
        "properties": {
            "instance-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "InstanceIds",
                "description": "IDs of instances.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "stop-instances": {
        "additionalProperties": False,
        "name": "StopUserInstances",
        "description": "Allows to stop user instances.",
        "properties": {
            "instance-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "InstanceIds",
                "description": "IDs of instances.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "terminate-instances": {
        "additionalProperties": False,
        "name": "TerminateUserInstances",
        "description": "Allows to terminate user instances.",
        "properties": {
            "instance-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "InstanceIds",
                "description": "IDs of instances.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "reboot-instances": {
        "additionalProperties": False,
        "name": "RebootUserInstances",
        "description": "Allows to reboot user instances.",
        "properties": {
            "instance-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "InstanceIds",
                "description": "IDs of instances.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "create-volume": {
        "additionalProperties": False,
        "name": "CreateUserVolume",
        "description": "Allows to create EBS volumes.",
        "properties": {
            "size": {
                "name": "Size",
                "description": "The size of the volume, in GiBs.",
                "required": False,
                "type": "integer",
                "minValue": 1,
                "maxValue": 1024
            },
            "snapshot-id": {
                "name": "SnapshotId",
                "description": "The snapshot from which to create the new volume.",
                "required": False,
                "type": "string"
            },
            "volume-type": {
                "name": "VolumeType",
                "description": "The volume type.",
                "required": False,
                "type": "string",
                "enum": [
                    "standard",
                    "io1"
                ],
            },
            "iops": {
                "name": "Iops",
                "description": "The number of I/O operations per second (IOPS) that the volume supports.",
                "required": False,
                "type": "integer",
                "minValue": 100,
                "maxValue": 2000
            }
        },
        "type": "object"
    },
    "delete-volume": {
        "additionalProperties": False,
        "name": "DeleteUserVolume",
        "description": "Allows to delete EBS volumes.",
        "properties": {
            "volume-id": {
                "name": "VolumeId",
                "description": "The ID of the volume.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "attach-volume": {
        "additionalProperties": False,
        "name": "AttachUserVolume",
        "description": "Allows to stop user instances.",
        "properties": {
            "volume-id": {
                "name": "VolumeId",
                "description": "The ID of the Amazon EBS volume. The volume and instance must be within the same Availability Zone.",
                "required": True,
                "type": "string"
            },
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance. The instance must be running.",
                "required": True,
                "type": "string"
            },
            "device": {
                "name": "Device",
                "description": "The device name as exposed to the instance (e.g., /dev/sdh, or xvdh).",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "detach-volume": {
        "additionalProperties": False,
        "name": "DetachUserVolume",
        "description": "Detaches an Amazon EBS volume from an instance. Make sure to unmount any file systems on the device within your operating system before detaching the volume.",
        "properties": {
            "volume-id": {
                "name": "VolumeId",
                "description": "The ID of the Amazon EBS volume. The volume and instance must be within the same Availability Zone.",
                "required": True,
                "type": "string"
            },
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance. The instance must be running.",
                "required": False,
                "type": "string"
            },
            "device": {
                "name": "Device",
                "description": "The device name as exposed to the instance (e.g., /dev/sdh, or xvdh).",
                "required": False,
                "type": "string"
            },
            "force": {
                "name": "Force",
                "description": "Forces detachment if the previous detachment attempt did not occur cleanly.",
                "required": False,
                "type": "boolean"
            }
        },
        "type": "object"
    },
    "describe-volumes": {
        "additionalProperties": False,
        "name": "DescribeUserVolumes",
        "description": "Allows to see information about volumes.",
        "properties": {
            "filters": {
                "items": [
                    {
                        "additionalProperties": False,
                        "name": "Filters",
                        "properties": {
                            "name": {
                                "name": "Name",
                                "required": True,
                                "type": "string"
                            },
                            "value": {
                                "name": "Value",
                                "required": True,
                                "type": "string"
                            }
                        },
                        "required": True,
                        "type": "object"
                    }
                ],
                "required": False,
                "description": "Filters to apply to list of results.",
                "type": "array"
            },
            "volume-ids": {
                "items": [
                    {
                        "blank": False,
                        "type": "string"
                    }
                ],
                "name": "VolumeIds",
                "description": "Volumes IDs.",
                "required": False,
                "type": "array"
            }
        },
        "type": "object"
    },
    "get-login-ports": {
        "additionalProperties": False,
        "name": "GetLoginPorts",
        "description": "Allows user to get port forwarding details for specified instance ID.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "get-console-output": {
        "additionalProperties": False,
        "name": "GetConsoleOutput",
        "description": "Allows user to get console output from specified instance ID.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "create-tags": {
        "additionalProperties": False,
        "name": "CreateTags",
        "description": "Allows user to add tags for specified resources.",
        "properties": {
            "resource-id": {
                "name": "ResourceId",
                "description": "The ID of the resource.",
                "required": True,
                "type": "string"
            },
            "tags": {
                "name": "Tags",
                "description": "Tags list.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "delete-tags": {
        "additionalProperties": False,
        "name": "DeleteTags",
        "description": "Allows user to remove tags for specified resources.",
        "properties": {
            "resource-id": {
                "name": "ResourceId",
                "description": "The ID of the resource.",
                "required": True,
                "type": "string"
            },
            "tags": {
                "name": "Tags",
                "description": "Tags list.",
                "required": False,
                "type": "string"
            }
        },
        "type": "object"
    },
    "describe-tags": {
        "additionalProperties": False,
        "name": "DescribeTags",
        "description": "Allows user to get information about created tags.",
        "properties": {
            "resource-id": {
                "name": "ResourceId",
                "description": "The ID of the resource.",
                "required": False,
                "type": "string"
            }
        },
        "type": "object"
    },
    "list-instance-types": {
        "additionalProperties": False,
        "name": "ListUserInstanceTypes",
        "description": "Allows user to get information about available instance types.",
        "type": "object"
    },
    "set-instance-type": {
        "additionalProperties": False,
        "name": "SetUserInstanceType",
        "description": "Allows user to change instance type.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            },
            "instance-type": {
                "name": "InstanceType",
                "description": "The type of the instance to set to.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "set-instance-name": {
        "additionalProperties": False,
        "name": "SetUserInstanceName",
        "description": "Allows user to set instance name.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            },
            "instance-name": {
                "name": "InstanceName",
                "description": "The desired name you want to set to instance.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "delete-instance-name": {
        "additionalProperties": False,
        "name": "DeleteUserInstanceName",
        "description": "Allows user to unset instance name.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "describe-key-pairs": {
        "additionalProperties": False,
        "name": "DescribeUserKeypairs",
        "description": "Displays information about user key pairs.",
        "properties": {
            "key-name": {
                "name": "KeyName",
                "description": "The name of key pair.",
                "required": False,
                "type": "string"
            }
        },
        "type": "object"
    },
    "list-gateway-types": {
        "additionalProperties": False,
        "name": "ListNatInstanceTypes",
        "description": "Displays available gateway types.",
        "type": "object"
    },
    "get-gateway-type": {
        "additionalProperties": False,
        "name": "GetNatInstanceType",
        "description": "Displays gateway type.",
        "type": "object"
    },
    "set-gateway-type": {
        "additionalProperties": False,
        "name": "SetNatInstanceType",
        "description": "Allows user to change gateway type.",
        "properties": {
            "instance-type": {
                "name": "InstanceType",
                "description": "The type of the gateway instance to change to.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
    "get-windows-password-data": {
        "additionalProperties": False,
        "name": "GetPasswordData",
        "description": "Allows user to get windows instance encrypted password data.",
        "properties": {
            "instance-id": {
                "name": "InstanceId",
                "description": "The ID of the instance.",
                "required": True,
                "type": "string"
            }
        },
        "type": "object"
    },
}


if __name__ == '__main__':
    import json
    try:
        json.dumps(commands)
    except Exception:
        raise
    print 'Schema verification successful.'
