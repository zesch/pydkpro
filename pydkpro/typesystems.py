#! usr/bin/env python3
# -*- coding : utf-8 -*-
"""
@author : aggarwal

"""

from cassis import load_typesystem

class Tok(object):
    def __init__(self, begin=0, end=1, id='0', pos='NNP'):
        self.begin = begin
        self.end = end
        self.id = id
        self.pos = pos




class DKProCoreTypeSystem(object):
    def __init__(self):
        with open('../pydkpro/typesystems/dkpro-core-types.xml', 'rb') as f:
            self.typesystem = load_typesystem(f)

    def __call__(self):
        return self.typesystem

    def token(self, **kwargs):
        return 0


    def sentence(self, **kwargs):
        return 'sentence'


