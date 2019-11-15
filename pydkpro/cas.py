#! usr/bin/env python
# -*- coding : utf-8 -*-

from cassis import Cas as cs
from cassis import load_typesystem, load_cas_from_xmi
from spacy.tokens import Doc, Span
from spacy.attrs import POS, HEAD, DEP
from spacy.vocab import Vocab
import codecs
import subprocess
import shlex
import os

class Cas(object):
    def __init__(self, cas_path=None, type_system_path='pydkpro/typesystems/temp_TypeSytems.xml', token_type='de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'):
        self.cas_path = cas_path
        self.type_system_path = type_system_path
        self.token_type = token_type
        self.token_list = []
        with open(self.type_system_path, 'rb') as f:
            self.typesystem = load_typesystem(f)
        if cas_path:
            with open(self.cas_path , 'rb') as f:
                self.cas = load_cas_from_xmi(f, typesystem=self.typesystem)
        else:
            self.cas = cs(typesystem = self.typesystem)
            self.cas.sofa_mime = "text/plain"
            self.cas.sofa_string = ""

    def add_token(self, string_token):
        self.token_list.append(string_token)
        return self

    def updateCas(self):
        Token = self.typesystem.get_type(self.token_type)
        self.cas.sofa_string = ' '.join(self.token_list)
        begin_tok = 0
        for tok in self.token_list:
            self.cas.add_annotations([
                Token(begin=begin_tok, end=begin_tok+len(tok))
            ])
            begin_tok += len(tok) + 1
        return self

    def sofa_string(self):
        return self.cas.sofa_string


    def select_all(self):
        return self.cas.select_all()

    def from_xmi(self, xmi_string):
        self.cas = load_cas_from_xmi(xmi_string, typesystem=self.typesystem)
        return self

    def from_xmi_path(self):
        return self

    def to_xmi(self):
        return self.cas.to_xmi()

    def string_to_cas(self, string):
        self.sentence = self.typesystem.get_type('uima.tcas.DocumentAnnotation')  # TODO for pydkpro only
        self.cas.sofa_string = string
        self.cas.add_annotations([
            self.sentence(begin=0, end=len(string)-1)
        ])
        return self

    def file_to_cas(self, filepath):
        # TODO below code is implemented for pydkpro purpose only
        in_text = filepath
        ts_xml = 'pydkpro/typesystems/temp_TypeSytems_textToXMI.xml'
        log_path = 'pydkpro/test_data/textToXMI.log'
        cmd = shlex.split(
            "java -jar pydkpro/pydkpro-0.0.1-SNAPSHOT-standalone_textXMI.jar %s %s %s" % (in_text, os.path.dirname(in_text), ts_xml))
        if os.path.exists(in_text + '.xmi'):
            os.remove(in_text + '.xmi')
        with codecs.open(log_path, 'w', 'utf-8') as f:
            p = subprocess.Popen(cmd, stdout=f, stderr=f)
            p.wait()
        with open(ts_xml, 'rb') as f:
            self.typesystem = load_typesystem(f)
        with open(in_text + '.xmi', 'rb') as f:
            self.cas = load_cas_from_xmi(f, typesystem=self.typesystem)
        os.remove(in_text + '.xmi')
        return self

    def update(self):
        if self.cas_path:
            self.cas.to_xmi(path=self.cas_path)
        else:
            raise NotImplementedError

    def to_spacy(self):         # it is more specific function for pydkpro purpose only
        return self.get_doc(words=self.get_tokens(), pos=self.get_pos(), tags=self.get_tags())

    def to_nltk_pos_tagger(self):     # it is more specific function for pos tagger of cas and  for pydkpro purpose only
        return self.get_postags()

    def get_text(self):
        return self.cas.sofa_string

    def get_tokens(self):
        tokens = [self.cas.get_covered_text(token) for token in self.cas.select(self.token_type)]
        return set(tokens)

    def _get_tags(self, tag_type):
        tags = []
        for token in self.cas.select(self.token_type):
            tags.append((self.cas.get_covered_text(token), getattr(token, tag_type)))
        return tags

    def get_postags(self):
        tags = []
        for token in self.cas.select(self.token_type):
            tags.append((self.cas.get_covered_text(token), getattr(getattr(token, 'pos'),'PosValue')))
        return set(tags)

    def get_pos(self):
        pos = []
        for token in self.cas.select(self.token_type):
            if getattr(getattr(token, 'pos'),'coarseValue') is None:
                pos.append('')
            else:
                pos.append(getattr(getattr(token, 'pos'),'coarseValue'))
        return pos

    def get_tags(self):
        tags = []
        for token in self.cas.select(self.token_type):
            tags.append(getattr(getattr(token, 'pos'),'PosValue'))
        return tags

    def get_lemmas(self):
        return self._get_tags('lemma')

    def get_stem(self):
        return self._get_tags('stem')

    def get_morph(self):
        return self._get_tags('morph')

    def get_doc(self, words=None, pos=None, heads=None, deps=None, tags=None, ents=None):
        """Create Doc object from given vocab, words and annotations."""

        if words is None:
            words = []
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