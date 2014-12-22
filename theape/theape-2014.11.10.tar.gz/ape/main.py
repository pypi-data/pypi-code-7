
# this package
from ape.infrastructure.arguments.argumentbuilder import ArgumentBuilder
from ape.log_setter import set_logger


def enable_debugging(args):
    """
    Enables interactive debugging

    :param:

     - `args`: A namespace with pudb and pdb attributes
    """
    if args.pudb:
        import pudb
        pudb.set_trace()
        return
    if args.pdb:
        import pdb
        pdb.set_trace()
    return


def main():
    """
    The 'site-entry' point.

       1. Gets command-line arguments
       2. Sets the logger
       3. Enables debugging (if asked for)
       4. Calls the function set by the argparse subcommand
    """
    argue = ArgumentBuilder()
    args = argue()
    set_logger(args)
    enable_debugging(args)
    args.function(args)
    return
