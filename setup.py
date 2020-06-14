#!/usr/bin/env python

from setuptools import setup, find_packages
import os

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup (name = "asaki",
       author = "val (zvtyrdt.id)",
       description="Asaki - All in one Penetration Toolkit",
       url = "https://github.com/zevtyardt",
       install_requires=requirements,
       py_modules = ["AsakiConsole"],
       packages=find_packages(),
       include_package_data=True,
       zip_safe=False,
       entry_points={'console_scripts': ['asaki=AsakiConsole:main']}
)
