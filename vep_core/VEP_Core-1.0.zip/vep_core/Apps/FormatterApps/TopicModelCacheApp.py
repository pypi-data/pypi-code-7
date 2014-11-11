# coding=utf-8
__author__ = 'kohlmannj'

import os
import json
import codecs
from Ity import metadata_root, corpus_root
from Ity.Utilities import FilePaths
from Ity.Tokenizers import RegexTokenizer
from Ity.Taggers import TopicModelTagger
from Ity.Formatters import HTMLFormatter, LineGraphFormatter
import argparse

if __name__ == "__main__":
    #### Parse Input Arguments ####
    parser = argparse.ArgumentParser(description="Given several file paths as positional arguments, print out \"valid\" paths.")
    parser.add_argument('corpus_name', type=str, metavar='NAME',
                        help="The name of a corpus stored in Ity's Data/Corpora folder.")
    parser.add_argument('-f', '--filename', type=str, nargs='+', metavar='FILENAMES', dest='filenames',
                        help="Optionally, one or more text filenames within the specified corpus (WITH extension!).")
    parser.add_argument('-e', '--extension', type=str, metavar='EXT', dest='file_extension', default='txt',
                        help="The file extension (*without* leading '.') of the files we want to filter paths by.")
    parser.add_argument('--debug', action='store_true', dest='debug',
                        help="Print debugging output.")
    args = parser.parse_args()
    # Get the input files with the appropriate file extension.
    patterns = None
    if args.file_extension is not None:
        patterns = ("\." + args.file_extension + "$",)

    corpus_path = os.path.join(corpus_root, args.corpus_name)

    if args.filenames is not None and len(args.filenames) > 0:
        for index, filename in enumerate(args.filenames):
            args.filenames[index] = os.path.join(corpus_path, filename)
        input_paths = FilePaths.valid_paths(args.filenames, patterns=patterns, recursion_levels=2, debug=args.debug)
    else:
        input_paths = FilePaths.valid_paths(corpus_path, patterns=patterns, recursion_levels=2, debug=args.debug)

    # Initialize Ity modules.
    tokenizer = RegexTokenizer(case_sensitive=True)
    tagger = TopicModelTagger(corpus_name=args.corpus_name)
    formatter = HTMLFormatter()

    # Make sure we have a folder to put things in.
    corpus_output_dir = os.path.join(
        metadata_root,
        args.corpus_name,
        "TopicModel",
        "Serendip"
    )
    if not os.path.exists(corpus_output_dir):
        os.makedirs(corpus_output_dir)

    # Keep calm and DO THINGS
    for path_index, path in enumerate(input_paths):
        # Make a folder on-disk for this text's data.
        text_name = os.path.splitext(os.path.basename(path))[0]
        text_output_dir = os.path.join(
            corpus_output_dir,
            text_name
        )
        if not os.path.exists(text_output_dir):
            os.makedirs(text_output_dir)

        # Open the file and get its contents.
        the_file = codecs.open(path, encoding="utf-8")
        the_str = the_file.read()
        the_file.close()

        # Keep track of file names and content that we're going to write to disk.
        data_to_disk = {
            "tokens.json": None,
            "tag_data_topic_model.json": None,
            "tag_maps_topic_model.json": None,
            "topic_model.html": None,
            "topic_model.html_partial": None,
            "line_graph.svg": None
        }
        # Do we have to do work?!
        paths_exist = []
        for key in data_to_disk.keys():
            paths_exist.append(os.path.exists(os.path.join(text_output_dir, key)))

        all_text_files_exist = reduce(
            lambda a, b: a and b,
            paths_exist
        )

        # Skip this text if all the files already exist.
        # IMPORTANT: The user must dump the files on-disk if something in the
        # Ity modules changes!!!
        if all_text_files_exist:
            print "\tWe can skip '%s' (%u / %u)" % (os.path.basename(path), path_index + 1, len(input_paths))
            continue

        # Tokenize
        tokens = tokenizer.tokenize(the_str)
        tokens_dict = dict(
            tokens=tokens
        )
        data_to_disk["tokens.json"] = json.dumps(tokens_dict)

        # Tag
        tag_data, tag_maps = tagger.tag(tokens, text_name=text_name)
        data_to_disk["tag_data_topic_model.json"] = json.dumps(tag_data)
        data_to_disk["tag_maps_topic_model.json"] = json.dumps(tag_maps)

        # Format
        html_output = formatter.format(
            tags=(tag_data, tag_maps),
            tokens=tokens,
            s=the_str
        )
        data_to_disk["topic_model.html"] = html_output
        html_output_partial = formatter.format(
            tags=(tag_data, tag_maps),
            tokens=tokens,
            s=the_str,
            partial=True
        )
        data_to_disk["topic_model.html_partial"] = html_output_partial

        # Write things we care about out to disk.
        for the_file_name, file_content in data_to_disk.items():
            if file_content is None:
                continue
            the_file_path = os.path.join(text_output_dir, the_file_name)
            the_file = codecs.open(the_file_path, encoding="utf-8", mode="w")
            the_file.write(file_content)
            the_file.close()

        print "\t** Processed '%s' (%u / %u) **" % (os.path.basename(path), path_index + 1, len(input_paths))

    print "** Finished generating TopicModel cached data for corpus '%s'. **" % args.corpus_name
