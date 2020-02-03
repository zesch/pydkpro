#! usr/bin/env python
# -*- coding : utf-8 -*-

from cassis import *
import codecs
import os
import glob
from spacy.tokens import Doc, Span
from spacy.attrs import POS, HEAD, DEP
from spacy.vocab import Vocab


class Pipeline(object):
    def __init__(self):
        #super(Component)
        self._pipeline_dict = dict()
        self._pipeline_dict['components'] = []
        self.cas = Cas()

    def _check_format(self):
        keys = ['components', 'payload']
        for key in keys:
            if not key in self._pipeline_dict.keys():
                raise KeyError(str(key) + ' is need to be added')

    # in original version this function should send request to server and return the response
    def _call_microservice(self):
        # pydkpro/blackbox function defined just for pydkpro purposes only
        print('Building pipeline......')

        with open('TypeSystem.xml', 'rb') as f:
            typesystem = load_typesystem(f)
        self.cas = load_cas_from_xmi(str(self._pipeline_dict['payload']), typesystem=typesystem)
        token_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
        Token = typesystem.get_type(token_type)


        tokens = [
            Token(begin=0, end=5, id='0', pos='DEMO_POS'),
            Token(begin=6, end=9, id='1', pos='DEMO_POS'),
            Token(begin=10, end=13, id='2', pos='DEMO_POS'),
            Token(begin=14, end=17, id='3', pos='DEMO_POS'),
        ]

        for token in tokens:
            self.cas.add_annotation(token)

        for token in self.cas.select(token_type):
            print(self.cas.get_covered_text(token))

            # Annotation values can be accessed as properties
            print('Token: begin={0}, end={1}, id={2}, pos={3}'.format(token.begin, token.end, token.id, token.pos))

        return self.cas

    def add(self, entity):
        if not isinstance(entity, Component):
            raise TypeError('The added entity must be '
                            'an instance of class Component or Casobject. '
                            'Found: ' + str(entity))
        self._pipeline_dict['components'].append(entity().component_obj)
        return self

    def run(self, string):
        if isinstance(string, Cas):
            self._pipeline_dict['payload'] = string.to_xmi()
        elif isinstance(string, Loadfile):
            string = string()
        entity = Casobject(string)
        self._pipeline_dict['payload'] = entity()
        self._check_format()
        return self._call_microservice()

    def trigger(self):
        pass


class Component(Pipeline):
    def __init__(self, name=None, **kwargs):
        super(Pipeline,self).__init__()
        self.component_obj = dict()
        self.component_name = name
        self.kwags = kwargs

    def __call__(self):
        self.component_obj['name'] = self.component_name
        for key, value in self.kwags.items():
            self.component_obj[key] = value
        return self
        #return self.component_obj



class CasHelper(object):
    def __init__(self, cas_obj):
        self.cas = cas_obj
        self.token_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token' # need to change TODO

    def to_spacy(self): # it is more specific function for pydkpro purpose only
        return self.get_doc(words=self.get_tokens(), pos=self.get_pos(), tags=self.get_tags())

    def to_nltk_pos_tagger(self): # it is more specific function for pos tagger of cas and  for pydkpro purpose only
        return self.get_postags()

    def get_tokens(self):
        tokens = [self.cas.get_covered_text(token) for token in self.cas.select(self.token_type)]
        return tokens

    def _get_tags(self, tag_type):
        tags = []
        for token in self.cas.select(self.token_type):
            tags.append((self.cas.get_covered_text(token), token[tag_type]))
        return tags


    def get_postags(self):
        self._get_tags('pos')

    def get_pos(self):
        pos = []
        for token in self.cas.select(self.token_type):
            pos.append(token['POS']['coarseValue'])

    def get_tags(self):
        tags = []
        for token in self.cas.select(self.token_type):
            tags.append(token['POS']['PosValue'])

    def get_lemmas(self):
        self._get_tags('lemma')

    def get_stem(self):
        self._get_tags('stem')

    def get_morph(self):
        self._get_tags('morph')

    def get_doc(self, words=[], pos=None, heads=None, deps=None, tags=None, ents=None):
        """Create Doc object from given vocab, words and annotations."""

        vocab = Vocab()
        pos = pos or [""] * len(words)
        tags = tags or [""] * len(words)
        heads = heads or [0] * len(words)
        deps = deps or [""] * len(words)
        for value in deps + tags + pos:
            vocab.strings.add(value)

        doc = Doc(vocab, words=words)
        attrs = doc.to_array([POS, HEAD, DEP])
        for i, (p, head, dep) in enumerate(zip(pos, heads, deps)):
            attrs[i, 0] = doc.vocab.strings[p]
            attrs[i, 1] = head
            attrs[i, 2] = doc.vocab.strings[dep]
        doc.from_array([POS, HEAD, DEP], attrs)
        if ents:
            doc.ents = [
                Span(doc, start, end, label=doc.vocab.strings[label])
                for start, end, label in ents
            ]
        if tags:
            for token in doc:
                token.tag_ = tags[token.i]
        return doc



class Casobject(object):
    def __init__(self,  string):
        if isinstance(string, list):
            string = ' '.join(string)
        self.cas = Cas()
        self.cas.sofa_mime = "text/plain"
        self.cas.sofa_string = string
        with open('typesystem.xml', 'rb') as f:
            self.typesystem = load_typesystem(f)
        self.sentence = self.typesystem.get_type('uima.tcas.DocumentAnnotation')
        print(string)
        self.cas.add_annotations([
            self.sentence(begin=0, end=len(string)-1)
        ])

    def __call__(self):
        return self.cas.to_xmi()


class Loadfile(object):
    def __init__(self, filename, typesystem_path='TypeSystem.xml'):
        self.filename = filename
        self.string = ''
        self.file_type = file_type
        self.typesystem_path = typesystem_path

    def __call__(self):
        if self.filename.split('.')[-1].strip().lower() == 'xmi': # TODO
            with open(self.typesystem_path, 'rb') as f:
                typesystem = load_typesystem(f)
            with open(str(self.filename), "wb") as f:
                self.string = load_cas_from_xmi(f, typesystem=typesystem)

        else:
            if os.path.isdir(self.filename):
                text_files = [eachfile for eachfile in glob.glob(self.filename + '/*')]
            else:
                text_files = [self.filename]
            for each_file in text_files:
                with codecs.open(each_file, 'r', 'utf-8') as query_doc_obj:
                    for line in query_doc_obj:
                        self.string += line.strip().rstrip('\r\n') # TODO
        return self.string


class Savefile(object):
    def __init__(self):
        pass








def main():


    # case 1 : get tokens and correponding pos tags for the given string using dkpro clearnlp tokenizer
    # and stanford fast41 pos tagger
    p = Pipeline()
    p.add(Component(name='tokenizer', brand='clearnlp', language='en'))
    p.add(Component(name='pos_tagger', brand='stanford', language='en', variant='fast41'))
    mycas = p.run('hello how are you')

    # work with CAS

    # case 1a : display cas string and corresponding tags


    # case 1aa: using cashelper
    ch = CasHelper(mycas)
    print(ch.get_tokens()) # to get tokens
    print(ch.get_postags()) # get pos tags
    print(ch.get_lemmas()) # get lemmas

    # to spacy object
    spacy_doc = ch.to_spacy()
    for token in spacy_doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)

    # to nltk object
    print(ch.to_nltk_pos_tagger())


    # case 1ab : requirement not available in helper, you can use cassis

    for token in mycas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
        print(token)

    # case 1b : save return annotation as cas object in xmi

    mycas.to_xmi(path='.')

    # case 1c : save return annotation as text file.

        #  difficult to do as we dont need which format user need




    # case 2 : use text file instead of given string

    p.run(Loadfile('test2.txt'))

    # case 3 : use xmi file instead of text file and string if it is xmi that directly cas object can be created

    p.run(Loadfile('test.xmi')) # need fix TODO type

    # case 4 use folder path include multiple text files
    for file in folder:
        for String in array:
            CAS = p.run(file)  # return cas object

    p.run([text,text,text])
    p.run( [file for file in folder] )

    # case 5 : get tokens using  nltk TweetTokenizer and get pos tags using dkpro stanford
    # fast41 pos tagger.

    from nltk.tokenize import TweetTokenizer
    p2 = Pipeline()
    p2.add(Component(name='pos_tagger', brand='stanford', language='en', variant='fast41'))
    tknzr = TweetTokenizer()
    #p2.run(Casobject(tknzr.tokenize('hello how are you'))) # TODO csv
    CAS = CAS()
    for token in tknzr.tokenize('hello'):
        Token
        CAS.add(token)


    # case 6 : get individual dkpro component instead of pipeline
    dkppro_tok = Component(name='tokenizer', brand='clearnlp', language='en')

    dkppro_tok.run('hello how are you')  # TODO



    # ISSUE: how to handle consumers / collectionProcessComplete()


if __name__ == '__main__':
    main()



