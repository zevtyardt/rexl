#!/usr/bin/env python

from setuptools import setup, find_packages
from rexl.lib.constants import APP_VERSION

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup (name = "rexl",
       version = APP_VERSION,
       author = "val (zvtyrdt.id)",
       description = "rexl - All in one Penetration Toolkit",
       url = "https://github.com/zevtyardt",
       install_requires = requirements,
       py_modules = ["rexl"],
       packages=find_packages(),
       include_package_data=True,
       zip_safe=False,
       entry_points={'console_scripts': ['rexl-console=rexl.rexl:main']}
)
