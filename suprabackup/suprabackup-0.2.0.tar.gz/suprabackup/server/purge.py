"""
This module contains utils to purge expired backups

"""
from ..models import Job, JobStatus

class SupraPurge:
    """
    This class stores config, logger and session and provides utils to purge
    old backup jobs from disk and database

    """

    def __init__(self, config, logger, session):
        """
        Sets up SupraReceive with given config/logger and db connection

        """
        self.config = config
        self.logger = logger
        self.session = session


    def purge(self):
        """
        Fetch all expired backup jobs from database and remove them from disk

        """
        import os

        for job in self.session.query(Job).all():
            if job.expired:
                try:
                    os.remove(job.file_path)
                    self.logger.info("Job {} purged: file {} removed"
                                     .format(job.id, job.file_path))
                except OSError as e:
                    self.logger.warning("Cannot remove file {} for job id {}"
                                        .format(job.file_path, job.id))
                finally:
                    job.status = JobStatus.PURGED


def purge_backups(config, logger, session):
    """
    A simple wrapper around SupraPurge

    """
    purger = SupraPurge(config, logger, session)
    purger.purge()
