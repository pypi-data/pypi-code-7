
from datetime import datetime
from systematic.log import LogFile, LogEntry, LogFileError

class BackupTask(object):
    def __init__(self, entry):
        self.backup_date = None
        self.started = None
        self.finished = None
        self.state = 'UNKNOWN'
        self.messages = []

        self.add_logentry(entry)

    def __repr__(self):
        if self.state == 'finished':
            return 'FINISHED %s' % self.backup_date
        elif self.state == 'failed':
            return 'FAILED %s' % self.started
        else:
            return '%s %s' % (self.state.upper(), self.started)

    def add_logentry(self, entry):
        if entry.message == 'Starting automatic backup':
            self.started = entry.time
            self.state = 'started'

        elif entry.message[:13] == 'Backup failed':
            self.finished = entry.time
            self.state = 'failed'

        elif entry.message[:19] == 'Created new backup:':
            self.backup_date = datetime.strptime(entry.message[19:].strip(), '%Y-%m-%d-%H%M%S')
            self.state = 'created'

        elif entry.message == 'Starting post-backup thinning':
            self.state = 'cleanup'

        elif entry.message[:30] == 'Post-backup thinning complete:':
            self.stateu = 'cleanup_finished'

        elif entry.message == 'Backup completed successfully.':
            self.finished = entry.time
            self.state = 'finished'

        self.messages.append(entry)


class BackupdLogEntry(LogEntry):
    pass

class BackupdLog(LogFile):
    lineloader = BackupdLogEntry

    def __init__(self):
        LogFile.__init__(self, '/var/log/system.log')
        self.backups = []

    def __is_backupd_logentry__(self, entry):
        return entry.program == 'com.apple.backupd'

    @property
    def last_failed_backup(self):
        try:
            return [x.finished for x in self.backups if x.state == 'failed'][-1]
        except IndexError:
            return None

    @property
    def last_successful_backup(self):
        try:
            return [x.backup_date for x in self.backups if x.state == 'finished'][-1]
        except IndexError:
            return None

    def next(self):
        entry = self.next_iterator_match(iterator='default', callback=self.__is_backupd_logentry__)
        if entry is None:
            return None

        if entry.message == 'Starting automatic backup':
            self.backups.append(BackupTask(entry))
        elif self.backups:
            self.backups[-1].add_logentry(entry)
        return entry

if __name__ == '__main__':
    log = BackupdLog()
    log.reload()
    print log.last_failed_backup
    print log.last_successful_backup
