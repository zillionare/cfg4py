#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "watchdog>=0.9.0",
    "apscheduler>=3.6.3",
    "fire>=0.2.1",
    "ruamel.yaml==0.16.0"
]

setup_requirements = []

test_requirements = []

setup(
    author="Aaron Yang",
    author_email='aaron_yang@jieyu.ai',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A python config module support hierarchical configuration and multi-environment deployment",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cfg4py',
    name='cfg4py',
    packages=find_packages(include=['cfg4py', 'cfg4py.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jieyu_tech/cfg4py',
    version='0.6.0',
    zip_safe=False,
    entry_points={
        'console_scripts': ['cfg4py=cfg4py.command_line:main']
    }
)
