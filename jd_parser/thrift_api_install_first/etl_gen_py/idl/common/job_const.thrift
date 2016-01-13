namespace java com.ipin.rpc.common
namespace py ipin.rpc.common.types.job_const

enum IncType {
	/** 其他 */
	INC_TYPE_OTHER = 0,
	/** 国企    国有企业 国有企业    国有企业 */
	INC_TYPE_GUOQI = 1,
	/** 私营·民营企业   私营·民营企业   民营    私营·民营企业 */
	INC_TYPE_MINYING = 2,
	/** 中外合营(合资·合作) 中外合营(合资·合作) 合资    中外合营(合资·合作)  */
	INC_TYPE_HEYING = 3
	/** 外商独资    外商独资·外企办事处 外商独资·外企办事处 外商独资·外企办事处 */
	INC_TYPE_DUZI = 4,
	/** 国内上市公司    上市公司 */
	INC_TYPE_SHANGSHI = 5,
	/** 事业单位    事业单位 */
	INC_TYPE_SHIYE = 6,
	/** 国家机关    政府机关／非盈利机构 政府机关／非盈利机构    政府机关／非盈利机构 */
	INC_TYPE_JIGUAN = 7,
	/** 股份制企业  股份制企业 */
	INC_TYPE_GUFEN = 8,
	/** 代表处  代表处 */
	INC_TYPE_DAIBIAOCHU = 9,
}

enum WorkStatusType {
	/** 应届毕业生 */
	WORK_STATUS_YINGJIE = 1,
	/** 目前离职，随时可以谈新机会 */
	WORK_STATUS_OFFJOB = 2,
	/** 目前在职，希望尽快寻找新机会 */
	WORK_STATUS_ONJOB1 = 3,
	/** 目前在职，有好的机会可以看看 */
	WORK_STATUS_ONJOB2 = 4,
	/** 目前暂无跳槽打算 */
	WORK_STATUS_NOJUMP = 5,
}

enum JobType {
	/** 全职 */
	JOB_TYPE_QUANZHI = 1,
	/** 实习 */
	JOB_TYPE_SHIXI = 2,
	/** 兼职 */
	JOB_TYPE_JIANZHI = 3,
	/** 全/兼职 */
	JOB_TYPE_ALL = 4,
}
