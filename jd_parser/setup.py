#!/usr/bin/env python
# coding=utf-8


from setuptools import setup,find_packages


setup(
    name="jd_parser_html",
    version = "0.1",
    author = "jkmiao",
    author_email = "miaoweihong@ipin.com",
    description = ("jd_parser of html files with 51job,zhilian,liepin and lagou"),
    install_requires = ["tgrocery","beautifulsoup4","lxml","ipin_rpc_gen_etl","ipin_rpc_gen_common>=0.3"],
    packages = find_packages(),
    )
