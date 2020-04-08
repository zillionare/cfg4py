Overview
========

.. image:: https://img.shields.io/pypi/v/cfg4py.svg
        :target: https://pypi.python.org/pypi/cfg4py

.. image:: https://img.shields.io/travis/jieyu_tech/cfg4py.svg
        :target: https://travis-ci.com/jieyu_tech/cfg4py

.. image:: https://readthedocs.org/projects/cfg4py/badge/?version=latest
        :target: https://cfg4py.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




A python config module support hierarchical configuration and multi-environment deployment


* Free software: BSD license
* Documentation: https://cfg4py.readthedocs.io.

Features
--------

You have a bunch of severs of the same role, which usually share same
configuration. But somehow for troubleshooting or maintenance purpose,
you'd like some particular machines could have its own settings at some
particular moment.

At most occasions we'll solve the problem this way:

1. The most broad used settings are in a central database or provided by a service. To save time for editing, these settings are at server-role granularity, not machine/instance bound.
2. Your application code (with cfg4py module) will provide a default configuration set, which are least important , used only if the application cannot talk to the central configuration service. In that case, the application can still run with downgraded quality, but is surely better than no service.
3. Each local machine could have local config files for overwriting central settings.


That's the three-level hierarchical configuration design. The default settings value which put in the config module (or your code) is least important, they'll serve only if no settings can be retrieved elsewhere. The settings reside on local machines, are the most important, once exists, will override all other settings.

Adaptive Deployment Environment Support
---------------------------------------

Sometimes developer mess up with development environment and production site. Once this happen, it could result in very serious consequence. To avoid this, one should always read configuration from which specify for the production site when the application runs on a production site.

cfg4py module knows which environment it's running on by lookup environment variables __cfg4py_server_role__. It can be one of 'development', 'test' and 'production'. If nothing found, it means setup is not finished or something wrong. Then it'll load the very default configuration.

Config logging
--------------
Setup a basic logging for your application in one line:
    cfg.enable_logging(level, filename=None)

Watching configuration change
-----------------------------
and update automatically.

Autocomplete prompt
------------
It's hard to remember all configuration keys. To ease the use and prevent from using wrong keys, cfg4py provide
mechanism to leverage IDE's auto-complete function. You just need write your configuration files in supported format
(currently json and yaml), then call `cfg4py.build`, this will build a python class file, and IDE can leverage it
for auto-complete.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
