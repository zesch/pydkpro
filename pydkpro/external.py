#! usr/bin/env python
# -*- coding : utf-8 -*-

import spacy
import nltk
from pydkpro.cas import Cas

class To_spacy(object):
    def __init__(self, cas):
        self.cas = cas

    def __call__(self):
        nlp = spacy.load("en_core_web_sm")
        text = 'Backgammon is one of the oldest known board games.'
        doc = nlp(text)
        return doc


class From_spacy(object):
    def __init__(self, arg):
        pass
    def __call__(self):
        return Cas()

class To_nltk(object):
    def __init__(self):
        pass
    def tagger(self, arg):
        return [('Backgammon', 'NNP'), ('is', 'VBZ'), ('one', 'CD'), ('of', 'IN'), ('the', 'DT'), ('oldest', 'JJS'), ('known', 'VBN'), ('board', 'NN'), ('games', 'NNS'), ('.', '.')]


class From_nltk(object):
    def __init__(self):
        pass
    def tokenizer(self, abc):
        return Cas()

class File2str(object):
    def __init__(self, arg):
        pass
    def __call__(self):
        return Cas()