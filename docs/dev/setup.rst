Set up the development environment
==================================

You’re free to setup up the environment in any way you like. Here is a way using virtualenv and virtualenvwrapper. If you don’t have them, you can install them using:

.. code-block:: sh

        $ pip install virtualenvwrapper

Virtual environments allow you to work on an installation of python which is not the one installed on your system. Especially, it will install the different projects under a different location.

To create the virtualenv environment, you have to do:


.. code-block:: sh

        $ mkvirtualenv turses

Then you would have to install all the dependencies:


.. code-block:: sh

        $ pip install -r requirements/dev.txt
        $ make install

Running the test suite
----------------------

Each time you add a feature, there are two things to do regarding tests: checking that the tests run in a right way, and be sure that you add tests for the feature you are working on or the bug you’re fixing.

The tests leaves under ``/tests`` and you can run them using ``nosetests``:


.. code-block:: sh

        $ make test
