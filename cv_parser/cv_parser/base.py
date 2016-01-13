#!/usr/bin/env python
# coding=utf-8

import re

class CvTopParser(object):

    def __init__(self):

        self.CLEAN_TEXT = re.compile(u"[\s　]|^[）】\)\]\s]|[（【\(\[\s\)）]$")
        self.AGE = re.compile(u"\d+周?岁")
        self.SEX = re.compile(u"男|女")
        self.DOB = re.compile(u"岁[\(（](\d{2,4}年\d{1,2}月)")
        self.EXP = re.compile(u"(\d+)年(以上)?工作经验")

        self.DEGREE = re.compile(u"中专|大专|高中|本科|研究生|硕士|博士|博士后|初中|职校")
        self.POLITIC = re.compile(u"(预备)?党员|团员|群众")
        self.QQ = re.compile(u"[Qq]{1,2}[\s:：　](\d{5,13})")
        self.IDNUM = re.compile(u"身份证号?[\s:：　](\d+[Xx]?)")
        self.PHONE = re.compile(u"\d{11}|\d{3,4}[\-－]\d{8}")
        self.EMAIL = re.compile(u"[\d\w\.]+@[\d\w\.]+")

        self.MARRIAGE = re.compile(u"未婚|已婚|离异|新婚|丧偶|离婚")
        self.HUKOU = re.compile(u"户口[\s:：　](\S+)|籍贯[\s:：](\S+)")
        self.HEIGHT = re.compile(u"(\d{3})cm|身高.(\d{3})")
        self.OVER_SEA = re.compile(u"留学|出国深造|国外就读")
        self.CERT_LEVEL = re.compile(u"[初中高一二三四五六七八九\d]级")
        self.CV_ID = re.compile("ID:(\d+)")


        self.result = {
            "cvid":"",
            "cvFrom":"",
            # 基本信息
            "baseInfo" : {},
            # 求职意向
            "jobExp" : {},
            # 教育经历
            "eduList" : [],
            # 工作经历
            "jobList" : [],
            # 项目经验
            "proList" : [],
            # 培训经历
            "trainList" : [],
            # 语言技能
            "languageList" :[],
            # 证书
            "certList" : [],
            # 技能
            "skillList" : [],
            # 隐私信息
            "privateInfo" : {},
        }

    
    def clean_edu_time(self,eduTime):
        items = re.findall("\d+",eduTime)
        if len(items)==2:
            return '.'.join(items)
        else:
            return eduTime.strip()
