import click
from ghform.config import Config
from ghform.github import Repo, Pull, Tracker
from ghform.form import Form

pass_config = click.make_pass_decorator(Config, ensure=True)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """A command line tool for generating forms, adding them to GitHub
    pull requests or issues, and tracking them.
    """
    pass

@cli.command()
@pass_config
@click.option('--token', prompt='GitHub access token',
              help="The token to be used for GitHub access.")
@click.option('--tracker', prompt='Tracking repo (org/repo)',
              help=("The repo (format as 'org/repo') where forms will be"
                    " tracked."))
@click.argument('repo')
def init(config, token, tracker, repo):
    """Setup ghform for REPO (format as 'org/repo').
    """

    # Ensure the passed token gives access to the passed repo_url
    repo_obj = Repo(repo, token)
    # Clone the tracking repo down to the local tracking path
    tracker_obj = Tracker(tracker)
    tracker_obj.clone()
    # Save the configuration
    config[repo] = {'token': token, 'tracker': tracker}

@cli.command()
@click.option('--tracker', prompt='Tracker to add tpl to (org/repo)',
              help=("The tracking repo (format as org/repo) to add the"
                    " template to."))
@click.argument('tpl', type=click.Path(exists=True, dir_okay=False))
def addtpl(tracker, tpl):
    """Add template at path TPL to TRACKER (format as org/repo).
    """

    # Get the tracker
    tracker = Tracker(tracker)
    # Add the template to the tracker repo
    tracker.add_tpl(tpl)

@cli.command()
@pass_config
@click.option('--tpl', prompt='Template',
              help="The name of the template to use when creating the form.")
@click.argument('pr')
def add(config, tpl, pr):
    """Comment on PR (org/repo/pull/##) with a form created from TPL.
    """

    # Parse arguments into usable pieces
    owner, name, typ, number = pr.split('/')
    repo_ghname = '/'.join([owner, name])

    # Get repo, tracker, pull, and form objects
    repo = Repo(repo_ghname, config[repo_ghname]['token'])
    tracker = Tracker(config[repo_ghname]['tracker'])
    pull = Pull(number, repo)
    form = Form(tpl, repo, tracker, pull)

    # Get users answers
    form.get_responses(pull)

    # Output form data to json, md, html, and png
    form.write_json()
    form.write_md()
    form.write_html()
    form.write_png()

    # Add all those files to the tracker and push them up
    tracker.git.pull()
    msg = 'Add {} json, md, html, and png'.format(form.formname)
    tracker.add_commit_push(msg)

    # Add form to pull comments
    pull.add_form(form, tracker)

    # Perform form response appropriate actions
    pull.do_form_actions(form, repo)
