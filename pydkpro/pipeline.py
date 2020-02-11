#! usr/bin/env python
# -*- coding : utf-8 -*-

from pydkpro.cas import Cas
import os
from pydkpro.server_request import ServerRequest
import codecs
from generate_basic_pipeline import build_pipeline
from dkpro_cli import cliDefinition, killAllRunningContainers
import requests
import json
from yaspin import yaspin
requests.exceptions.ConnectionError


CWD = os.path.abspath(os.path.join('../pydkpro'))

class Pipeline(object):
    def __init__(self, version="2.0.0", language='en'):
        self._pipeline_dict = dict()
        self._components = []
        self.version = version
        self.language = language
        self.component_path = os.path.join(CWD, "dictionaries/class_entries.txt")
        self.component_list = self._load_components()
        self.component_seqid = 0

    def _load_components(self):
        component_list = {}
        with codecs.open(self.component_path, 'r', 'utf-8') as component_obj:
            for line in component_obj:
                line = line.strip().replace('\n','').rstrip('\r\n').split(',')
                component_list[line[0]] = line[1:]
        return component_list

    def _check_format(self):
        keys = [ 'type', 'entity']
        for key in keys:
            if not key in self._pipeline_dict.keys():
                raise KeyError(str(key) + ' is need to be added')

    def _call_microservice(self):
        sr = ServerRequest('localhost')
        return sr.send_request(self._pipeline_dict)

    def _get_metadata(self, componentName):
        return self.component_list[componentName]

    def add(self, entity):
        self.component_seqid += 1
        metadata = self._get_metadata(entity['classname'])
        component_entry = {}
        component_entry["class"] = entity['classname']
        component_entry["groupID"] = metadata[0]
        component_entry["artifactId"] = metadata[1]
        component_entry["version"] = metadata[2]
        component_entry["java_import"] = metadata[3]
        component_entry["seqid"] = self.component_seqid
        component_entry["parameters"] = entity['parameters']
        self._components.append(component_entry)

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

    def build(self):
        build_pipeline(self._components)
        cliDefinition()
        print('Container web service for the provided pipeline is fired up. To stop use finish method')
        return self

    @staticmethod
    def process(text, language='en'):
        headers = {'Content-Type': 'application/json'}
        with yaspin(text="Pinging...", color="green") as sp:
            while True:
                try:
                    r = requests.post('http://localhost:3000/testPage', headers=headers,
                                      data=json.dumps({'text': 'ping...'}), verify=False)
                except requests.exceptions.ConnectionError:
                    continue
                if (r.status_code == requests.codes.ok):
                    break
            sp.ok("✓")

        body = json.dumps({'text': str(text)})
        r = requests.post('http://localhost:3000/analysis', headers=headers, data=body, verify=False)
        response = r.content

        cs = Cas(xmi_string=response.decode('utf-8'))
        return cs


    @staticmethod
    def finish():
        killAllRunningContainers()
        return "Container service is successfully destroyed"






class Component(Pipeline):
    def __init__(self):
        super(Component, self).__init__()
        self.component = dict()


    def run(self, string):
        return Pipeline().run(string)

    def opennlp_segmenter(self, **kwargs):
        """
        TODO
        :arg

        """
        self.component["classname"] = "OpenNlpSegmenter"
        parameter_list = {}
        parameter_list["PARAM_LANGUAGE"] = '"' + self.language + '"'
        self.component["parameters"] = parameter_list
        return self.component

    def opennlp_postagger(self, param_tagset=True, **kwargs):

        """
        Send a message to a recipient

        :param intern_tags: Use the String#intern() method on tags. This is usually a good idea to avoid spaming
        the heap with thousands of strings representing only a few different tags. (Default:True)
        :return: Cas object or DKPRO typesystem token or sentence
        """
        self.component["classname"] = "OpenNlpPosTagger"
        parameter_list = {}
        parameter_list["PARAM_LANGUAGE"] = '"' + self.language + '"'
        parameter_list["PARAM_PRINT_TAGSET"] = '"' + str(param_tagset) + '"'
        self.component["parameters"] = parameter_list
        return self.component

    @staticmethod
    def process(text, language='en'):
        cs = Cas()
        return cs




