from gevent import monkey
monkey.patch_all()
import logging
import click
import sys

from .config import Config

pass_config = click.make_pass_decorator(Config, ensure=False)


@click.group()
@click.option('-c', '--config', required=True, help='config file', type=click.Path(file_okay=True, dir_okay=False, exists=True))
@click.option('-l', '--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR']))
@click.pass_context
def main(ctx, config, log_level):
    ctx.obj = Config(config)

    ctx.obj.add_home_to_pythonpath()

    log_level = getattr(logging, log_level)
    logging.basicConfig(level=log_level)
    logging.getLogger('kafka').setLevel(logging.WARN)


@main.command()
@pass_config
def run(config):
    click.echo("running")

    from .container import TaskContainer
    from .state import StateManager

    state_manager = StateManager(config.state_dir())
    tasks = [config.load_task(x) for x in config.tasks()]
    c = TaskContainer(config.kafka_hosts, tasks, state_manager, config)
    c.run()


@main.command()
@pass_config
@click.argument('dotfile', required=True, type=click.Path(file_okay=True, dir_okay=False))
def topology(config, dotfile):
    click.echo("Saving topology to {0}".format(dotfile))

    with open(dotfile, 'w') as f:
        topics = set()

        print >>f, "digraph topology {"
        for task in [config.load_task(x) for x in config.tasks()]:
            print >>f, "task_{0} [label=\"{0}\", tooltip=\"{1}\", shape=box, style=bold]".format(
                task.name, task.description)

            for s in task.source_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "topic_{0} -> task_{1}".format(s, task.name)
            for s in task.result_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "task_{0} -> topic_{1}".format(task.name, s)

        for topic in topics:
            print >>f, "topic_{0} [label=\"{0}\", tooltip=\"{0} topic\", shape=ellipse, style=dashed]".format(
                topic)

        print >>f, "}"

    click.echo(
        "Done. You can run `dot {0}  -Tsvg -o {0}.svg` to convert it to SVG.".format(dotfile))


@main.command()
@pass_config
@click.option('--zookeeper', default='127.0.0.1')
@click.option('--partitions', default=1)
@click.option('--replication-factor', default=1)
def create_topics(config, zookeeper, partitions, replication_factor):
    topics = set()

    for task in [config.load_task(x) for x in config.tasks()]:
        topics.update(task.source_topics)
        topics.update(task.result_topics)

    print >>sys.stderr, "Please run following commands to create topics:"
    for topic in sorted(topics):
        print "./bin/kafka-topics.sh --zookeeper {zookeeper} --create --topic {topic} --replication-factor {replication_factor} --partitions {partitions}".format(**locals())


@main.command()
@click.argument('task_name')
def reset(task_name):
    click.echo("Resetting {0}".format(task_name))

    # stopping
    # resetting state
    # seeking to 0
    # starting


@main.command()
@pass_config
def topics(config):
    topics = set()

    for task in [config.load_task(x) for x in config.tasks()]:
        topics.update(task.source_topics)
        topics.update(task.result_topics)

    for t in sorted(topics):
        print t


@main.command()
@pass_config
@click.argument('task')
def offsets(config, task):

    task = config.load_task(task)
    from .state import StateManager
    state_manager = StateManager(config.state_dir())
    ostore = state_manager.get_offset_store(task)

    from pymza.offset import SimpleOffsetTracker

    offset = SimpleOffsetTracker()
    ostore.load(offset)

    print offset._offsets


@main.command()
@click.option('--kafka', default="localhost:9092")
@click.argument('topic')
def topic_tail(kafka, topic):
    from kafka import KafkaClient, SimpleConsumer

    kafka = KafkaClient(kafka)

    consumer = SimpleConsumer(
        kafka, "my-group", str(topic), auto_commit=False, max_buffer_size=10 * 1024 * 1024)
    consumer.provide_partition_info()
    consumer.seek(0, 0)
    click.echo(
        "Tailing {0}, {1} messages pending".format(topic, consumer.pending()))
    for partition, message in consumer:
        print 'k:', message.message.key
        print 'v:', message.message.value
        print

    kafka.close()

if __name__ == '__main__':
    main()
