=====
Usage
=====

Quick Guide
-----------

To use Cfg4Py in a project::

    import cfg4py

    # create config object
    cfg = cfg4py.init(path_to_config_dir)

    # then refer to settings by cfg's properties
    # given the following yaml settings (filename: defaults.yaml) under path_to_config_dir

    # services:
    #   redis:
    #       host: localhost

    # you can access settings by '.'
    print(cfg.services.redis.host)

    # you CANNOT access settings like this way (this will raise exceptions):
    print(cfg["services"])

Exhausted Guide
---------------

Step 1.
~~~~~~~
Use Cfg4Py tool to generate configuration templates:

.. code-block::shell
        cfg4py scaffold

.. image:: static/scaffold.png

You may need modify settings according to your enviroment.

Step 2.
~~~~~~~
Build config class, and import it into your project:

.. code-block::bash
        cfg4py build /path/to/your/config/dir

.. code-block::python
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            # make sure that cfg4py_auto_gen is at your $PYTHONPATH
            from cfg4py_auto_gen import Config
        import cfg4py

        cfg: Config = cfg4py.init('/path/to/your/config/dir')

        # now you should be able to get auto-complete hint while typing
        cfg.?

Step 3.
~~~~~~~
cfg4py will take care of setting's change automatically, all you need to do is put correct settings into either
(defaults, dev, test, production) config file. And once you change the settings, it should take effect at once.

You can also configure a remote source by implemented a subclass of `RemoteConfigFetcher`. A redis fetcher is
provided out-of-box:

.. code-block::python
        from cfg4py import RedisConfigFetcher
        from redis import StrictRedis

        cfg = cfg4py.int()  # since we're using remote config now, so we can omit path param here
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        cfg4py.config_remote_fetcher(fetcher, 1)

The settings in redis under `key` should be a json string, which can be converted into a dict object.

Step 4.
~~~~~~~~
Before starting run your application, you should set __cfg4py_server_role__ to any of [DEV,TEST,PRODUCTION]. You can
run the following command to get the help:

.. code-block::bash
        cfg4py hint set_server_role

Use cfg4py as a cheat sheet
----------------------------
cfg4py does more than a config module, it can be a cheat sheet for many configurations. For example, want to know how
to config a conda source?

.. code-block::bash
        cfg4py hint conda --usage

It'll tell you how to change conda source channels by either command or modifying conda config file.
