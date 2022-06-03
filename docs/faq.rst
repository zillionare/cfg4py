FAQ
===
1. What is schema.py?

  It's generated for code completion. It's safe to keep it in both development environment and release package. Don't try to instantiate it (an TypeError will raise to prevent from instantiate it), you should only use it for typing annotation.

2. Why after upgrade to 0.9.0, cfg4py doesn't work as before?

  v0.9 introduced `strict` mode, which is False by default. When cfg4py is initialized with ```strict = True```, cfg4py works only if __cfg4py_server_role__ is set; if it's non-strict mode, cfg4py works with __cfg4py_server_role__ is not set.

  So if you've used cfg4py for a while and it worked before v0.9, then you need to modify your code where it initialize cfg4py as:

  .. code:: python

    import cfg4py

    # strict is an added param
    cfg4py.init('path_to_config_dir_as_before', strict = True)

  if you don't specify `strict = True`, cfg4py still works, but it will NOT read config under the name 'dev.yaml', 'test.yaml' or 'production.yaml'

3. Why `cfg.logging` acts like dict? 

  Because `cfg.logging`` is a dict. `cfg.logging` is provided since 0.9.3, in case one may need it, for example, get the log file location. However, logging settings may contains key that is python's reserved word, thus it's not possible to convert it into python's object (It's not allowed to use python's reserved word as object's member)
