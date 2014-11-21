'''
basic serial main function module
'''

import logging
from data import load, save_result, strip_ephemeral
from serial_process import process, required_actions_count, print_progress_info

logger = logging.getLogger(__name__)

def main(conf, istream, ostream, test_whitelist, test_blacklist, stage_whitelist, stage_blacklist,
            tags_whitelist, tags_blacklist, no_action):
    '''
    main worker function
    performs particular stages handling
    generates particular stage/test result list
    '''
    params = dict(test_whitelist=test_whitelist, test_blacklist=test_blacklist,
                    stage_whitelist=stage_whitelist, stage_blacklist=stage_blacklist,
                    tags_whitelist=tags_whitelist, tags_blacklist=tags_blacklist,
                   enabled=not no_action)
    params = load(istream, config_file=conf, augment=params)
    total = required_actions_count(params)
    processed = 0
    print_progress_info(processed, total)
    for item in params:
        for result in process(item):
            processed += 1
            save_result(ostream, strip_ephemeral(result))
            print_progress_info(processed, total)

