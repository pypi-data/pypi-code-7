# coding=utf-8
__author__ = 'kohlmannj'

import os
from Ity import data_root, Tokenizers, Taggers

# if __name__ == "__main__":
# Paths to stuff
input_root = os.path.join(data_root, "Testing", "input")
output_root = os.path.join(data_root, "Testing", "output", "TopicModelTaggerApp")
# Create the output directory if it doesn't exist.
if not os.path.exists(output_root):
    os.makedirs(output_root)

########################################
#### Stuff you might want to change ####
########################################s
write_to_disk = True
sample_file_path = os.path.join(input_root, "Hamlet rev Boogered.txt")

# Instantiate a Tokenizer.
the_tokenizer = Tokenizers.RegexTokenizer(debug=True)

# Instantiate a Tagger.
the_tagger = Taggers.TopicModelTagger("Blei_AP",debug=True)

# Open a sample text file to tokenize.
# sample_file_path = os.path.join(input_root, "Hamlet rev.txt")
sample_file = open(sample_file_path, "rU")
sample_file_string = sample_file.read()
sample_file.close()

# Tokenize the text with RegexTokenizer.
tokens = the_tokenizer.tokenize(sample_file_string)

# Tag the tokens with DocuscopeTagger.
tags, tag_maps = the_tagger.tag(tokens)

# Output the tokens to files for further comparison.
if write_to_disk:
    print "Writing %u tokens to text file..." % len(tokens)
    # Write tokens to disk.
    tokenizer_name = "RegexTokenizer"
    tokens_file_path = os.path.join(output_root, "tokens_%s.txt" % tokenizer_name)
    tokens_file = open(tokens_file_path, "w")
    for token in tokens:
        print >>tokens_file, str(token)
    tokens_file.close()
    print "Wrote %s to disk." % tokens_file_path

    tagger_name = "TopicModelTagger"
    tags_file_path = os.path.join(output_root, "tag_maps_%s.txt" % tagger_name)
    tags_file = open(tags_file_path, "w")

    max_tag_maps = -1
    if max_tag_maps < 0 or len(tag_maps) < max_tag_maps:
        max_tag_maps = len(tag_maps)

    print "Writing a maximum of %u tag maps to text file..." % max_tag_maps

    for i in range(0, max_tag_maps):
        tag_map= tag_maps[i]
        tokens_for_tag = []
        token_range = range(tag_map["index_start"], tag_map["index_end"] + 1)
        # Just starting...token_pos could be 0 for the very first token.
        prev_token_pos = -1
        for token_index in token_range:
            token = tokens[token_index]
            token_pos = token[Tokenizers.Tokenizer.INDEXES["POS"]]
            if token_pos < tag_map["pos_start"] or token_pos > tag_map["pos_end"] or token_pos <= prev_token_pos:
                break
            else:
                tokens_for_tag.append(token)
                prev_token_pos = token_pos

        if len(tokens_for_tag) != tag_map["len"]:
            raise StandardError("Couldn't reliably retrieve tokens for this tag. The token list is pretty messed up.")

        token_strs = [token[Tokenizers.Tokenizer.INDEXES["STRS"]][-1] for token in tokens_for_tag]
        token_strs_joined = "".join(token_strs)
        print >>tags_file, "\"%s\":\n\t%s\n" % (token_strs_joined, str(tag_map))
    tags_file.close()
    print "Wrote %s to disk." % tags_file_path
