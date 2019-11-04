PyDKPro
------------

**REC:** If it is a wrapper for "DKPro Core", then IMHO it should be "PyDKProCore" because DKPro is larger than DKPro Core.

PyDKPro provides a Python wrapper for the `DKPro Core <https://dkpro.github.io/dkpro-core/>`_ NLP framework.
DKPro Core itself is based on the `UIMA <https://uima.apache.org>`_ framework and programmed in Java.
Interoperability is achieved via web services deployed as `docker container <https://www.docker.com/>`_.

**REC:** Can you say something on the life-cycle of the containers? When are they started, how long do they run?

Analysis results in DKPro Core are represented as CAS objects.
Conversion between Java and Python data structures is based on `dkpro-cassis <https://github.com/dkpro/dkpro-cassis>`_
We also provide built-in support for `spacy <https://spacy.io>`_ format and `NLTK <https://www.nltk.org>`_) format
allowing for seamless integration.

PyDKPro is still under heavy development. Feedback is highly appreciated.

System requirements
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

**REC:** How to tell/choose which version of DKPro Core is being used?

**REC:** How can I know which components exist and what I need to fill in for type/name?

**REC:** Normally, DKPro Core components have a name `ClearNlpTokenizer` - the 'tool' is internal and not fully standardized across different modules. I would not recommend splitting into `type` and `name`. In any case `type` clashes with the concept of an annotation "type". The model artifacts in turn are standardized and the variables `variant` and `language` should be used. Specifying an artifact directly is possible but should not be the default. If It is done, it should include groupId and version as well.

.. code-block:: python

    from pydkpro import Pipeline, Component

    p = Pipeline()
    p.add(Component(type='tokenizer', name='clearnlp', modelArtifact='clearnlp-model-segmenter-en-default',
                      language='en'))
    p.add(Component(type='pos_tagger', name='stanfordnlp', modelArtifact='stanfordnlp-model-tagger-en-fast.41',
                        printTagSet='false', language='en'))
    p.build()

Note: while defining components, except parameter 'type', the rest of the parameters are optional.

**REC:** What does the `build()` call actually do / return?

**REC:** I see how you would like to abstract the choice of the actual implementation away. I would recommend using `tool='segmenter'` here and providing a list somewhere what the tool names and the default implementations for the different tools are. Try sticking to established DKPro Core nomenclature (tool, variant, language, etc.).


**Run the pipeline**

For the triggered pipeline above, a CAS object will be generated for the provided string.
This CAS object can be used to retrieve annotations like tokens and POS tags, etc.

.. code-block:: python

    cas = p.run('Backgammon is one of the oldest known board games.')

**REC:** Provide language or document which default language is used (or if a language detector is used).

**REC:** How to run a pipeline on a pre-existing CAS, e.g. one loaded from disk?

To return all the tokens:

.. code-block:: python

    cas.get_token_strings()

**REC:** I'm not paricularly convinced of such convenience methods. I'd rather see the CAS select API be nicer, e.g. `cas.select(TOKEN).as_text()`.

Output:

.. code-block:: output

    ['Backgammon', 'is', 'one', 'of', 'the', 'oldest', 'known', 'board', 'games', '.']

To return all the pos tags:

.. code-block:: python

    cas.get_pos()

**REC:** See above.

Output:

.. code-block:: output

    ['NNP', 'VBZ', 'NN', 'IN', 'DT', 'JJS', 'VBN', 'NN', 'NNS', '.']

**Provide UIMA CAS functionality**

Generated cas object also provide UIMA CAS functionality. For example:

**REC:** It would be great if we could avoid having two implementations of the CAS, one in your project and one in Cassis. Let's rather try improving the API in Cassis.

**REC:** This is confusing - why use `cassis.Token` and not the DKPro Core token?

**REC:** Instead of having a CAS implementation in pydkpro which adds convenience methods like `get_pos()`, I'd suggest to add a parameter to the Cassis CAS constructor by which an "initializer" can be specified, e.g.

.. code-block:: python

    from pydkpro import DKProCoreTypeSystem
    from cassis import Cas

    cas = Cas(DKProCoreTypeSystem())

The effect of this "initializer" (here `DKProCoreTypeSystem()`) would be that it adds the convenience methods. It would also allow people with other type systems to nicely use Cassis with their types systems. It would even for the first time ever in UIMA allow a cross-type-system convenience API to be established!

.. code-block:: python

    # add annotation
    from pydkpro import Cas
    from cassis import Typesystem
    cas = Cas()
    Token = Typesystem(type_system='typesystem/TypeSystem.xml').get_type('cassis.Token')

    tokens = [
        Token(begin=0, end=1, id='0', pos='NNP'),
        Token(begin=2, end=6, id='1', pos='VBD'),
        Token(begin=7, end=12, id='2', pos='IN'),
        Token(begin=13, end=14, id='3', pos='.'),
    ]
    for token in tokens:
        cas.add_annotation(token)

    # select annotation
    s_type = 'cassis.Sentence'
    t_type = 'cassis.Token'
    for sentence in cas.select(s_type):
        for tok in cas.select_covered('cassis.Token', sentence):
            print(tok.pos)


**Conversion from CAS to spaCy format**

Generated CAS objects can also be typecast to the spaCy type system.

.. code-block:: python

    for token in cas.to_spacy():
        print(token.text, token.tag_)

**REC:** Having the converter is great, but IMHO it should be kept separately from the CAS object: `to_spacy(cas)` and `cas = from_spacy(doc)`.


**Conversion from CAS to NLTK format**

NLTK returns a specific format for each type of preprocessing.
Here is an example for POS:

**REC:** See comment on spacy.

.. code-block:: python

    print(cas.to_nltk_tagger())


Output:

.. code-block:: output

    [('Backgammon', 'NNP'), ('is', 'VBZ'), ('one', 'CD'), ('of', 'IN'), ('the', 'DT'), ('oldest', 'JJS'), ('known', 'VBN'), ('board', 'NN'), ('games', 'NNS'), ('.', '.')]

This output can then be used for further integration with other NLTK components:

.. code-block:: python

    import nltk
    chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>}"""
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(cas.to_nltk_pos_tagger())
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

**Conversion from spaCy or NLTK to PyDKPro**

PyDKPro also provides reverse functionality where a CAS object can be created from spaCy or NLTK output.
In the following example, tokenization is performed using NLTK tweet tokenizer, but POS tagging is done with the DKPro wrapper of Stanford CoreNLP POS tagger using their `fast.41` model:

**REC:** Why is there no `from_nltk` method? Having using the loop to add the tokens seems strange.

.. code-block:: python
    from nltk.tokenize import TweetTokenizer

    cas = Cas()
    for token in TweetTokenizer().tokenize('Backgammon is one of the oldest known board games.'):
        cas.add_token(token)

    p = Pipeline()
    p.add(Component(type='pos_tagger'))
    p.build()

    cas = p.run(cas)

    # get tokens
    cas.get_token_strings()

    # get pos tags
    cas.get_postags()

**REC: Above it as `get_pos()`...?


**Shortcut for running single components**

A single component can also be run without the need to build a pipeline first:

.. code-block:: python

    tokenizer = Component(type='tokenizer')
    cas = tokenizer.run('I like playing cricket.')
    cas.get_token_strings()

**REC:** call it `process` instead of `run` to stay in line with UIMA naming conventions.

Output:

.. code-block:: output

    ['I', 'like', 'playing', 'cricket', '.']

**Working with list of strings**

Multiple strings in the form of list can also be processed, where each element of list will be considered as
document.

.. code-block:: python

    str_list = ['Backgammon is one of the oldest known board games.', 'I like playing cricket.']
    for str in str_list:
        cas = p.run(str)
        cas.get_token_strings() # do something with the CAS

    # trigger collectionProcessComplete
    p.finalize()

**REC:** Call it `p.collection_process_complete()`?
**TZ:** p.finish() and p.collection_process_complete() as a synonym

**Working with text documents**

Pipelines can also be directly run on text documents:

.. code-block:: python

    cas = p.run(file2str('test_data/input/test2.txt'))
    cas.get_token_strings()
    cas.get_postags()

**Working with multiple text documents**

Multiple documents can also be processed by providing documents path and document name matching patterns

.. code-block:: python

    # documents available at different path can be provided in list
    docs = ['test_data/input/1.txt', 'test_data/input/2.txt']
    for doc in docs:
        p.run(file2str(doc))

    p.finalize()
