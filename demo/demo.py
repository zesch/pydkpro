#! usr/bin/env python
# -*- coding : utf-8 -*-

from cassis import *

class Component(object):
    def __init__(self, name=None, **kwargs):
        self.component_obj = dict()
        self.component_name = name
        self.kwags = kwargs

    def __call__(self):
        self.component_obj['name'] = self.component_name
        for key, value in self.kwags.items():
            self.component_obj[key] = value
        return self.component_obj


class Casobject(object):
    def __init__(self,  string):
        with open('TypeSystem.xml', 'rb') as f:
            self.typesystem = load_typesystem(f)
        self.cas = Cas()
        self.cas.sofa_mime = "text/plain"
        self.Token = self.typesystem.get_type('uima.tcas.Annotation')
        self.cas.sofa_string = string

    def __call__(self):
        return self.cas.to_xmi()


class Pipeline(object):
    def __init__(self):
        super(Pipeline, self).__init__()
        self._pipeline_dict = dict()
        self._pipeline_dict['components'] = []

    def _check_format(self):
        keys = ['components', 'payload']
        for key in keys:
            if not key in self._pipeline_dict.keys():
                raise KeyError(str(key) + ' is need to be added')

    def _call_microservice(self):
        return self._pipeline_dict # need to change

    def add(self, entity):
        if not isinstance(entity, Component):
            raise TypeError('The added entity must be '
                            'an instance of class Component or Casobject. '
                            'Found: ' + str(entity))
        self._pipeline_dict['components'].append(entity())
        return self

    def run(self, string):
        entity = Casobject(string)
        self._pipeline_dict['payload'] = entity()
        self._check_format()
        return self._call_microservice()








