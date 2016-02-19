#!/usr/bin/env python
import StringIO
import gzip
import os
import struct
import threading
#from os.path import join, getsize

class FileSaver:
    def __init__(self, fn):
        self.fw = open(fn, 'a+b')
        self.lock = threading.Lock()

    def __del__(self):
        self.fw.close()

    def append(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        with self.lock:
            self.fw.write(value+"\n")
            self.fw.flush()


class BinSaver:
    @staticmethod
    def compress_item(name, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(name, unicode):
            name = name.encode('utf-8')

        fo = StringIO.StringIO()
        f = gzip.GzipFile(fileobj=fo, mode='wb')
        f.write(value)
        f.close()

        r = fo.getvalue()
        fo.close()
        return struct.pack("I", len(name)) + name + struct.pack("I", len(r)) + r

    def __init__(self, fn):
        self._fd = open(fn, 'a+b')
        self._locker = threading.Lock()
        self._fn = fn

    def __del__(self):
        self._fd.close()

    def append(self, name, value):
        a = BinSaver.compress_item(name, value)
        pos = 0
        with self._locker:
            pos = self._fd.tell()
            self._fd.write(a)
            self._fd.flush()
        return pos

    def filename(self):
        return self._fn

    def getsize(self):
        filename = os.path.abspath(self.filename())
        #print "filename======",filename
        size = os.path.getsize(filename)
        #print "size======",size
        return size


class BinReader:
    def __init__(self, fn):
        self._fsz = float(os.path.getsize(fn))
        self._nread = 0
        self.fd = open(fn, 'rb')
        self.lock = threading.Lock()

    def __del__(self):
        self.fd.close()

    def _readone_i(self):
        sz0 = self.fd.read(4)
        if len(sz0) == 0:
            return (None,None)

        if len(sz0) != 4:
            raise IOError('invalid file')

        (sz,) = struct.unpack("I", sz0)
        fn = self.fd.read(sz)
        if len(fn) != sz:
            raise IOError('invalid file')

        self._nread += sz+4

        sz0 = self.fd.read(4)
        if len(sz0) != 4:
            raise IOError('invalid file')

        (sz,) = struct.unpack("I", sz0)
        gzconn = self.fd.read(sz)
        
        if len(gzconn) != sz:
            raise IOError('invalid file')

        self._nread += sz+4

        fin = StringIO.StringIO(gzconn)

        with gzip.GzipFile(fileobj=fin, mode='rb') as f:
            conn = f.read()

        fin.close()
        return (fn, conn)

    def progress(self):
        if self._fsz == 0.0:
            return 1.0
        return float(self._nread) / self._fsz

    def readone(self):
        with self.lock:
            return self._readone_i()

    def readone_at(self, pos):
        with self.lock:
            self.fd.seek(pos)
            return self._readone_i()


if __name__ == "__main__":
    t = BinReader('cv_51job.22252.bin')
    while True:
        (a,b) = t.readone()
        if a is None:
            break
        print '\r',a,
        print b[:100]
        with open(a,'wb') as fw:
            fw.write(b)


