# pydkpro

## demo example

```
from demo import *
p = Pipeline()
p.add(d.Component(name='tokenizer', brand='clearnlp', language='en'))
p.add(d.Component(name='pos_tagger', brand='stanford', language='en', variant='fast41'))
p.run('hello how are you')
````

## output
```
{'components': [{'name': 'tokenizer', 'brand': 'clearnlp', 'language': 'en'},
  {'name': 'pos_tagger',
   'brand': 'stanford',
   'language': 'en',
   'variant': 'fast41'}],
 'payload': '<?xml version=\'1.0\' encoding=\'ASCII\'?>\n<xmi:XMI xmlns:xmi="http://www.omg.org/XMI" xmlns:cas="http:///uima/cas.ecore" xmi:version="2.0"><cas:NULL xmi:id="0"/><cas:Sofa xmi:id="1" sofaNum="1" sofaID="_InitialView" mimeType="text/plain" sofaString="hello how are you"/><cas:View sofa="1" members=""/></xmi:XMI>'}
 ```


