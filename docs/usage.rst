=====
Usage
=====

Very Baisc
----------

To use PyConfig in a project::

    import pyconfig

    # create config object
    cfg = pyconfig.create_config(path_to_config_dir, dump_on_change=True)

    # then refer to settings by cfg's properties
    # given the following yaml settings (filename: defaults.yaml) under path_to_config_dir

    # services:
    #   redis:
    #       host: localhost

    print(cfg.services.redis.host)

    # this will raise exceptions
    print(cfg["services"])

Exhausted Guide
---------------

Step 1.
~~~~~~~
Prepare configuration folder (could be in your home dir, like `~/.my_great_app/`, or any place), and place the
following files under it:
    1. defaults.yml
    2. dev.yml
    3. test.yml
    4. production.yml

both .yml and .yaml is supported, but only on kind one time. json is supported too.

defaults.yml consists of all default settings, usually very safe settings, for example, let database settings points to
`localhost`, so even if code goes wrong, you'll not destroy production site database.

Then put you development settings in dev.yml. For example, you're developing on a windows machine, so the log output
should be something like 'c:\\my_great_app\log\my_great_app.log', instead of '/var/log/my_great_app.log', which
should be settings for production site.

Tester may have other different settings too. So configure it in test.yml file. And write all production site
settings in production.yml.

Be aware that pyconfig is hierarchical design, so you should put all common settings in defaults.yml, then they'll be
share by all enviroment, as long as it's not overwritten.

Step 2.
~~~~~~~
Set environment variable __pyconfig_server_role__ as one of 'DEV', 'TEST', 'PRODUCTION', according to the machine's
role.

Step 3.
~~~~~~~
Build config class, add the path to python path, and import it into your project:

.. code-block:: console
    pyconfig build /path/to/your/config/dir

.. code-block::python
    from pyconfig_auto_gen import Config
    import pyconfig

    cfg: Config = pyconfig.create_config('/path/to/your/config/dir')

    # now you should be able to get auto-complete hint while typing
    cfg.?

Step 4.
~~~~~~~
Additionally, pyconfig will take care of log settings automatically, all you need to do is put correct settings into
either (defaults, dev, test, production) config file. And once you change the setting, it should take effect at once.

You can also configure a remote source by implemented a subclass of `RemoteConfigFetcher`. If the remote server is
Redis, then a default redis fetcher is provided:

.. code-block::python
        from pyconfig import RedisConfigFetcher
        from redis import StrictRedis

        cfg = pyconfig.create_config()
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        pyconfig.config_remote_fetcher(fetcher, 1)

The settings in redis under `key` should be a json string, which can be converted into a dict object.
