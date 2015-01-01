""" sample docstring

$DESCRIPTION

$AUTHOR

"""

# sample import
import argparse
from Logger import logger


def main():
    """ A sample main method """
    logger.critical("critical")
    logger.error("error")
    logger.warning("warning")
    logger.info("info")
    logger.debug("debug")
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="$DESCRIPTION")
    exit(main())
