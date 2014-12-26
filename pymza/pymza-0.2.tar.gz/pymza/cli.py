from gevent import monkey; monkey.patch_all()
import logging
import click

from .repo import Repo

pass_repo = click.make_pass_decorator(Repo, ensure=False)


@click.group()
@click.option('--repo', required=True, help='number of greetings', type=click.Path(file_okay=False, exists=True))
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR']))
@click.pass_context
def main(ctx, repo, log_level):
    import sys
    sys.path.append(repo)

    ctx.obj = Repo(repo)

    log_level = getattr(logging, log_level)
    logging.basicConfig(level=log_level)
    logging.getLogger('kafka').setLevel(logging.WARN)


@main.command()
@pass_repo
def run(repo):
    click.echo("running")


    from .container import TaskContainer
    from .state import StateManager

    state_manager = StateManager(repo.state_dir())
    tasks = [repo.load_task(x) for x in repo.tasks()]
    c = TaskContainer(tasks, state_manager)
    c.run()


@main.command()
@pass_repo
@click.argument('dotfile', required=True, type=click.Path(file_okay=True, dir_okay=False))
def topology(repo, dotfile):
    click.echo("Saving topology to {0}".format(dotfile))

    with open(dotfile, 'w') as f:
        topics = set()

        print >>f, "digraph topology {"
        for task in [repo.load_task(x) for x in repo.tasks()]:
            print >>f, "task_{0} [label=\"{0}\", tooltip=\"{1}\", shape=box, style=bold]".format(task.name, task.description)

            for s in task.source_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "topic_{0} -> task_{1}".format(s, task.name)
            for s in task.result_topics:
                if s not in topics:
                    topics.add(s)
                print >>f, "task_{0} -> topic_{1}".format(task.name, s)

        for topic in topics:
            print >>f, "topic_{0} [label=\"{0}\", tooltip=\"{0} topic\", shape=ellipse, style=dashed]".format(topic)

        print >>f, "}"

    click.echo("Done. You can run `dot {0}  -Tsvg -o {0}.svg` to convert it to SVG.".format(dotfile))

@main.command()
@click.argument('task_name')
def reset(task_name):
    click.echo("Resetting {0}".format(task_name))

    # stopping
    # resetting state
    # seeking to 0
    # starting

if __name__ == '__main__':
    main()