# -*- coding:utf8 -*-
# -*- coding:utf8 -*-
#!/usr/bin/python
# -*- encoding:utf8 -*-

from setuptools import setup,find_packages


setup(
    name = "ipin_rpc_gen_etl",
    version = "0.0.1",
    packages = find_packages("src"),
    package_dir={"":"src"},
    install_requires=[
        "ipin_rpc_gen_common>=0.3"
    ],
)
