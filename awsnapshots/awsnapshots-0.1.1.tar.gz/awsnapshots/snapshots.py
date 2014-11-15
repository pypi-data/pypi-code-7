import boto.ec2
import os
import sys
import yaml
from datetime import datetime

def run():
    try:
        config = yaml.load(file(os.getcwd() + '/awsnapshots.yaml'))
    except:
        try:
            config = yaml.load('/etc/awsnapshots.yaml')
        except:
            pass

        print "Configuration file not found."
        sys.exit(1)

    if len(sys.argv) < 4:
        print "Usage: awsnapshots <region_id> <volume_id> <snapshots_to_keep> [description]"
        print "Region id, volume id, and number of snapshots to keep are required. Description is optional."
        sys.exit(1)


    region = sys.argv[1]
    vol_id = sys.argv[2]
    keep = int(sys.argv[3])


    conn = boto.ec2.connect_to_region(region, aws_access_key_id = config['AWS_ACCESS_KEY'], aws_secret_access_key = config['AWS_SECRET_KEY'])

    volumes = conn.get_all_volumes([vol_id])
    volume = volumes[0]
    description = 'Created by AWSnapshots at ' + datetime.today().isoformat(' ')

    if len(sys.argv) > 4:
        description = sys.argv[4]

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
    delta = len(snapshots) - keep
    for i in range(delta):
        print 'Deleting snapshot ' + snapshots[i].description
        snapshots[i].delete()
