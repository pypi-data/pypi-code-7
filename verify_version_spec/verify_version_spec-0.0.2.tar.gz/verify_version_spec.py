"""verify_version_spec

Usage: verify_version_spec --spec=<spec> <target> [<ignored> ...]

Options:
  --spec=<spec>     Set the version specification to match the target against. Example: ">=0.9,<0.10"
  -h --help         Show this screen.

Verify that a version specification matches the target version string.

"""

import sys
import logging

from docopt import docopt
import semantic_version

logging.basicConfig(level=logging.INFO,
                    format='%(message)s')

logger = logging.getLogger('verify_version_spec')

def main():
    args = docopt(__doc__)

    spec = semantic_version.Spec(args.get('--spec'))
    target = semantic_version.Version.coerce(args.get('<target>'))

    if (spec.match(target)):
        sys.exit(0)
    else:
        logger.info("The version '%s' doesn't match the specification: '%s'" % (target, spec))
        sys.exit(1)

if __name__ == "__main__":
    main()
