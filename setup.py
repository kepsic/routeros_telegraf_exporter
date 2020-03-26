#!/usr/bin/env python

"""The setup script."""
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here,'README.rst')) as readme_file:
    readme = readme_file.read()

with open(os.path.join(here, 'HISTORY.rst')) as history_file:
    history = history_file.read()

requirements = [
                "venusian",
                "simplejson",
                "pyramid",
                "cornice",
                "waitress",
                "routeros_api",
                "pyyaml"
]

setup_requirements = [ ]

test_requirements = [ ]

package_name = "routeros_telegraf_exporter"

setup(
    author="Andres Kepler",
    author_email='andres@kepler.ee',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="RouterOS metrics exporter enables metrics export to Telegraf",
    entry_points={
        'console_scripts': [
            'rte={0}.cli:cli_main'.format(package_name),
            'rte_probe={0}.probe_cli:main'.format(package_name),
        ],
        'paste.app_factory': [
            'main={0}:main'.format(package_name)
        ]
    },
    paster_plugins=['pyramid'],
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='{0}, web service'.format(package_name),
    name='{0}'.format(package_name),
    packages=find_packages(include=[package_name, '{0}.*'.format(package_name)]),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kepsic/{0}'.format(package_name),
    version='0.1.6',
    zip_safe=False,
)
