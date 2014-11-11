# coding=utf-8
__author__ = 'kohlmannj'

import os
import codecs
import gzip
from string import punctuation
from Ity import data_root, Tokenizers, Taggers, Formatters

use_gzip = False

# Paths to stuff
input_root = os.path.join(data_root, "Testing", "input")
output_root = os.path.join(data_root, "Testing", "output", "HTMLFormatterTest")
# Create the output directory if it doesn't exist.
if not os.path.exists(output_root):
    os.makedirs(output_root)

sample_file_name = "Hamlet rev Boogered.txt"
sample_file_path = os.path.join(input_root, sample_file_name)

# VEP_Core Instances
tokenizer = Tokenizers.RegexTokenizer(debug=True)
# tagger = Tokenizers.TopicModelTagger(debug=True)
formatter = Formatters.HTMLFormatter(debug=True, standalone=True)

if __name__ == "__main__":
    # Open a sample text file to tokenize
    f = codecs.open(sample_file_path, encoding='utf-8')
    s = f.read()
    f.close()
    # Tokenize the text.
    tokens = tokenizer.tokenize(s)
    # Format the text as HTML.
    html = formatter.format(tokens=tokens, s=s)
    # Write the HTML to disk.
    output_file_extension = ".html"
    if use_gzip:
        output_file_extension += ".gz"
    output_file_path = os.path.join(output_root, os.path.splitext(sample_file_name)[0] + output_file_extension)
    if use_gzip:
        output_file = gzip.open(output_file_path, "wb")
    else:
        output_file = open(output_file_path, "wb")
    output_file.write(html.encode("utf-8"))
    output_file.close()
