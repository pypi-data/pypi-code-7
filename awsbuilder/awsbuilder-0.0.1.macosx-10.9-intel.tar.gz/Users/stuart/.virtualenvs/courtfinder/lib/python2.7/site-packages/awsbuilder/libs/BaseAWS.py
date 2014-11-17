import os.path
import yaml


class AbstractAWS:

    config = None
    instance_data = None

    def set_config(self, config_file, account):
        '''
        Read in the generic config.yaml file and return the project section
        '''

        if config_file is not None and os.path.isfile(config_file):
            f = open(config_file).read()
            self.config = yaml.load(f)['account'][account]
        else:
            raise Exception('Invalid config file')
            sys.exit(1)

    def get_config(self):
        if self.config is not None:
            return self.config
        else:
            return None

    def set_instance_data(self, instance_data_file, project, environment):
        '''
        Read in the generic instance_data file and return the environment section
        '''

        if instance_data_file is not None and os.path.isfile(instance_data_file):
            f = open(instance_data_file).read()
            self.instance_data = yaml.load(f)['project'][project][environment]
        else:
            raise Exception('Invalid instance data file')
            sys.exit(1)