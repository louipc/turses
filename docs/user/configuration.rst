Configuration
=============

The standard location is under ``$HOME`` directory, in a folder called ``.turses``. 

There is one mayor configuration file in turses:

    ``config``
        contains user preferences: colors, bindings, etc.

An one default token file:

    ``token``
        contains authentication token for the default user account

Each user account that is no the default one has its ``.token`` file. You
can generate new token files with:

.. code-block:: sh

    $ turses -a <alias>

After inserting the PIN code, a new ``.token`` file will appear in your 
configuration directory:

    ``<alias>.token``
        contains the oauth tokens for the account aliased to ``alias``

Now, when you execute:

.. code-block:: sh

    $ turses -a <alias>

you will be logged in with the previously stored credentials.

Here is an example with two accounts apart from the default one, aliased
to `alice` and `bob`.

.. code-block:: sh

    ~
    |+.turses/
    | |-config
    | |-token              # default user's token
    | |-alice.token        # accounts aliased to `alice` and `bob`
    | `-bob.token
    |+...
    |-...
    `

Bindings
--------

TODO

Palette
-------

TODO

Debug
-----

TODO
