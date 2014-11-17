import time
import sys
import boto.ec2
from BaseAWS import AbstractAWS


class EC2(AbstractAWS):

    def __init__(self, aws_account, config_file):
        self.aws_account = aws_account
        self.set_config(config_file, aws_account)
        self.conn_ec2 = None

    def set_ec2_conn(self, region=None):
        if region is None:
            region = self.config['region']

        self.conn_ec2 = boto.ec2.connect_to_region(region,
                                                   aws_access_key_id=self.config['aws_access_key_id'],
                                                   aws_secret_access_key=self.config['aws_secret_access_key'])

    def get_instance_list(self):
        '''
        Return a list of 'running' instances
        '''
        if self.conn_ec2 is None:
            self.set_ec2_conn()
        instance_list = self.conn_ec2.get_all_instances(filters={'instance-state-name': 'running'})
        return instance_list

    def create_instance(self, server):
        '''
        instance_data should be a python dictionary, for example: see example file:
        config/example_instance_data.yaml
        '''

        if self.conn_ec2 is None:
            self.set_ec2_conn()
        if self.instance_data is None:
            print "[ERROR] No Instance data set"
            exit(1)

        try:
            data = self.instance_data['servers'][server]
        except KeyError:
            print "[ERROR] No Server found:", server
            sys.exit(1)

        reservation = self.conn_ec2.run_instances(str(data['ami']),
                                                  key_name=str(data['key']),
                                                  instance_type=str(data['instance_type']),
                                                  security_groups=data['security_groups'],
                                                  user_data=open(data['userdata']).read())

        instance = reservation.instances[0]
        print "Sleeping 5s while EC2 wakes up..."
        time.sleep(5)

        status = instance.update()
        while status != 'running':
            time.sleep(10)
            print "Sleeping for 10 more seconds (not ready yet...)"
            status = instance.update()

        # Set the tags for the instance when 'running'
        if status == 'running':
            for tag in data['tags']:
                instance.add_tag(str(tag), str(data['tags'][tag]))
                print "[EC2] Set Instance Tag to %s:%s" % (str(tag), str(data['tags'][tag]))

        return instance

    def terminate_instances(self, instances_list):
        '''
        Terminate a list of instances based on their ID's
        '''
        if self.conn_ec2 is None:
            self.set_ec2_conn()
        self.conn_ec2.terminate_instances(instance_ids=instances_list)
        print "Terminated:", instances_list
