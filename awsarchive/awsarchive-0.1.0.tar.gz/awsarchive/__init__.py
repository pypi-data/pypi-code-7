import argparse
from collections import namedtuple
import os.path

from boto import sdb, connect_glacier


ArchiveMetadata = namedtuple(
    'ArchiveMetadata', 'archive_id filename vault region')


def to_glacier(filename, vault_name, access_key, secret_key, region):
    """
    Archive file in glacier. On completion, the archive will be assigned a ID
    which is returned and should be stored to be used for retrieving the file
    at a later stage.

    :type filename: string
    :param filename: Local file to archive.

    :type vault_name: string
    :param vault_name: AWS Glacier vault to store file in.

    :type access_key: string
    :param access_key: AWS Glacier access key.
    
    :type secret_key: string
    :param secret_key: AWS Glacier secret key.
    
    :type region: string
    :param region: AWS Glacier region name.

    :rtype: :class:`awsarchive.ArchiveMetadata`
    :returns: Archive metadata.
    """
    conn = connect_glacier(
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    vault = conn.create_vault(vault_name)
    id_ = vault.concurrent_create_archive_from_file(
        filename,
        description=None,
        num_threads=80
    )
    return ArchiveMetadata(id_, os.path.basename(filename), vault_name, region)


def log_archive(metadata, domain_name, access_key, secret_key, region):
    """
    Log archive to AWS SimpleDB. The archive ID will be used for the item name
    along with filename, the vault name and the region where the vault is
    located as its attributes.

    :type archive_metadata: :class:`awsarchive.ArchiveMetadata`
    :param archive_metadata: Information about the archive.

    :type domain_name: string
    :param domain_name: AWS SimpleDB domain name.

    :type access_key: string
    :param access_key: AWS SimpleDB access key.

    :type secret_key: string
    :param secret_key: AWS SimpleDB secret key.

    :type region: string
    :param region: AWS SimpleDB region name.
    """
    conn = sdb.connect_to_region(
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)
    dom = conn.create_domain(domain_name)
    dom.put_attributes(
        metadata.archive_id,
        {
            "filename": metadata.filename,
            "vault": metadata.vault,
            "region": metadata.region
        }
    )


def handle_glacier(args):
    metadata = to_glacier(
        filename=args.file,
        vault_name=args.vault,
        access_key=args.access_key,
        secret_key=args.secret_key,
        region=args.region
    )
    if args.domain:
        log_archive(
            metadata=metadata,
            domain_name=args.domain,
            access_key=args.access_key,
            secret_key=args.secret_key,
            region=args.region
        )
    print metadata


def get_args():
    parser = argparse.ArgumentParser(
        usage="Toolkit for archiving files using AWS products.")
    subparsers = parser.add_subparsers(help="Available commands")

    glacier = subparsers.add_parser('glacier', help="Archive files in Glacier.")
    glacier.add_argument(
        '-f', '--file', required=True, help="File to archive.")
    glacier.add_argument(
        '-v', '--vault', required=True, help="Glacier vault name.")
    glacier.add_argument(
        '-a', '--access-key', required=True, help="AWS access key.")
    glacier.add_argument(
        '-s', '--secret-key', required=True, help="AWS secret key.")
    glacier.add_argument(
        '-r', '--region', required=True, help="AWS region name.")
    glacier.add_argument(
        '-d', '--domain', help="SimpleDB domain name. If given, the archive will be logged in SimpleDB.")
    glacier.set_defaults(func=handle_glacier)

    return parser.parse_args()


def main():
    arguments = get_args()
    arguments.func(arguments)


if __name__ == '__main__':
    main()
