# coding=utf-8
__author__ = 'kohlmannj'

import os
from string import punctuation
from Ity import data_root, Tokenizers, Taggers

# if __name__ == "__main__":
# Paths to stuff
output_root = os.path.join(data_root, "Testing", "output", "DocuscopeTaggerTests")
# Create the output directory if it doesn't exist.
if not os.path.exists(output_root):
    os.makedirs(output_root)

########################################
#### Stuff you might want to change ####
########################################s
write_to_disk = True

# Instantiate a Tokenizer.
the_tokenizer = Tokenizers.RegexTokenizer()

# Instantiate a DocuscopeTagger.
print "Reading Doscuscope dictionary..."
the_tagger = Taggers.DocuscopeTagger()

# Generate a list of all Docuscope rules that contain words with trailing punctuation.
ds_unique_long_rules_with_trailing_punctuation = []
for long_rules_dict in the_tagger._ds_dict.rules.values():
    for key, value in long_rules_dict.items():
        # Is the last char of the key a punctuation character?
        # Also, is this a unique rule?
        if key[-1] in punctuation and (
                    key[0:-1] not in long_rules_dict or
                    long_rules_dict[key][0][0] != long_rules_dict[key[0:-1]][0][0]
        ):
            rule_str = " ".join(value[0][1])
            ds_unique_long_rules_with_trailing_punctuation.append((value[0][0], rule_str))
            ds_unique_long_rules_with_trailing_punctuation.append((the_tagger.notword_rule, "\n"))
# Concatenate all the rule strings into one big string.
big_str = ""
for rule_tuple in ds_unique_long_rules_with_trailing_punctuation:
    big_str += rule_tuple[1]
# Tokenize and tag the big string with RegexTokenizer.
tokens = the_tokenizer.tokenize(big_str)
# Tag the tokens with DocuscopeTagger.
tags, tag_maps = the_tagger.tag(tokens)
# Output the tokens to files for further comparison.
if write_to_disk:
#     print "Writing %u tokens to text file..." % len(tokens)
#     # Write tokens to disk.
#     tokenizer_name = "RegexTokenizer"
#     tokens_file_path = os.path.join(output_root, "tokens_%s.txt" % tokenizer_name)
#     tokens_file = open(tokens_file_path, "w")
#     for token in tokens:
#         print >>tokens_file, str(token)
#     tokens_file.close()
#     print "Wrote %s to disk." % tokens_file_path

    # tagger_name = "DocuscopeTagger"
    # tags_file_path = os.path.join(output_root, "tag_maps_%s.txt" % tagger_name)
    # tags_file = open(tags_file_path, "w")

    max_tag_maps = -1
    if max_tag_maps < 0 or len(tag_maps) < max_tag_maps:
        max_tag_maps = len(tag_maps)

    # print "Writing a maximum of %u tag maps to text file..." % max_tag_maps

    for i in range(0, max_tag_maps):
        tag_map = tag_maps[i]
        tag_map_tag_keys_list = [the_tuple[0] for the_tuple in tag_map["tag_keys"]]
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
        if (
            ds_unique_long_rules_with_trailing_punctuation[i][0] not in tag_map_tag_keys_list
        ):
            raise StandardError("Couldn't correctly tag a multi-token string with a rule containing a word with trailing punctuation!")
        else:
            print "\nPassed self.tag_maps[%u] = %s" % (i, str(token_strs))
    # tags_file.close()
    # print "Wrote %s to disk." % tags_file_path
