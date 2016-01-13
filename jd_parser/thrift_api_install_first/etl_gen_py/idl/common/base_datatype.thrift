namespace java com.ipin.rpc.common
namespace py ipin.rpc.common.datatype

struct ServiceAccessToken {
	1:i64 timeStamp = 0,
	2:string randomStr = "",
	3:binary token = "",
}

struct DtShort {
	1:i16 value = 0,
	2:byte flag = 0,
}

struct DtInt {
	1:i32 value = 0,
	2:byte flag = 0,
}

struct DtLong {
	1:i64 value = 0,
	2:byte flag = 0,
}

struct DtDouble {
	1:double value = 0,
	2:byte flag = 0,
}

struct DtString {
	1:string value = "",
	2:byte flag = 0,
}

struct DtBool {
	1:bool value = 0,
	2:byte flag = 0,
}

struct DtByte {
	1:byte value = 0,
	2:byte flag = 0,
}

struct DtDateTime {
	1:i64 timeStamp = 0,
	2:i32 utcOffset = 0,
	3:byte flag = 0,
}
