#!/usr/bin/env python
# coding=utf-8

import re
import sys
import string

reload(sys)
sys.setdefaultencoding('utf-8')

import codecs

# 英文标点符号+中文标点符号
punc = string.punctuation + u'.,;《》？！“”‘’@#￥%…&×（）——+【】{};；●，。&～、|\s:：'+ string.digits+' '+string.letters

print punc

#inputFile = sys.argv[1]
#fr = codecs.open(inputFile,encoding='uft-8'
fr = codecs.open('./train_jkm.txt',encoding='utf-8')
fw = codecs.open('./train_clean.txt','w',encoding='utf-8')

# 利用正则表达式替换为一个空格
for line in fr:
    line = re.sub(r"[{}]+".format(punc)," ",line)
    line = line.replace('（','').replace('）','')
    fw.write(line+' ')

fr.close()
fw.close()
