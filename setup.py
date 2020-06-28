#!/usr/bin/env python

from setuptools import setup, find_packages
from AsakiConsole.lib.constants import APP_VERSION

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup (name = "asaki",
       version = APP_VERSION,
       author = "val (zvtyrdt.id)",
       description = "Asaki - All in one Penetration Toolkit",
       url = "https://github.com/zevtyardt",
       install_requires = requirements,
       py_modules = ["AsakiConsole"],
       packages=find_packages(),
       include_package_data=True,
       zip_safe=False,
       entry_points={'console_scripts': ['asaki.console=AsakiConsole.asaki:main']}
)
