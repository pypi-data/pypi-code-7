# coding=utf-8
__author__ = 'kohlmannj'

from Ity import Taggers, Tokenizers

if __name__ == "__main__":
    tokenizer = Tokenizers.RegexTokenizer()
    tagger = Taggers.DocuscopeTagger()
    print str(tagger.tag(tokenizer.tokenize('saying that: "')))
