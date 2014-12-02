from datetime import datetime
import argparse
import boto.ec2
import yaml
import sys
import os

# CLI definitions
parser = argparse.ArgumentParser(description='Simple tool to manage AWS Volume Snapshots using the AWS API.')
parser.add_argument('region', nargs=1, action='store',
                   help='The ID of the AWS region where your volumes are. (e.g., us-west-1)')
parser.add_argument('volume', nargs=1, action='store',
                   help='The ID of the volume you want to take the snapshot from. (e.g., vol-abcd1234)')
parser.add_argument('keep', nargs=1, type=int, default=1, action='store',
                   help='Number of snapshots to keep. (i.e., if 3, the last 3 snapshots will be kept. When the fourth one is taken, the oldest will be automatically deleted.')
parser.add_argument('description', nargs='?', action='store',
                   help='Snapshot description')
parser.add_argument('--config', dest='config', type=argparse.FileType('r'),
                   help='YAML formatted configuration file to be used. Default is ./awsnapshots.yaml')

def run():
    args = parser.parse_args()

    try:
        if (not args.config):
            config = yaml.load(file(os.getcwd() + '/awsnapshots.yaml'))
        else:
            config = yaml.load(args.config)
    except:
        print 'Configuration file not found.'
        sys.exit(1)

    conn = boto.ec2.connect_to_region(args.region, aws_access_key_id = config['AWS_ACCESS_KEY'], aws_secret_access_key = config['AWS_SECRET_KEY'])

    volumes = conn.get_all_volumes([args.volume])
    if (len(volumes) <= 0):
        print 'Cannot find volume '+ args.volume
        sys.exit(1)

    volume = volumes[0]
    description = 'Created by AWSnapshots at ' + datetime.today().isoformat(' ')
    if args.description:
        description = args.description

    if volume.create_snapshot(description):
        print 'Snapshot created with description: ' + description

    snapshots = volume.snapshots()
    snapshot = snapshots[0]

    def date_compare(snap1, snap2):
        if snap1.start_time < snap2.start_time:
            return -1
        elif snap1.start_time == snap2.start_time:
            return 0
        return 1

    snapshots.sort(date_compare)
    delta = len(snapshots) - args.keep
    for i in range(delta):
        print 'Deleting snapshot ' + snapshots[i].description
        try:
            snapshots[i].delete()
        except:
            print 'Snapshot ' + snapshots[i].description + ' could not be deleted.'
