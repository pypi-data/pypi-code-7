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

import os
import subprocess
import re


FAILED_RE = re.compile(r'failed\=(\d+)')


def execute(command, **kwargs):
    """
    Run given command printing out stdout and stderr.
    Collect final stdout and stderr and return them as a result.
    """
    log_file = ".ansible.log"
    proc = subprocess.Popen(
        " ".join(command) + " 2>&1 | tee {}".format(log_file),
        shell=True,
        **kwargs
    )
    proc.wait()

    with open(log_file) as fh:
        result = fh.read()
        return result


def run_playbook(
        playbook,
        inventory_path=None,
        verbose=False,
        retry=False,
        extra_vars=None,
        dry_run=False):
    """
    Runs Ansible playbook.
    Detects playbook failure or success, and
    returns True if playbook is successful.
    """
    ansible_invocation = [
        'ansible-playbook',
    ]
    if inventory_path:
        ansible_invocation += [
            '-i',
            inventory_path
        ]

    if verbose:
        ansible_invocation.append('-vvvv')
    if extra_vars:
        ansible_invocation += [
            "--extra-vars",
            "'{}'".format(extra_vars.replace('\\', '\\\\'))
        ]

    ansible_invocation.append(
        playbook
    )

    if retry:
        retry_file = "{0}.retry".format(
            os.path.basename(playbook)
        ).replace(".yml", "")
        retry_path = os.path.expanduser(os.path.join("~", retry_file))
        if os.path.exists(retry_path):
            ansible_invocation += [
                "--limit",
                "@" + retry_path
            ]

    env = os.environ.copy()
    env['ANSIBLE_HOST_KEY_CHECKING'] = "False"
    env['PYTHONUNBUFFERED'] = "True"
    if dry_run:
        if os.path.exists(inventory_path):
            with open(inventory_path) as fh:
                print("Inventory:")
                print(fh.read())
        else:
            print("Inventory file \"{}\" doesn't exist.".format(inventory_path))
        print("Ansible command:")
        print(" ".join(ansible_invocation))
        return True
    stdout = execute(ansible_invocation, env=env)
    if "FATAL:" in stdout:
        return False
    failed_number = FAILED_RE.search(stdout)
    if failed_number:
        failed_jobs = int(failed_number.group(1))
        return failed_jobs == 0
    return None
