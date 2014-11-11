# coding=utf-8
__author__ = 'kohlmannj'

import argparse
import os
import codecs
import json
from Ity import corpus_root
from Ity.Utilities import FilePaths


if __name__ == "__main__":
    #### Parse Input Arguments ####
    parser = argparse.ArgumentParser(
        description="Extract hotel reviews from a JSON file as a folder of text files."
    )
    parser.add_argument(
        'paths',
        type=str,
        nargs='+',
        help="A path to a folder of JSON files."
    )
    parser.add_argument(
        '-e',
        '--extension',
        type=str,
        metavar='EXT',
        dest='file_extension',
        default='json',
        help="The file extension (*without* leading '.') of the files we want to filter paths by."
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        dest='debug',
        help="Print debugging output."
    )
    parser.add_argument(
        "--single-corpus",
        action="store_true",
        dest="single_corpus",
        help="Write reviews from multiple JSON files to a single corpus folder."
    )
    #### Actually Do Things ####
    args = parser.parse_args()
    # Get the input files with the appropriate file extension.
    patterns = None
    if args.file_extension is not None:
        patterns = ("\." + args.file_extension + "$",)
    input_paths = FilePaths.valid_paths(
        args.paths,
        patterns=patterns,
        recursion_levels=2,
        debug=args.debug
    )
    for path in input_paths:
        # Open the JSON file and get its contents.
        path_dict = None
        try:
            json_file = codecs.open(
                path,
                encoding="utf-8"
            )
            path_dict = json.load(json_file)
            json_file.close()
        except (IOError, ValueError) as e:
            # Skip this file.
            if args.debug:
                print e
            continue
        # Skip this file if we have no contents, we have no "reviews" key, or we have no reviews.
        if (
            path_dict is None or
            "reviews" not in path_dict or
            type(path_dict["reviews"]) is str or
            len(path_dict["reviews"]) == 0
        ):
            continue
        # Create a folder in corpus_root based on the name of this JSON file.
        file_base_name = os.path.splitext(
            os.path.basename(path)
        )[0]
        if not args.single_corpus:
            folder_path = os.path.join(
                corpus_root,
                file_base_name
            )
            # Create the corpus folder if it doesn't exist.
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        print "**** Importing corpus '%s'... ****" % file_base_name
        # Extract each review as a text file.
        for review in path_dict["reviews"]:
            # Skip this review if it has no id or text.
            if (
                "id" not in review or
                "text" not in review
            ):
                continue
            try:
                # Use just the review ID as its filename.
                review_base_name = review["id"]
                review_file_path = os.path.join(
                    folder_path,
                    str(review_base_name) + ".txt"
                )
            except NameError:
                review_base_name = file_base_name + "_" + str(review["id"])
                review_file_path = os.path.join(
                    corpus_root,
                    "HotelReviews",
                    review_base_name + ".txt"
                )
            # Open the file and write its contents.
            review_file = codecs.open(
                review_file_path,
                mode="w",
                encoding="utf-8"
            )
            review_file.write(review["text"])
            review_file.close()
            print "\t** Wrote '%s' to corpus folder. **" % (
                os.path.basename(review_file_path)
            )
        print "**** Completed import of '%s' corpus. ****\n" % file_base_name
