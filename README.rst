Overview
========

.. image:: https://img.shields.io/pypi/v/cfg4py.svg
        :target: https://pypi.python.org/pypi/cfg4py

.. image:: https://travis-ci.org/zillionare/cfg4py.svg?branch=master
        :target: https://travis-ci.com/zillionare/cfg4py

.. image:: https://readthedocs.org/projects/cfg4py/badge/?version=latest
        :target: https://cfg4py.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/zillionare/cfg4py/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/zillionare/cfg4py

.. image:: https://static.pepy.tech/badge/cfg4py
  :target: https://pepy.tech/project/cfg4py

* Free software: BSD license
* Documentation: https://cfg4py.readthedocs.io.


A python config module that:

1. Adaptive deployment (default, dev, test, production) support
2. Cascading configuration (central vs local) support
3. Auto-complete
4. Templates (logging, database, cache, message queue,...)
5. Environment variables macro support
6. Enable logging in one line
7. Built on top of yaml

Features
^^^^^^^^

It's common to see that you have different settings for development machine, test machine and production site. They share many common settings, but a few of them has to be different.

For example, developers should connect to local database server when performing unittest, and tester should connect to their own database server. All these servers should be deployed separately and no data should be messed up.

Cfg4Py has perfect solution supporting for this: adaptive deployment environment support.

Adaptive Deployment Environment Support
---------------------------------------
In any serious projects, your application may run at both development, testing and production site. Except for effort of copying similar settings here and there, sometimes we'll mess up with development environment and production site. Once this happen, it could result in very serious consequence.

To solve this, Cfg4Py developed a mechanism, that you provide different sets for configurations: dev for development machine, test for testing environment and production for production site, and all common settings are put into a file called `defaults`.

cfg4py module knows which environment it's running on by looking up environment variable __cfg4py_server_role__. It should be one of `DEV`, `TEST` and `PRODUCTION`. If nothing found, it means setup is not finished, and Cfg4Py will refuse to work. If the environment is set, then Cfg4Py will read settings from defaults set, then apply update from either of `DEV`, `TEST` and `PRODUCTION` set, according to the environment the application is running on.

.. important::

    Since 0.9.0, cfg4py can still work if __cfg4py_server_role__ is not set, when it work at non-strict mode.

Cascading design
--------------------

Assuming you have a bunch of severs for load-balance, which usually share same configurations. So you'd like put the configurations on a central repository, which could be a redis server or a relational database. Once you update configuration settings at central repository, you update configurations for all servers. But somehow for troubleshooting or maintenance purpose, you'd like some machines could have its own settings at a particular moment.

This is how Cfg4Py solves the problem:

1. Configure your application general settings at remote service, then implement a `RemoteConfigFetcher` (Cfg4Py has already implemented one, that read settings from redis), which pull configuration from remote serivce periodically.
2. Change the settings on local machine, after the period you've set, these changes are popluated to all machines.

Auto-complete
-------------

.. image:: http://images.jieyu.ai/images/projects/cfg4py/auto-complete.gif


With other python config module, you have to remember all the configuration keys, and refer to each settings by something like cfg["services"]["redis"]["host"] and etc. Keys are hard to rememb, prone to typo, and way too much tedious.

When cfg4py load raw settigns from yaml file, it'll compile all the settings into a Python class, then Cfg4Py let you access your settings by attributes. Compares the two ways to access configure item:

.. code-block:: python

        cfg["services"]["redis"]["host"]

vs:

.. code-block:: python

        cfg.services.redis.host

Apparently the latter is the better.

And, if you trigger a build against your configurations, it'll generate a python class file. After you import this file (named 'schema.py') into your project, then you can enjoy code auto-complete!

Templates
----------
It's hard to remember how to configure log, database, cache and etc, so cfg4py provide templates.

Just run cfg4py scaffold, follow the tips then you're done.

.. image:: http://images.jieyu.ai/images/projects/cfg4py/scaffold.png


Environment variables macro
----------------------------
The best way to keep secret, is never share them. If you put account/password files, and these files may be leak to the public. For example, push to github by accident.

With cfg4py, you can set these secret as environment variables, then use marco in config files. For example, if you have the following in defaults.yaml (any other files will do too):

.. code-block:: text

        postgres:
                dsn: postgres://${postgres_account}:${postgres_password}@localhost

then cfg4py will lookup postgres_account, postgres_password from environment variables and make replacement.


Enable logging with one line
-----------------------------
with one line, you can enable file-rotating logging:

.. code-block:: python

    cfg.enable_logging(level, filename=None)

Apply configuration change on-the-fly
-------------------------------------
Cfg4Py provides mechanism to automatically apply configuration changes without restart your application. For local files configuration change, it may take effect immediately. For remote config change, it take effect up to `refresh_interval` settings.

On top of yaml
---------------
The raw config format is backed by yaml, with macro enhancement. YAML is the best for configurations.



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
