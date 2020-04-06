PyConfig
========

!\[\](<https://img.shields.io/pypi/v/pyconfig.svg>)
!\[\](<https://img.shields.io/travis/jieyu-tech/pyconfig.svg>)
!\[\](<https://readthedocs.org/projects/pyconfig/badge/?version=latest>)

A hierarchical, multi-env (dev, test, production) supported config
module

-   Free software: BSD license
-   Documentation: <https://pyconfig.readthedocs.io>.

Features
--------

### Hierarchical Design

In a large scale application, the following scenario is quite common:

You have a bunch of severs of the same role, which usually share same
configuration. But somehow for troubleshooting or maintenance purpose,
you'd like some particular machines could have its own settings at some
particular moment.

At most occasions we'll solve the problem this way:

1. The most broad used settings are in a central database or provided by a service. To save time for editing, these

:   settings are at server-role granularity, not machine/instance bound.

3\. Your application code (with pyconfig module) will provide a default
configuration set, which are least important , used only if the
application cannot talk to the central configuration service. In that
case, the application can still run with downgraded quality, but is
surely better than no service. 3. Each local machine could have local
config files for overwriting central settings.

That's the three-level hierarchical configuration design. The default settings value which put in the config module

:   

    (or your code) is least important, they'll serve only if no settings can be retrieved elsewhere. The settings

    :   resides on local machines, are the most important, once exists,
        will override all other settings.

Adaptive Deployment Environment Support
---------------------------------------

### Credits

This package was created with Cookiecutter\_ and the
audreyr/cookiecutter-pypackage\_ project template.

\[Cookiecutter\]: <https://github.com/audreyr/cookiecutter>
\[audreyr/cookiecutter-pypackage\]:
<https://github.com/audreyr/cookiecutter-pypackage>
