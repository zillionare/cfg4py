
# History

!!! Info
    `(#{number})` means an issue of this project. You may check details of the issue by visiting https://github.com/zillionare/cfg4py/issues/_{number}_

## 0.9.3 (2022-06-03)

* on apple m1, it's not able to watch file changes, and cause cfg4py fail. This revision will disable hot-reload in such scenario and user can still use all other functions of cfg4py.
* remove support for python 3.6 since it's out of service, and opt 3.10, 3.11 in
* (#4) log settings are now available by `cfg.logging`. 

## 0.9.2 (2021-12-17)

* (#1) hot-reload will now only react to configuration files's change.

## 0.9.0 (2020-12-03)

* add strict mode: default is non-strict mode, which allows you run cfg4py without set environment variable __cfg4py_server_role__

    this is a **break** change. If you've used cfg4py in your project and it worked well, after upgrade to 0.9.0, you have to modify your init code as this:

```python

    cfg4py.init('path_to_config_dir', strict = True)
```
    see more in usage and FAQ document

## 0.8.0 (2020-11-22)

* rename cfg4py_auto_gen.py to schema.py

## 0.7.0 (2020-10-31)

* support environment macro

## 0.5.0 (2020-04-30)

* add command hint, set_server_role
* export envar
* add pip source, conda source

## 0.1.0 (2020-04-06)

* First release on PyPI.








