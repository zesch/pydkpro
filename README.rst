PyDKPro
------------


PyDKPro provides a Python wrapper for the `DKPro Core <https://dkpro.github.io/dkpro-core/>`_ NLP framework.
DKPro Core itself is based on the `UIMA <https://uima.apache.org>`_ framework and programmed in Java.
Interoperability is achieved via web services deployed as `docker container <https://www.docker.com/>`_.
After containerization, services remain active unless manually disabled or idle for limited period of interval.


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

Create virtual environment.

.. code-block:: bash
    virtualenv -p python3 pydkpro

Install dependencies using pip.

    $ python -m pip install -r requirements.txt

    $ python -m spacy download en_core_web_sm


Features
------------

- Using DKPro Core components directly in Python
- Conversion to spaCy
- Conversion to NLTK


Usage
-----

**How to open examples notebook**

    $ cd /Examples
    
    $ jupyter notebook

**Defining an NLP pipeline**

A pipeline is build by adding DKPro Core components.


.. code-block:: python

    from pydkpro import Pipeline, Component
    p = Pipeline(version="2.0.0", language='en')
    p.add(Component().clearNlpSegmenter())
    p.add(Component().stanfordPosTagger(variant='fast-caseless', printTagSet='false'))
    p.build() # fire up the container web service

Note: All parameters are optional and default to best performed model versions.



**Run the pipeline**

For the triggered pipeline above, a CAS object will be generated for the provided string.
This CAS object can be used to retrieve annotations like tokens and POS tags, etc.

.. code-block:: python

    cas = p.process('Backgammon is one of the oldest known board games.', language='en')

Note: Language detector is used, if language parameter is not provided.


To return all the tokens:

.. code-block:: python

    from pydkpro import DKProCoreTypeSystem as dts
    cas.select(dts().token).as_text()


Output:

.. code-block:: output

    ['Backgammon', 'is', 'one', 'of', 'the', 'oldest', 'known', 'board', 'games', '.']

To return all the pos tags:

.. code-block:: python

    cas.select(dts().token).get_pos()


Output:

.. code-block:: output

    ['NNP', 'VBZ', 'NN', 'IN', 'DT', 'JJS', 'VBN', 'NN', 'NNS', '.']

**Provide UIMA CAS functionality**


``DKProCoreTypeSystem`` would allow integration of other type systems to nicely use `DKPro Cassis <https://github.com/dkpro/dkpro-cassis>`_ with their types systems. Generated cas object provide UIMA CAS functionality. For example:


.. code-block:: python

    # add annotation
    from pydkpro.cas import Cas
    Token = dts().typesystem.get_type('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token') # define dkpro token
    cas = Cas(dts().typesystem)()
    cas.sofa_string = "I like cheese ."
    tokens = [
        Token(begin=0, end=1, id='0', pos='NNP'),
        Token(begin=2, end=6, id='1', pos='VBD'),
        Token(begin=7, end=13, id='2', pos='IN'),
        Token(begin=14, end=15, id='3', pos='.')
    ]


    for token in tokens:
        cas.add_annotation(token)

Cas token attributes can printed as following:

.. code-block:: python

    print([x.get_covered_text() for x in cas.select_all()])
    print([x.pos for x in cas.select_all()])

Output:

.. code-block:: output

    ['I', 'like', 'cheese', '.']
    ['NNP', 'VBD', 'IN', '.']


**Conversion from CAS to spaCy format and vice-versa**

Generated CAS objects can also be typecast to the spaCy type system.

.. code-block:: python

    from pydkpro import To_spacy, From_spacy
    cas = p.process('Backgammon is one of the oldest known board games.', language='en')


    for token in To_spacy(cas)():
        print(token.text, token.tag_)



**Conversion from spaCy**

.. code-block:: python

    import spacy

    nlp = spacy.load("en_core_web_sm")
    doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
    cas = From_spacy(doc)()
    print(cas.select(dts().token).get_pos())

**Conversion from CAS to NLTK format**

NLTK returns a specific format for each type of preprocessing.
Here is an example for POS:



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




**Shortcut for running single components**

A single component can also be run without the need to build a pipeline first:

.. code-block:: python

    tokenizer = Component().clearNlpSegmenter()

    cas = tokenizer.process('I like playing cricket.')
    print(cas.select(dts().token).as_text())



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
        print(cas.select(dts().token).as_text())



**Working with text documents**

Pipelines can also be directly run on text documents:

.. code-block:: python

    from pydkpro.external import File2str

    cas = p.process(File2str('test_data/input/test2.txt')())
    print(cas.select(dts().token).as_text())


**Working with multiple text documents**

Multiple documents can also be processed by providing documents path and document name matching patterns

.. code-block:: python

    # documents available at different path can be provided in list
    docs = ['test_data/input/1.txt', 'test_data/input/2.txt']
    for doc in docs:
        p.process(File2str(doc)())
**End collection process**

With following command pipeline's collection process will be completed (Alternatively, scope operator ``with`` can be used)

.. code-block:: python
    
    p.finish()
