# coding=utf-8
__author__ = 'kohlmannj'

import os
import codecs
import argparse
from time import time
from Ity import metadata_root, corpus_root, Tokenizers, Utilities

# Parser Setup
parser = argparse.ArgumentParser(description="Given several file paths as positional arguments, print out \"valid\" paths.")
parser.add_argument('paths', type=str, nargs='+',
                    help="One or more paths a file or a folder of files.")
parser.add_argument('-e', '--extension', type=str, metavar='EXT', dest='file_extension',
                    help="The file extension (*without* leading '.') of the files we want to filter paths by.")
parser.add_argument('--debug', action='store_true', dest='debug',
                    help="Print debugging output.")

# Main Function
if __name__ == "__main__":
    # Parse command line arguments
    args = parser.parse_args()
    # Get the input files with the appropriate file extension.
    patterns = None
    if args.file_extension is not None:
        patterns = ("\." + args.file_extension + "$",)
    input_paths = Utilities.FilePaths.valid_paths(args.paths, patterns=patterns, recursion_levels=2, debug=args.debug)
    # Instantiate Ity modules
    tokenizer = Tokenizers.RegexTokenizer(
        case_sensitive=False,
        keep_original_strs=True,
        debug=args.debug
    )
    # Track some statistics.
    total_duration = 0
    total_num_texts = 0
    total_num_tokens = 0
    num_tokens = [0] * len(input_paths)
    durations = [0] * len(input_paths)
    max_time_index = -1
    min_time_index = -1
    longest_text_index = -1
    shortest_text_index = -1
    # Tokenize the input texts
    print "Tokenizing %u texts..." % len(input_paths)
    for path_index, path in enumerate(input_paths):
        start_time = time()

        # Open the file and get its contents.
        the_file = codecs.open(path, encoding="utf-8")
        the_str = the_file.read()
        the_file.close()
        # Tokenize the file.
        tokens = tokenizer.tokenize(the_str)

        end_time = time()

        if len(tokens) == 0:
            print "\t**** Skipping '%s'...but why? ****" % os.path.basename(path)
            continue

        # Update statistics
        duration = end_time - start_time
        total_duration += duration
        total_num_tokens += len(tokens)
        total_num_texts += 1
        num_tokens[path_index] = len(tokens)
        durations[path_index] = duration
        if duration > durations[max_time_index]:
            max_time_index = path_index
        if duration < durations[min_time_index]:
            min_time_index = path_index
        if len(tokens) > num_tokens[longest_text_index]:
            longest_text_index = path_index
        if len(tokens) < num_tokens[shortest_text_index]:
            shortest_text_index = path_index
        # Print some information.
        print "\t(%u / %u) Tokenized %u tokens in '%s' in %f sec (%f sec/token avg.)" % (
            path_index, len(input_paths),
            len(tokens),
            os.path.basename(path),
            float(duration),
            float(duration) / float(len(tokens))
        )
    # Print summary information.
    print "**** Finished. Tokenized %u texts in %f sec ****" % (
        total_num_texts,
        float(total_duration)
    )
    print "**** Averages: %f sec/text; %f sec/token. ****" % (
        float(total_duration) / total_num_texts,
        float(total_duration) / total_num_tokens
    )
    print "**** Minimum time: '%s'. %f sec for %u tokens (%f sec/token) ****" % (
        os.path.basename(input_paths[min_time_index]),
        float(durations[min_time_index]),
        num_tokens[min_time_index],
        float(durations[min_time_index]) / num_tokens[min_time_index]
    )
    print "**** Maximum time: '%s'. %f sec for %u tokens (%f sec/token) ****" % (
        os.path.basename(input_paths[max_time_index]),
        float(durations[max_time_index]),
        num_tokens[max_time_index],
        float(durations[max_time_index]) / num_tokens[max_time_index]
    )
    print "**** Longest text: '%s'. %f sec for %u tokens (%f sec/token) ****" % (
        os.path.basename(input_paths[longest_text_index]),
        float(durations[longest_text_index]),
        num_tokens[longest_text_index],
        float(durations[longest_text_index]) / num_tokens[longest_text_index]
    )
    print "**** Shortest text: '%s'. %f sec for %u tokens (%f sec/token) ****" % (
        os.path.basename(input_paths[shortest_text_index]),
        float(durations[shortest_text_index]),
        num_tokens[shortest_text_index],
        float(durations[shortest_text_index]) / num_tokens[shortest_text_index]
    )
