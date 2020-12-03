=======
History
=======

0.1.0 (2020-04-06)
------------------

* First release on PyPI.

0.5.0 (2020-04-30)
-------------------

* add command hint, set_server_role
* export envar
* add pip source, conda source

0.7.0 (2020-10-31)
-------------------
* support environment macro

0.8.0 (2020-11-22)
-------------------
* rename cfg4py_auto_gen.py to schema.py

0.9.0 (2020-12-03)
---------------------
* add strict mode: default is non-strict mode, which allows you run cfg4py without set environment variable __cfg4py_server_role__

    this is a **break** change. If you've used cfg4py in your project and it worked well, after upgrade to 0.9.0, you have to modify your init code as this:

.. code::

    cfg4py.init('path_to_config_dir', strict = True)

    see more in usage and FAQ document
