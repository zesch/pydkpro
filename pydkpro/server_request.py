#! usr/bin/env python
# -*- coding : utf-8 -*-

import subprocess
import random
import codecs
import shlex
import os
from pydkpro.cas import Cas
import glob


class ServerRequest(object):
    def __init__(self, server_name):
        self.server_name = server_name

    def _get_dummy_server_response(self, json_string):  # TODO need to be deleted
        if json_string['type'] == 'Components':
            return ('Pipeline build!')  # TODO
        if json_string['type'] == 'payload':
            in_xmi = 'pydkpro/test_data/temp.xmi'
            out_xmi = 'pydkpro/cas_xmis'
            ts_xml = 'pydkpro/typesystems/temp_TypeSytems.xml'
            log_path = 'pydkpro/test_data/pipeline.log'
            with codecs.open(in_xmi, 'w', 'utf-8') as xmi_tofile:
                xmi_tofile.write(json_string['entity'])
            cmd = shlex.split("java -jar pydkpro/pydkpro-0.0.1-SNAPSHOT-standalone.jar %s %s %s" %(in_xmi, out_xmi, ts_xml))
            for f in glob.glob(os.path.join(out_xmi,  '*.xmi')):
                 os.remove(os.path.join(f))
            with codecs.open(log_path, 'w', 'utf-8') as f:
                p = subprocess.Popen(cmd, stdout=f, stderr=f)
                p.wait()
            for f in glob.glob(os.path.join(out_xmi,  '*.xmi')):
                 xmi_file = f
            return Cas(cas_path=xmi_file,  type_system_path=ts_xml)
        else:
            raise NotImplementedError


    def send_request(self, json_string):
        json_string['session_id'] = random.randint(1, 101) # add other metadata if necessary
        return self._get_dummy_server_response(json_string)