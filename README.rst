PyDKPro
------------

.. **REC:** If it is a wrapper for "DKPro Core", then IMHO it should be "PyDKProCore" because DKPro is larger than DKPro Core. But in fact, I would suggest to think of a name that can work nicely without "DKPro", e.g. "Pypeline" or "Pyper" or something completely random - "Maryo" because Mario is a famous plumber and you do plumbing of pipelines in pYthon here, ... etc. - and then as an "afterthought" add the "DKPro" brand -> "DKPro Pyper", "DKPro Maryo", etc. We get a lot of confusion about whawt "DKPro" is and that it is a different thing than "DKPro Core". Having more emancipated names for the DKPro products could alleviate this problem.

.. **PA** "PyDKProCore" is too long for API name. We should think something short and consumable. What about "DKPyro" can be stand for DK PYthon pROcessing :-p

PyDKPro provides a Python wrapper for the `DKPro Core <https://dkpro.github.io/dkpro-core/>`_ NLP framework.
DKPro Core itself is based on the `UIMA <https://uima.apache.org>`_ framework and programmed in Java.
Interoperability is achieved via web services deployed as `docker container <https://www.docker.com/>`_.
After containerization, services remain active unless manually disabled or idle for limited period of interval.

.. **REC:** Can you say something on the life-cycle of the containers? When are they started, how long do they run?

Analysis results in DKPro Core are represented as CAS objects.
Conversion between Java and Python data structures is based on `dkpro-cassis <https://github.com/dkpro/dkpro-cassis>`_
We also provide built-in support for `spacy <https://spacy.io>`_ format and `NLTK <https://www.nltk.org>`_) format
allowing for seamless integration.

PyDKPro is still under heavy development. Feedback is highly appreciated.

Demo Version
-------------

For demo purpose, different use cases are provided with working example (mocked) in ``Examples/UseCases.ipynb``

System requirements
-------------------

- TODO

Installation
-------------------

- TODO


Features
------------

- Using DKPro Core components directly in Python
- Conversion to spaCy
- Conversion to NLTK


Usage
-----

**Defining an NLP pipeline**

A pipeline is build by adding DKPro Core components.

.. **REC:** How to tell/choose which version of DKPro Core is being used?

.. **REC:** How can I know which components exist and what I need to fill in for type/name?

.. **REC:** Normally, DKPro Core components have a name `ClearNlpTokenizer` - the 'tool' is internal and not fully standardized across different modules. I would not recommend splitting into `type` and `name`. In any case `type` clashes with the concept of an annotation "type". The model artifacts in turn are standardized and the variables `variant` and `language` should be used. Specifying an artifact directly is possible but should not be the default. If It is done, it should include groupId and version as well.

.. code-block:: python

    from pydkpro import Pipeline, Component
    p = Pipeline(version="2.0.0", language='en')
    p.add(Component().clearNlpSegmenter())
    p.add(Component().stanfordPosTagger(variant='fast-caseless', printTagSet='false'))
    p.build() # fire up the container web service

Note: All parameters are optional and default to best performed model versions.

.. **REC:** What does the `build()` call actually do / return?

.. **REC:** I see how you would like to abstract the choice of the actual implementation away. I would recommend using `tool='segmenter'` here and providing a list somewhere what the tool names and the default implementations for the different tools are. Try sticking to established DKPro Core nomenclature (tool, variant, language, etc.).

.. **PA:** If we provide drop down list capabilities like above, then user will easily adapt to dkpro components. Ofcourse, we can also provide group name to all the components


**Run the pipeline**

For the triggered pipeline above, a CAS object will be generated for the provided string.
This CAS object can be used to retrieve annotations like tokens and POS tags, etc.

.. code-block:: python

    cas = p.process('Backgammon is one of the oldest known board games.', language='en')

Note: Language detector is used, if language parameter is not provided.

.. **REC:** Provide language or document which default language is used (or if a language detector is used).

.. **REC:** How to run a pipeline on a pre-existing CAS, e.g. one loaded from disk?

.. **PA:** I believe there is one example below that run pipeline with pre-existing cas.

To return all the tokens:

.. code-block:: python

    from pydkpro import DKProCoreTypeSystem as dts
    cas.select(dts().token()).as_text()

.. **REC:** I'm not paricularly convinced of such convenience methods. I'd rather see the CAS select API be nicer, e.g. `cas.select(TOKEN).as_text()`.

Output:

.. code-block:: output

    ['Backgammon', 'is', 'one', 'of', 'the', 'oldest', 'known', 'board', 'games', '.']

To return all the pos tags:

.. code-block:: python

    cas.select(dts().token()).get_pos()

.. **REC:** See above.

Output:

.. code-block:: output

    ['NNP', 'VBZ', 'NN', 'IN', 'DT', 'JJS', 'VBN', 'NN', 'NNS', '.']

**Provide UIMA CAS functionality**

.. **REC:** It would be great if we could avoid having two implementations of the CAS, one in your project and one in Cassis. Let's rather try improving the API in Cassis.

.. **REC:** This is confusing - why use `cassis.Token` and not the DKPro Core token?

.. **REC:** Instead of having a CAS implementation in pydkpro which adds convenience methods like `get_pos()`, I'd suggest to add a parameter to the Cassis CAS constructor by which an "initializer" can be specified, e.g.

``DKProCoreTypeSystem`` would allow integration of other type systems to nicely use DKPro Cassis with their types systems. Generated cas object provide UIMA CAS functionality. For example:

..  python

.. from pydkpro import DKProCoreTypeSystem
.. from cassis import Cas

..  cas = Cas(DKProCoreTypeSystem())

.. The effect of this "initializer" (here `DKProCoreTypeSystem()`) would be that it adds the convenience methods. It would also allow people with other type systems to nicely use Cassis with their types systems. It would even for the first time ever in UIMA allow a cross-type-system convenience API to be established!

.. code-block:: python

    # add annotation
    from pydkpro.cas import Cas
    cas = Cas(dts())

    tokens = [
           dts().token(begin=0, end=1, id='0', pos='NNP'),
           dts().token(begin=2, end=6, id='1', pos='VBD'),
           dts().token(begin=7, end=12, id='2', pos='IN'),
           dts().token(begin=13, end=14, id='3', pos='.'),
        ]

    for token in tokens:
        cas.add_annotation(token)

    # select annotation
    for sentence in cas.select(dts().sentence()):
         for tok in cas.select_covered(dts().token, sentence):
            print(tok.pos)

Output:

.. code-block:: output

    NNP
    VBD
    IN
    .


**Conversion from CAS to spaCy format and vice-versa**

Generated CAS objects can also be typecast to the spaCy type system.

.. code-block:: python

    from pydkpro import To_spacy, From_spacy
    cas = p.process('Backgammon is one of the oldest known board games.', language='en')


    for token in To_spacy(cas)():
        print(token.text, token.tag_)

.. **REC:** Having the converter is great, but IMHO it should be kept separately from the CAS object: `to_spacy(cas)` and `cas = from_spacy(doc)`.


**Conversion from spaCy**

.. code-block:: python

    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
    cas = From_spacy(doc)()
    print(cas.select(dts().token()).get_pos())

**Conversion from CAS to NLTK format**

NLTK returns a specific format for each type of preprocessing.
Here is an example for POS:

.. **REC:** See comment on spacy.

.. code-block:: python

    from pydkpro.external import To_nltk, From_nltk
    print(To_nltk().tagger(cas))

Output:

.. code-block:: output

    [('Backgammon', 'NNP'), ('is', 'VBZ'), ('one', 'CD'), ('of', 'IN'), ('the', 'DT'), ('oldest', 'JJS'), ('known', 'VBN'), ('board', 'NN'), ('games', 'NNS'), ('.', '.')]

This output can then be used for further integration with other NLTK components:

.. code-block:: python

    import nltk
    chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>}"""
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(To_nltk().tagger(cas))
    print(chunked)

Output:

.. code-block:: output

  (S
  (Chunk Backgammon/NNP)
  is/VBZ
  one/CD
  of/IN
  the/DT
  oldest/JJS
  known/VBN
  board/NN
  games/NNS
  ./.)

**Conversion from NLTK**

PyDKPro also provides reverse functionality where a CAS object can be created from spaCy or NLTK output.
In the following example, tokenization is performed using NLTK tweet tokenizer, but POS tagging is done with the DKPro wrapper of Stanford CoreNLP POS tagger using their `fast.41` model:

.. **REC:** Why is there no `from_nltk` method? Having using the loop to add the tokens seems strange.

.. code-block:: python

    from nltk.tokenize import TweetTokenizer
    cas = From_nltk().tokenizer(TweetTokenizer().tokenize('Backgammon is one of the oldest known board games.'))

**Cas processing**

PyDKPro pipeline also provide direct cas object processing as demonstrated in below example:

.. code-block:: python
    p = Pipeline()
    p.add(Component().stanfordPosTagger())
    p.build()

    cas = p.process(cas)

    # get tokens
    print(cas.select(dts().token()).as_text())

    # get pos tags
    print(cas.select(dts().token()).get_pos())

.. **REC: Above it as `get_pos()`...?


**Shortcut for running single components**

A single component can also be run without the need to build a pipeline first:

.. code-block:: python

    tokenizer = Component().clearNlpSegmenter()

    cas = tokenizer.process('I like playing cricket.')
    print(cas.select(dts().token()).as_text())

.. **REC:** call it `process` instead of `run` to stay in line with UIMA naming conventions.

Output:

.. code-block:: output

    ['I', 'like', 'playing', 'cricket', '.']

**Working with list of strings**

Multiple strings in the form of list can also be processed, where each element of list will be considered as
document.

.. code-block:: python

    str_list = ['Backgammon is one of the oldest known board games.', 'I like playing cricket.']
    for str in str_list:
        cas = p.process(str)
        print(cas.select(dts().token()).as_text())

.. **REC:** Call it `p.collection_process_complete()`?
.. **TZ:** p.finish() and p.collection_process_complete() as a synonym

**Working with text documents**

Pipelines can also be directly run on text documents:

.. code-block:: python

    from pydkpro.external import File2str

    cas = p.process(File2str('test_data/input/test2.txt')())
    print(cas.select(dts().token()).as_text())


**Working with multiple text documents**

Multiple documents can also be processed by providing documents path and document name matching patterns

.. code-block:: python

    # documents available at different path can be provided in list
    docs = ['test_data/input/1.txt', 'test_data/input/2.txt']
    for doc in docs:
        p.process(File2str(doc)())
**End collection process**

With following command pipeline's collection process will be completed (Alternatively, scope operator ``with` can be used)

.. code-block:: python
    p.finish()
