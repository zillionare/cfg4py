FAQ
===
- Q. What is schema.py? ::

  A. It's generated for code completion. It's safe to keep it in both development environment and release package. Don't try to instantiate it (an TypeError will raise to prevent from instantiate it), you should only use it for typing annotation.

- Q. Why after upgrade to 0.9.0, cfg4py doesn't work as before? ::

  A. v0.9 introduced `strict` mode, which is False by default. What it exactly do is, allow you use cfg4py without set environment variable __cfg4py_server_role__ (non-strict mode). So if you've used cfg4py for a while and it worked, then you need to modify your code where it initialize cfg4py as:

  .. code:: python

    import cfg4py

    # strict is an added param
    cfg4py.init('path_to_config_dir_as_before', strict = True)

  if you don't specify `strict = True`, cfg4py still works, but it will NOT read config under the name 'dev.yaml', 'test.yaml' or 'production.yaml'
