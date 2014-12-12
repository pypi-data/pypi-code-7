"""
This module contains utils to verify past jobs

"""
from ..models import Job, JobStatus


class SupraVerify:
    """
    This class is used to store logger, config and db connection with utils
    for verifying last backup jobs

    """

    def __init__(self, config, logger, session):
        """
        Sets up SupraReceive with given config/logger and db connection

        """
        self.config = config
        self.logger = logger
        self.session = session


    def verify(self):
        """
        Fetch all backups from database and check each file
        Updates the job status accordingly

        """
        self.logger.debug("Started verify jobs")
        for job in self.session.query(Job).filter(Job.status == JobStatus.DONE):
            if self.check_file(job.file_path):
                self.logger.info("Last backup for host {0} is OK"
                                 .format(job.host.name))
                job.status = JobStatus.VERIFIED
            else:
                self.logger.warning("Last backup for host {0} is NOT OK"
                                    .format(job.host.name))
                job.status = JobStatus.FAILED
        self.logger.debug("Ended verify jobs")


    def check_file(self, path):
        """
        Checks the TAR archive at path and returns True if OK

        """
        import subprocess

        with open('/dev/null', 'w') as null:
            ret = subprocess.call(['tar', '-tzf', path],
                                  stdout=null, stderr=null, stdin=null)
            if ret:
                return False
            else:
                return True


def verify_backups(config, logger, session):
    """
    A simple wrapper to SupraVerify

    """
    verifier = SupraVerify(config, logger, session)
    verifier.verify()
