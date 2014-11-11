# coding=utf-8
__author__ = 'kohlmannj'

import os
from Ity import data_root, Tokenizers

write_tokens_to_disk = True
test_docuscope_tagger = False

input_root = os.path.join(data_root, "Testing", "input")
output_root = os.path.join(data_root, "Testing", "output", "TokenizerTestApp")
# Create the output directory if it doesn't exist.
if not os.path.exists(output_root):
    os.makedirs(output_root)

sample_file_path = os.path.join(input_root, "Hamlet rev Boogered.txt")

if __name__ == "__main__":
    # Open a sample text file to tokenize
    f = open(sample_file_path, "rU")
    s = f.read()
    f.close()
    # Get the tokens
    tokens = {
        "regex": Tokenizers.RegexTokenizer(
            case_sensitive=False,
            keep_original_strs=True,
            excluded_token_types=(
                Tokenizers.Tokenizer.TYPES["WHITESPACE"],
            ),
            remove_hyphen_breaks=True,
            condense_newlines="\n"
        ).tokenize(s),
        "wordbreaker": Tokenizers.WordTokenizer().tokenize(s)
    }
    # Output the tokens to files for further comparison.
    if write_tokens_to_disk:
        for tokenizer_name, tokens in tokens.items():
            token_file_path = os.path.join(output_root, "tokens_%s.txt" % tokenizer_name)
            token_file = open(token_file_path, "w")
            for token in tokens:
                # Don't output newline tokens
                if token[0][0] != "\n":
                    print >>token_file, str(token)
            token_file.close()
            print "Wrote tokens_%s.txt to disk." % tokenizer_name
