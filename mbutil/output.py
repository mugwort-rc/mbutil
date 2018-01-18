import os, tarfile, io, datetime


class Output:
    def __init__(self, path):
        self.name = path
        self._tarfp = None
        self._init()

    def _init(self):
        if self.is_tar():
            self._tarfp = tarfile.open(self.name, "w")
        else:
            os.mkdir("%s" % self.name)

    def is_tar(self):
        root, ext = os.path.splitext(self.name)
        return ext == ".tar"

    def open(self, filepath, mode):
        if self.is_tar():
            return VirtualFile(filepath, mode, self)
        else:
            return open(os.path.join(self.name, filepath), mode)

    def makedirs(self, path): 
        if self.is_tar():
            return
        dirpath = os.path.join(self.name, path)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)


class VirtualFile:
    def __init__(self, filepath, mode, output):
        self.info = tarfile.TarInfo(filepath)
        self.mode = mode
        self.output = output
        self._bfp = io.BytesIO()
        self._closed = False
        if "b" in self.mode:
            self._fp = self._bfp
        else:
            self._fp = io.TextIOWrapper(self._bfp)

    def __del__(self):
        self.close()

    def write(self, data):
        return self._fp.write(data)

    def close(self):
        if self._closed:
            return
        self.info.size = self._bfp.tell()
        self.info.mtime = datetime.datetime.now().timestamp()
        self._bfp.seek(0)
        self.output._tarfp.addfile(self.info, self._bfp)
        self._closed = True
