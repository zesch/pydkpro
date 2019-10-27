#! usr/bin/env python
# -*- coding : utf-8 -*-

from pydkpro.cas import Cas
import os
from pydkpro.server_request import ServerRequest


class Pipeline(object):
    def __init__(self):
        self._pipeline_dict = dict()
        self._components = []

    def _check_format(self):
        keys = [ 'type', 'entity']
        for key in keys:
            if not key in self._pipeline_dict.keys():
                raise KeyError(str(key) + ' is need to be added')

    def _call_microservice(self):
        sr = ServerRequest('localhost')
        return sr.send_request(self._pipeline_dict)

    def add(self, entity):
        if not isinstance(entity, Component):
            raise TypeError('The added entity must be '
                            'an instance of class Component or Casobject. '
                            'Found: ' + str(entity))
        self._components.append(entity().component_obj)
        return self

    def trigger(self):
        self._pipeline_dict['type'] = 'Components'
        self._pipeline_dict['entity'] = self._components
        self._check_format()
        return self._call_microservice()

    def run(self, input_string):
        self._pipeline_dict['type'] = 'payload'
        if isinstance(input_string, str) and os.path.isfile(input_string):
            cas_object = Cas().file_to_cas(input_string)
        elif isinstance(input_string, str):
            cas_object = Cas().string_to_cas(input_string)
        elif isinstance(input_string, Cas):
            if len(input_string.token_list) > 0:
                cas_object = input_string.updateCas()
            else:
                cas_object = input_string
        else:
            raise NotImplementedError
        self._pipeline_dict['entity'] = cas_object.to_xmi()
        self._check_format()
        return self._call_microservice()





class Component(object):
    def __init__(self, name=None, **kwargs):
        #super(Pipeline,self).__init__()
        self.component_obj = dict()
        self.component_name = name
        self.kwags = kwargs

    def __call__(self):
        self.component_obj['name'] = self.component_name
        for key, value in self.kwags.items():
            self.component_obj[key] = value
        return self

    def run(self, string):
        return Pipeline().run(string)



