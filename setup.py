#!/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup

long_description = \
"""
Yet Another PDF OCR Tool

Makes converting PDF's to Text simple!

"""

version = "0.0.4"

setup(
    name="yapot",
    version=version,
    description="Yet Another PDF OCR Tool",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
    ],
    keywords="pdf,ocr,yapot",
    author="Timothy Duffy",
    author_email="tim@timduffy.me",
    license="GPLv3+",
    packages=['yapot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "wand",
    ],
    url="https://github.com/thequbit/yapot",
)

