#!/usr/bin/env python
# coding=utf-8


from pymongo import MongoClient
from bson.json_util import dumps

from multiprocessing import Pool


client = MongoClient("mongodb://localhost:27017/irectory")
db = client.jd_51job_raw

print db


cols = db.collection_names(include_system_collections=False)
cols = sorted(cols)
print cols

def del_jobDiploma(colName):
    print "=="*20,colName
    col = db.get_collection(colName)
    for item in col.find():
        col.update({"_id",item["_id"]},{"$set":{"jdJob.jobDiploma":item["jobDiploma"]}})
    col.update({},{"$unset":{"jobDiploma":""}},multi=True)
    print dumps(col.find_one(),ensure_ascii=False,indent=4)
    print ""


pools = Pool(10)
pools.map(del_jobDiploma,cols)
