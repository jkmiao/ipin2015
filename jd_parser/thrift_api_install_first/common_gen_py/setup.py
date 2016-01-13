#!/usr/bin/python
# -*- encoding:utf8 -*-

from setuptools import setup,find_packages


setup(
    name = "ipin_rpc_gen_common",
    version = "0.3",
    packages = find_packages("src"),
    package_dir={"":"src"},
    install_requires=[
        "thrift>=0.9.2"
    ],
)
