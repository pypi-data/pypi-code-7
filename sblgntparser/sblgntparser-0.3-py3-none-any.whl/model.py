class Text():
    def __init__(self, sentences, author, bookindex):
        self._sentences = sentences
        self._bookindex = bookindex

    def bookindex(self):
        return self._bookindex

    def sentences(self):
        for sentence in self._sentences:
            yield sentence

    def __len__(self):
        return len(self._sentences)

    def find(self, sought, view='lemma'):
        hits = []
        for sentence in self._sentences:
            hits += sentence.find(sought, view)
        return hits

    def words(self):
        for sentence in self._sentences:
            for word in sentence.words():
                yield word

    def __str__(self):
        return ' '.join([ word.views['text'] for word in self.words() ])

class Sentence():
    def __init__(self, wordlist):
        if wordlist:
            self.wordlist = wordlist
        else:
            self.wordlist = []

    def append(self, word):
         self.wordlist.append(word)

    def find(self, sought, view='lemma'):
        for word in self.wordlist:
            if sought == word.views[view]:
                yield word

    def words(self):
        return self.wordlist

    def __len__(self):
        return len(self.wordlist)

    def __str__(self):
        return ' '.join([ str(word) for word in self.wordlist ])

class Word():
    def __init__(self, word, sentence, position):
        self.textpos = word['text_position']
        self.book = word['book']
        self.chapter = word['chapter']
        self.verse = word['verse']
        self.part_of_speech = word['part_of_speech']
        self.codes = word['codes']
        self.views = word['views']
        self._sentence = sentence
        self._position = position

    def __str__(self):
        return self.views['text']

    def sentence(self):
        return self._sentence

    def position(self):
        return self._position

    def neighbors(self):
        p = self._position
        if 0 == self._position:
            return {
                'left': None,
                'right': self._sentence.words()[p+1]
            }
        elif 0 < self._position < len(self._sentence) - 1:
            return {
                'left':  self._sentence.words()[p-1],
                'right': self._sentence.words()[p+1]
            }
        else:
            return {
                'left': self._sentence.words()[p-1],
                'right': None
            }