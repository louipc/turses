Internals
=========

Overview
--------

Here is an overview of the multiple files that compound `turses`, each
of them with a comment explaining their goal.

.. code-block:: sh

    turses
    ├── requirements
    │   ├── base.txt
    │   └── dev.txt
    ├── setup.py
    └── turses
        ├── api
        │   ├── base.py      # definition of an interface to the Twitter API
        │   ├── backends.py  # Twitter API implementations
        │   └── __init__.py
        ├── cli.py           # logic for launching `turses`
        ├── config.py        # configuration management
        ├── core.py          # core logic: controller and event handling
        ├── __init__.py
        ├── models.py        # data structures
        ├── ui.py            # UI widgets
        └── utils.py         # misc funcions that don't fit elsewhere
