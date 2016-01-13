# -*- coding:utf8 -*-
# -*- coding:utf8 -*-
#!/usr/bin/python
# -*- encoding:utf8 -*-

import sys
import os

rewriteMap = {}
def _do_convert(dirPath,fileName):
    tmpList = []
    fileName = "{}/{}".format(dirPath,fileName)
    with open(fileName) as f:
        for line in f:
            for k,v in rewriteMap.items():
                if k in line:
                    line = line.replace(k,v)
                    break
            tmpList.append(line)
    with open(fileName,"wb") as f:
        f.truncate(0)
        for line in tmpList:
            f.write(line)
        f.flush()

for argv in sys.argv[1:]:
    parts = argv.split(":")
    if 2 == len(parts):
        rewriteMap[parts[0]] = parts[1]

for dirPath,_,fileNames in os.walk("."):
    for fileName in fileNames:
        if fileName.endswith(".go"):
            _do_convert(dirPath,fileName)



