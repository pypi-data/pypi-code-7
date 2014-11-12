from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import pairwise_kernels
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from goose import Goose
from scipy import sparse

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
sentence_tokenizer = sent_detector.tokenize
stemmer = PorterStemmer()


class Summarizer:

    def __init__(self, url=None, text=None):

        if (url is None) != (text is None):
            raise SystemExit("Need exactly one of text or url")

        self.url = url
        self.text = text

    def goose_extractor(self):
        '''get article contents'''
        article = Goose().extract(url=self.url)
        return article.title, article.meta_description,\
                                  article.cleaned_text

    def _tokenize(self, sentence):
        '''Tokenizer and Stemmer'''
        tokens = nltk.word_tokenize(sentence)
        tokens = [stemmer.stem(tk) for tk in tokens]
        return tokens

    def _textrank(self, matrix):
        '''return textrank vector'''
        nx_graph = nx.from_scipy_sparse_matrix(sparse.csr_matrix(matrix))
        return nx.pagerank(nx_graph)

    def _summarize(self, full_text, num_sentences=4):
        sentences = sentence_tokenizer(full_text)
        tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english', ngram_range=(1,2))
        norm = tfidf.fit_transform(sentences)
        similarity_matrix = pairwise_kernels(norm, metric='cosine')
        scores = textrank(similarity_matrix)
        scored_sentences = []
        for i, s in enumerate(sentences):
            scored_sentences.append((scores[i],i,s))
        top_scorers = sorted(scored_sentences, key=lambda tup: tup[0], 
                             reverse=True)[:num_sentences]
        return sorted(top_scorers, key=lambda tup: tup[1])

    def summarize_url(self, url, num_sentences=4):
        '''Returns summary for provided url
            parameters: url string, number of sentences
            returns: tuple containing
                        * human summary if contained
                          in article's meta description 
                        * tuple with score, index indicating
                          order in document, sentence string
        '''

        title, hsumm, full_text = self.goose_extractor()
        return hsumm, _summarize(full_text, num_sentences)

    def summarize_text(self, full_text, num_sentences=4):
        return self._summarize(full_text)

