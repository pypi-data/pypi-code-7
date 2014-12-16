# joblib_launcher.py

import os
import sys
import shlex
from clusterlib.scheduler import queued_or_running_jobs
from clusterlib.scheduler import submit
from joblib_main import main

if __name__ == "__main__":
    scheduled_jobs = set(queued_or_running_jobs())
    for param in range(100):
        job_name = "job-param=%s" % param
        job_command = "%s joblib.py --param %s" % (sys.executable, param)

        if job_name not in scheduled_jobs:
            try:
                # if results are not shelved, ...
                main.get(shlex.split(job_command))
            except KeyError:
                # ... then launch a job
                script = submit(job_command, job_name=job_name)

                print(script)
                # Uncomment this to launch
                # os.system(script)
