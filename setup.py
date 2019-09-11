#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

setup_requirements = ['pytest-runner', ]

setup(
    author="Shiva Adirala",
    author_email='adiralashiva8@gmail.com',
    description='Custom metrics report for pytest',
    long_description='Dashboard view of pytest results created using hook',
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
    license="MIT license",
    include_package_data=True,
    keywords=[
        'pytest', 'py.test', 'metrics',
    ],
    name='pytest-metrics',
    packages=find_packages(include=['pytest_metrics']),
    setup_requires=setup_requirements,
    url='https://github.com/adiralashiva8/pytest-metrics',
    version='0.1',
    zip_safe=True,
    install_requires=[
        'pytest',
        'pytest-runner'
    ],
    entry_points={
        'pytest11': [
            'pytest-metrics = pytest_metrics.plugin',
        ]
    }
)