class TorrentParserError(Exception):
    """
Torrent parsing exception. Contains path and character offset of
error
    """
    def __init__(self, path, offset):
        self.path = path
        self.offset = offset

    def __str__(self):
        return "Error parsing file " + self.path + " at file offset " + str(self.offset)

class TorrentParser:
    """Torrent file parsing class. """
    def __init__(self):
        # Algorithm overview:
        #
        # We keep three stacks. The state stack always has the current
        # structure which we're adding to (either a list or a dict).
        #
        # The keyStack is the names of keys which are waiting for values.
        # This allows us to descend into nested structures and know which
        # key the returned value will be set to.
        #
        # The isKey stack is a stack of booleans to know when we have a
        # key-value pair. Every time we get data, we toggle the top of isKey
        # and when isKey is false, we pop a key from keyStack and enter the
        # data with that key. Note that isKey is only relevant to dicts so we
        # only add new values when we add a new dict to stateStack
        self.stateStack = []
        self.keyStack = []
        self.isKey = []
        self.parsedFile = None

    def _parseInt(self):
        byte = self.fileHandle.read(1)
        num = 0
        while byte and byte != b'e':
            num = num * 10 + int(byte) - int(b'0')
            byte = self.fileHandle.read(1)
        return num

    def _parseByteString(self, firstByte):
        num = int(firstByte) - int(b'0')
        byte = self.fileHandle.read(1)
        while byte and byte != b':':
            num = num * 10 + int(byte) - int(b'0')
            byte = self.fileHandle.read(1)
        return self.fileHandle.read(num)

    def _parseDict(self):
        self.stateStack.append({})
        self.isKey.append(True)

    def _parseList(self):
        self.stateStack.append([])

    def _addData(self, struct, data):
        failed = False
        try:
            if type(struct) is dict:
                if self.isKey[-1]:
                    self.keyStack.append(data.decode())
                else:
                    key = self.keyStack.pop()
                    # pieces is a bunch of SHA-1 hashes - don't decode
                    if key != "pieces" and type(data) is bytes:
                        struct[key] = data.decode()
                    else:
                        struct[key] = data
                self.isKey[-1] = not self.isKey[-1]

            elif type(struct) is list:
                if type(data) is bytes:
                    struct.append(data.decode())
                else:
                    struct.append(data)

            else:
                raise TorrentParserError(self.filename, self.fileHandle.tell())
        except TypeError:
            # if the parser gets scrambled, we usually get a type error from
            # trying to hash a list or a dict...catch it and raise our own
            # Python 3 doesn't let us clobber the original and throw our own
            # so cheat and set a flag
            failed = True

        if failed:
            raise TorrentParserError(self.filename, self.fileHandle.tell())


    def getData(self):
        """Return the parsed torrent file data."""
        return self.parsedFile

    def parseFile(self, filename):
        """Parse a torrent file."""
        self.filename = filename
        with open(filename, "rb") as self.fileHandle:
            byte = self.fileHandle.read(1)
            while byte:
                if byte == b'd':
                    self._parseDict()

                elif byte == b'i':
                    curStruct = self.stateStack[-1]
                    num = self._parseInt()
                    self._addData(curStruct, num)

                elif byte == b'l':
                    self._parseList()

                elif byte == b'e':
                    data = self.stateStack.pop()
                    if type(data) is dict:
                        self.isKey.pop()
                    if len(self.stateStack) == 0:
                        self.parsedFile = data
                    else:
                        curStruct = self.stateStack[-1]
                        self._addData(curStruct, data)

                elif byte >= b'0' and byte <= b'9':
                    curStruct = self.stateStack[-1]
                    data = self._parseByteString(byte)

                    self._addData(curStruct, data)

                else:
                    raise TorrentParserError(self.filename, self.fileHandle.tell())

                byte = self.fileHandle.read(1)
