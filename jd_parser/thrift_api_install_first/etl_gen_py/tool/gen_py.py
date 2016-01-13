#!/usr/bin/python
# -*- coding:utf8 -*-

import argparse
import os

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--common_pkg',required=True)
    parser.add_argument('files',nargs="+")
    return parser.parse_args()

def _gen_source(args):
    absPath = os.path.abspath(__file__)
    curDir = os.path.dirname(absPath)
    thriftPath = os.sep.join([curDir,"thrift"])

    for filename in args.files:
        cmd = "{0} -out src -gen py:new_style,utf8strings {1}".format('thrift',filename)
        os.system(cmd)

def _fix_common_pkg(args):
    parts = args.common_pkg.split(".")
    for i in range(0,len(parts)):
        path = os.sep.join(parts[:i+1])
        path = os.sep.join(["src",path,"__init__.py"])
        with open(path,"w") as f:
            f.truncate(0)
            f.write("__import__(\'pkg_resources\').declare_namespace(__name__)")

def _add_file_coding(realFileName):
    if not realFileName.endswith(".py"):
        return
    #测试是否有coding头
    with open(realFileName) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "#" != line[0:1]:
                continue
            if "-*-" in line and "coding" in line:
                return
    #增加头
    content = None
    with open(realFileName) as f:
        content = f.read()
    with open(realFileName,"w") as f:
        f.truncate(0)
        f.write("# -*- coding:utf8 -*-\n")
        f.write(content)
        f.flush()


def _add_coding(dirName):
    for root,_,fileNames in os.walk(dirName):
        for fileName in fileNames:
            realFileName = os.sep.join([root,fileName])
            _add_file_coding(realFileName)

def _remove_unneed_file(dirName):
    for root,_,fileNames in os.walk(dirName):
        for fileName in fileNames:
            if not fileName.endswith("-remote"):
                continue
            realFileName = os.sep.join([root,fileName])
            os.unlink(realFileName)


if __name__ == "__main__":
    args = _parse_args()
    _gen_source(args)
    os.unlink("src/__init__.py")
    _fix_common_pkg(args)
    _add_coding("src")
    _remove_unneed_file("src")
