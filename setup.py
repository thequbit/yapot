#!/bin/env python
# -*- coding: utf8 -*-
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = "0.0.1"

setup(
    name="yapot",
    version=version,
    description="Yet Another PDF OCR Tool",
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
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "wand",
    ],
)

