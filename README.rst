# pydkpro

PyDKPro provides a pure-Python implementation of DKPro `https://dkpro.github.io/`
as defined by the `UIMA <https://uima.apache.org>` framework and **dkpro-cassis** `https://github.com/dkpro/dkpro-cassis`

This library dynamically generates a pipeline of variety Linguistic Features available in **DKPro** and deploy pipeline at the server as `docker container <https://www.docker.com/>`_.

This library also provide room for integration of Python-based Natural Language Processing (e.g.
`spacy <https://spacy.io>`_ or `NLTK <https://www.nltk.org>`_) and Machine Learning libraries (e.g.
`scikit-learn <https://scikit-learn.org/stable/>`_ or `Keras <https://keras.io>`_) in UIMA-based text analysis workflows.


Features
------------

Currently working on features which are still under development, e.g.:

- Dynamically building of **DkPro** java-based pipeline.
- Deserializing/ serializing documents into cas objects.
- Deserializing/serializing type systems from/to XML
- Data structures are compatible with spacy and NLTK.
- Multiple documents processing.
- Direct DKPro component usage.
- Type system can be changed after loading
- Reference, array, and list features


Usage
-----


**Building linguistic pipeline**


Linguistic Pipeline can be created by adding available DKPro core natural language processing components, for example, tokenizer, pos tagger, ner, etc and triggered to create docker container web service.

.. code-block:: python

    from pydkpro import *
    p = Pipeline()
    p.add(Component(name='tokenizer', brand='clearnlp', language='en'))
    p.add(Component(name='pos_tagger', brand='stanford', language='en', variant='fast41'))
    p.trigger()

Output:

.. code-block:: output

    Pipeline build!



**Generate annotations for the provided natural language string**


For the triggered pipeline above, Cas object will be generated for the provided string. This cas object can be be used to retrieve annotations like tokens and pos tags, etc.

.. code-block:: python

    text = 'Backgammon is one of the oldest known board games. Its history can be traced back nearly 5,000 years to archeological discoveries in the Middle East.'
    mycas = p.run(text)

To return all the tokens (for clearnlp tokenizer)

.. code-block:: python

    mycas.get_tokens()

Output:

.. code-block:: output

   {'in', 'the', 'archeological', 'discoveries', 'can', 'back', 'Backgammon', 'traced', 'known', 'be', 'to', 'oldest', 'East', '5,000', 'of', 'history', 'is', 'nearly', 'Its', '.', 'years', 'board', 'Middle', 'one', 'games'}

To return all the pos tags (for Stanford fast.41 pos tagger)

.. code-block:: python

    mycas.get_postags()

Output:

.. code-block:: output

    {('5,000', 'CD'), ('known', 'VBN'), ('Its', 'PRP$'), ('of', 'IN'), ('games', 'NNS'), ('Middle', 'NNP'), ('discoveries', 'NNS'), ('board', 'NN'), ('is', 'VBZ'), ('years', 'NNS'), ('traced', 'VBN'), ('to', 'TO'), ('back', 'RB'), ('oldest', 'JJS'), ('Backgammon', 'NNP'), ('can', 'MD'), ('nearly', 'RB'), ('one', 'CD'), ('archeological', 'JJ'), ('history', 'NN'), ('in', 'IN'), ('East', 'NNP'), ('be', 'VB'), ('the', 'DT'), ('.', '.')}

**Compatibility with spacy**

Generated Cas objects can also be typecast to the spacy usable type system.

.. code-block:: python

    casToSpacy = mycas.to_spacy()
    for token in casToSpacy:
        print(token.text, token.tag_)

Output:

.. code-block:: output

    Backgammon  NNP
    is  VBZ
    one  CD
    of  IN
    the  DT
    oldest  JJS
    known  VBN
    board  NN
    so on....

Spacy span can also be created using Cas type-casted spacy objects.

.. code-block:: python

   span = casToSpacy[2:8]
   span.text

Output:

.. code-block:: output

    'one of the oldest known board'

**Compatibility with NLTK**

As NLTK hasn't specific type-system like Cas or spacy doc. It produces a generic type system depends upon the components. For example:

.. code-block:: python

    casToNltk = mycas.to_nltk_pos_tagger()
    print(casToNltk)


Output:

.. code-block:: output

{('5,000', 'CD'), ('known', 'VBN'), ('Its', 'PRP$'), ('of', 'IN'), ('games', 'NNS'), ('Middle', 'NNP'), ('discoveries', 'NNS'), ('board', 'NN'), ('is', 'VBZ'), ('years', 'NNS'), ('traced', 'VBN'), ('to', 'TO'), ('back', 'RB'), ('oldest', 'JJS'), ('Backgammon', 'NNP'), ('can', 'MD'), ('nearly', 'RB'), ('one', 'CD'), ('archeological', 'JJ'), ('history', 'NN'), ('in', 'IN'), ('East', 'NNP'), ('be', 'VB'), ('the', 'DT'), ('.', '.')}

which can also be used for a further operation like the integration of chunk parser

.. code-block:: python

    import nltk
    chunkGram = r"""Chunk: {<RB.?>*<VB.?>*<NNP>}"""
    chunkParser = nltk.RegexpParser(chunkGram)
    chunked = chunkParser.parse(casToNltk)
    print(chunked)

Output:

.. code-block:: output

    (S
  5,000/CD
  known/VBN
  Its/PRP$
  of/IN
  games/NNS
  (Chunk Middle/NNP)
  discoveries/NNS
  board/NN
  is/VBZ
  years/NNS
  traced/VBN
  to/TO
  back/RB
  oldest/JJS
  (Chunk Backgammon/NNP)
  can/MD
  nearly/RB
  one/CD
  archeological/JJ
  history/NN
  in/IN
  (Chunk East/NNP)
  be/VB
  the/DT
  ./.)

PyDKPro also provides reverse functionality where Cas object can get annotation generated by other libraries like spacy or NLTK. In the following example, tokenization is performing using NLTK tweet tokenizer but pos tagging annotation is done by DKPro Stanford fast.41 component:

.. code-block:: python

    p2 = Pipeline()
    p2.add(Component(name='pos_tagger', brand='stanford', language='en', variant='fast41'))
    p2.trigger()
    from nltk.tokenize import TweetTokenizer
    tknzr = TweetTokenizer()
    mycas2 = Cas()
    for token in tknzr.tokenize('Backgammon is one of the oldest known board games.'):
        mycas2.add_token(token)
    nltkTokenizedCas = p2.run(mycas2)

    # get tokens
    nltkTokenizedCas.get_tokens()

Output:

.. code-block:: output

    {'board', 'of', 'Backgammon', 'is', 'known', 'the', '.', 'one', 'oldest', 'games'}

.. code-block:: python

    # get pos tags
    nltkTokenizedCas.get_postags()

Output:

.. code-block:: output

    {('one', 'NN'), ('Backgammon', 'NNP'), ('games', 'NNS'), ('.', '.'), ('known', 'VBN'), ('one', 'CD'), ('board', 'NN'), ('is', 'VBZ'), ('the', 'DT'), ('of', 'IN'), ('oldest', 'JJS')}

** Working with single Component**

PyDKPro also provides the functionality of using a single component of the DKPro library. Following example display the usage:


.. code-block:: python

    dkpro_clearnlp_tokenizer = Component(name='tokenizer', brand='clearnlp', language='en')
    tokenizer_cas = dkpro_clearnlp_tokenizer.run('I like playing cricket.')
    tokenizer_cas.get_tokens()

Output:

.. code-block:: output

    {'cricket', 'playing', 'I', 'like', '.'}

** Working with documents*

DKPro provides the functionality to load documents in addition to strings. This feature can also be used by using PyDKPro as shown in the following example:

.. code-block:: python

    cas_doc = p.run('test_data/input/test2.txt')
    # get tokens
    cas_doc.get_tokens()

    # get pos tags
    cas_doc.get_postags()

