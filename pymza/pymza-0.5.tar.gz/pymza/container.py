import logging
import gevent
from kafka import KafkaClient

from .task import Task

logger = logging.getLogger('pymza.container')


class TaskContainer(object):

    def __init__(self, kafka_hosts, tasks, state_manager, repo):
        self.tasks = tasks
        self.state_manager = state_manager
        self.kafka = KafkaClient(kafka_hosts)
        self.repo = repo

    def run(self):
        tasks = [
            Task(self.kafka,
                 task,
                 self.state_manager.get_state(task),
                 self.state_manager.get_offset_store(task),
                 self.repo.task_config(task.name)
                 )
            for task in self.tasks]

        greenlets = [gevent.spawn(t.run) for t in tasks]
        gevent.joinall(greenlets, raise_error=True)
