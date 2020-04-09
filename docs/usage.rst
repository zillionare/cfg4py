=====
Usage
=====

Quick Guide
-----------

To use Cfg4Py in a project::

    import cfg4py

    # create config object
    cfg = cfg4py.create_config(path_to_config_dir, dump_on_change=True)

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

You may need modify some settings.

Step 2.
~~~~~~~
Build config class, and import it into your project:

.. code-block:: console
    cfg4py build /path/to/your/config/dir

.. code-block::python
    # make sure that cfg4py_auto_gen is at your PYTHONPATH
    from cfg4py_auto_gen import Config
    import cfg4py

    cfg: Config = cfg4py.create_config('/path/to/your/config/dir')

    # now you should be able to get auto-complete hint while typing
    cfg.?

Step 3.
~~~~~~~
cfg4py will take care of log settings automatically, all you need to do is put correct settings into
either (defaults, dev, test, production) config file. And once you change the setting, it should take effect at once.

You can also configure a remote source by implemented a subclass of `RemoteConfigFetcher`. If the remote server is
Redis, then a default redis fetcher is provided:

.. code-block::python
        from cfg4py import RedisConfigFetcher
        from redis import StrictRedis

        cfg = cfg4py.create_config()
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        cfg4py.config_remote_fetcher(fetcher, 1)

The settings in redis under `key` should be a json string, which can be converted into a dict object.

Step 4.
~~~~~~~~
Before starting run your application, you should set __cfg4py_server_role__ to any of [DEV,TEST,PRODUCTIONSITE].
