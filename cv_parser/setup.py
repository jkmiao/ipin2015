#!/usr/bin/env python
# coding=utf-8



import os
from setuptools import setup,find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),fname)).read()



setup(
    name="cv_parser_html",
    version = "0.1",
    author = "jkmiao",
    author_email="miaoweihong@ipin.com",
    description = ("An cv_parser of html files with 51job,58tongcheng and zhilian"),
    license = "MIT",
    install_requires = ["beautifulsoup4","lxml","ipin_rpc_gen_etl","ipin_rpc_gen_common>=0.3"],
    packages = find_packages(),
    zip_safe=False,
    long_description = read("README.md"),
    )
