#! usr/bin/env python3
# -*- coding : utf-8 -*-
"""
@author : aggarwal

"""

from cassis import TypeSystem

class Tok(object):
    def __init__(self, begin=0, end=1, id='0', pos='NNP'):
        self.begin = begin
        self.end = end
        self.id = id
        self.pos = pos




class DKProCoreTypeSystem(object):
    def __init__(self):
        pass

    def token(self, **kwargs):
        return 0


    def sentence(self, **kwargs):
        return 'sentence'


