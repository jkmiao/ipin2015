namespace py jd

const string EMPTY_FIELD  = "EMPTY_VALUE"
const string NO_LIMIT_FIELD  = "NO_LIMIT_VALUE"

struct JD_RESULT_DATA{
    1: string incName,
    2: string incUrl,
    3: string incScale,
    4: string incIntro,
    5: string incIndustry,
    6: string incPlace,
    7: string pub_time,
    8: string end_time,
    9: string jobName,
    10: string jobType,
    11: string jobCate, 
    12: string sex,
    13: string jobNum,
    14: list<string> age,
    15: list<string> major,
    16: string degree,
    17: list<string> exp,
    18: list<string> skill,
    19: list<string> cert,
    20: list<string> pay,
    21: string workplace,
    22: string demand,
    23: string duty,
    24: string benefit,
    25: string youbian,
    26: string other
    27: string minAge,
    28: string maxAge,
}
struct JdRaw {
	1:string jdId,
	2:string jdFrom,
	3:string jdUrl,
	4:JdIncRaw jdInc = {},
	5:JdJobRaw jdJob = {},
    6:jd_remedy.JdRemedyRaw remedyInfo = {},
	8:base_datatype.DtString pubDate = {},
}

map = dict()
jdRawMap = dict()
jdRawMap['jdId'] = map.pop("jdInc", "")

jdRaw = JdRaw(**jdRawMap)


service JD_Parser{
    JD_RESULT_DATA parser(1:string jd_html,2:string jd_from)
}
