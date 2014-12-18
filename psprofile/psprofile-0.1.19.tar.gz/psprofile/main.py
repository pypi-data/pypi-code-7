from __future__ import division
import time
from collections import OrderedDict, defaultdict
import os
import signal
import sys
import psutil

from .util import mean, max, poll_children


def main(command, poll_interval, shell, skip_profile):
    try:
        # Run the command and do the polling
        start_time = time.time()
        proc = psutil.Popen(' '.join(command), shell=shell)

        output = OrderedDict()
        if skip_profile:
            output['exit_status'] = proc.wait()
        else:
            # Declare data store variables
            records = defaultdict(list)
            for place_holder in ['percent_cpu', 'wall_time', 'cpu_time', 'avg_rss_mem_kb', 'avg_vms_mem_kb', 'max_rss_mem_kb', 'max_vms_mem_kb']:
                output[place_holder] = None

            # Do Polling
            num_polls = 0
            while proc.poll() is None:
                num_polls += 1

                # get results from all children
                poll_result = defaultdict(list)
                for name, value in poll_children(proc):
                    poll_result[name].append(value)

                # sum results from children and put in output/records
                for name, values in poll_result.items():
                    if name in ['rss_mem_kb', 'vms_mem_kb', 'num_threads', 'num_fds']:
                        # TODO consolidate values to avoid using too much ram.  need to save max to do this
                        # if num_polls % 3600 == 0:
                        # records[name] = [_mean(records[name])]

                        records[name].append(sum(values))
                    else:
                        output[name] = sum(values)



                time.sleep(poll_interval)

    except KeyboardInterrupt:
        print >> sys.stderr, 'Caught a SIGINT (ctrl+c), terminating'
        os.kill(proc.pid, signal.SIGINT)
        output['exit_status'] = signal.SIGINT

    end_time = time.time()

    output['wall_time'] = end_time - start_time
    if not skip_profile:
        # Get means and maxes
        for name, values in records.items():
            output['avg_%s' % name] = mean(values)
            output['max_%s' % name] = max(values)

        # Calculate some extra fields
        output['num_polls'] = num_polls
        output['exit_status'] = proc.poll()
        output['cpu_time'] = output.get('user_time', 0) + output.get('system_time', 0)
        try:
            output['percent_cpu'] = int(round(float(output['cpu_time']) / float(output['wall_time']), 2) * 100)
        except ZeroDivisionError:
            output['percent_cpu'] = 0


    return output