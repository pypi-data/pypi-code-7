from __future__ import division

import logging
import os
import random
import time

# Set up logger
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
log.addHandler(ch)

# Word list file path info
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORD_LIST_FILENAME = 'word_list_en.txt'
WORD_LIST_PATH = os.path.join(BASE_DIR,'resources', WORD_LIST_FILENAME)

# Times
UNIX_EPOCH_SECONDS = int(time.time())
ONE_YEAR_SECONDS = int(60 * 60 * 24 * 365.25)
HUMANKIND_SECONDS = ONE_YEAR_SECONDS * 200000
UNIVERSE_SECONDS = ONE_YEAR_SECONDS * 13800000000

_word_list = None


class NoWordsMeetCriteriaException(BaseException):
    pass


def get_word_list():
    """
    Returns the word list currently residing in memory or loads
    the word list from txt file if not found.

    Args:
        None
    Returns:
        The words contained in word_list_en.txt split into a list
        by line.
    Raises:
        IOError: Word list file not found
    """
    global _word_list
    if _word_list is None:
        log.debug('No word list resident in memory, reading from file')
        with open(WORD_LIST_PATH, 'r') as f:
            log.debug('Opening {}...'.format(WORD_LIST_PATH))
            _word_list = [word.strip() for word in f.readlines()]
            log.debug('{} word list read into memory'.format(len(_word_list)))
    return _word_list

def generate(num_words=4,min_length=None,max_length=None,with_underscores=True,
        log_level=logging.INFO):
    """
    Generates a passphrase consisting of num_words words.

    Args:
        num_words: The number of words the passphrase should contain
        min_length: The minimum length of the words to consider when
            selecting from the word list.
        max_length: The maximum length of the words to consider when
            selecting from the word list.
        log_level: The level of detail the function will log
        with_underscores: Inserts underscores into passphrase at word
            boundaries for improved readability. On by default.
    Returns:
        The passphrase as a byte string.
    Raises:
        NoWordsMeetCriteriaException: The combination of min_length
            and max_length eliminates all
    """
    log.setLevel(log_level)

    passphrase = ""
    join_with = "_" if with_underscores else ""
    words = get_word_list()
    words_len = len(words)
    if min_length is not None:
        log.info("Eliminating all words less than {} characters in length...".format(min_length))
        words = [word for word in words if len(word) >= min_length]
        log.info("{} words removed from list of candidates.".format(words_len - len(words)))
        words_len = len(words)
    if max_length is not None:
        log.info("Eliminating all words greater than {} characters in length...".format(max_length))
        words = [word for word in words if len(word) <= max_length]
        log.info("{} words removed from list of candidates.".format(words_len - len(words)))
        words_len = len(words)

    if len(words) == 0:
        raise NoWordsMeetCriteriaException('No words found given min and max lengths')

    log.info("Generating passphrase of length {} from {} candidate words...".format(num_words, words_len))
    passphrase = join_with.join(random.choice(words) for i in xrange(num_words))
    passphrase_space = words_len**num_words
    seconds_to_search = int(passphrase_space / 1000000000)
    log.info("Passphrase generated.")
    log.info("Number of possible passphrases with given length and constraints: {:,}".format(passphrase_space))
    log.info("Time required to try all combinations at speed of 1 billion attempts/second: {:,}s".format(seconds_to_search))
    log.info("For the sake of comparison, here are several other lengths of time:")
    log.info("Seconds in one year: {:,}s".format(ONE_YEAR_SECONDS))
    log.info("Seconds since UNIX epoch (Jan 1, 1970 12:00:00am): {:,}s".format(UNIX_EPOCH_SECONDS))
    log.info("Seconds since humans emerged as a distinct species: {:,}s".format(HUMANKIND_SECONDS))
    log.info("Seconds since the universe formed: {:,}s".format(UNIVERSE_SECONDS))

    if seconds_to_search < 60*60*24*365*5:
        log.warn("Time required to exhaust space of all possibilities is less than 10 years")
    return passphrase
