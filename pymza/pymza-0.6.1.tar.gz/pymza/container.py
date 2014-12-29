import logging
import gevent
from kafka import KafkaClient

from .const import SOCKET_TIMEOUT
from .task import Task

logger = logging.getLogger('pymza.container')


class TaskContainer(object):

    def __init__(self, kafka_hosts, tasks, state_manager, repo):
        self.tasks = tasks
        self.state_manager = state_manager
        self.kafka = KafkaClient(kafka_hosts, timeout=SOCKET_TIMEOUT)
        self.repo = repo

    def run(self):
        try:
            self.tasks = [
                Task(self.kafka,
                     task,
                     self.state_manager.get_state(task),
                     self.state_manager.get_offset_store(task),
                     self.repo.task_config(task.name)
                     )
                for task in self.tasks]

            greenlets = [gevent.spawn(t.run) for t in self.tasks]
            gevent.joinall(greenlets, raise_error=True)
        finally:
            self.tasks = []

    def print_stats(self):
        topics = {x for task in self.tasks for x in task.source_topics}

        topic_partitions = [(topic, partition) for topic in topics for partition in self.kafka.get_partition_ids_for_topic(topic)]

        from collections import defaultdict
        from .kafka_utils import get_kafka_offset_range
        server_offsets = defaultdict(dict)
        for topic, partition_id, server_min, server_max in get_kafka_offset_range(self.kafka, topic_partitions):
            server_offsets[topic][partition] = server_max

        for task in sorted(self.tasks, key=lambda x:x.name):
            print task.name


            for topic in sorted(task.source_topics):
                server_topic_offsets = server_offsets[topic]

                for partition_id, server_offset in sorted(server_topic_offsets.items()):
                    task_offset = task.offsets.get(topic, partition_id)
                    lag = server_offset - task_offset
                    print '\t{0}:{1} {2}/{3} ({4} lag)'.format(topic, partition, task_offset, server_offset, lag)
