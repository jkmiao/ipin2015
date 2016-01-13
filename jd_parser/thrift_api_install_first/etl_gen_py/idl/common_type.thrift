namespace py ipin.rpc.etl.common_type
namespace java com.ipin.rpc.etl

enum StreamStatus {
    INDEXED = 0
    CRAWLERED = 1
    PARSED = 2
    MEASURED = 3
    MERGED = 4
    VECTORED = 5
    COMPUTED = 6
}

enum ValidStatus{
	NORMAL= 0
	EXPIRED = 1
	DUPLICATED = 2
}

struct Statistics {
    1:string recordId,
    2:i32 timestamp,
    3:string owner,
    4:string accountId,
    5:StreamStatus status,
    6:string pageType,
}

struct JdStatus{
	1: string indexUrl
	2: string owner
	3: i64  createTimeStamp
	4: i64  updateTimeStamp
	5: StreamStatus status
	6: ValidStatus validStatus
}

enum BIND_STATUS {
    HIDDEN= 0
    NORMAL = 1
}
