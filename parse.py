#!/usr/bin/env python
import sys
import getopt
import pprint

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

    def _parseInt(self, f):
        byte = f.read(1)
        num = 0
        while byte and byte != b'e':
            num = num * 10 + int(byte) - int(b'0')
            byte = f.read(1)
        return num

    def _parseByteString(self, f, firstByte):
        num = int(firstByte) - int(b'0')
        byte = f.read(1)
        while byte and byte != b':':
            num = num * 10 + int(byte) - int(b'0')
            byte = f.read(1)
        return f.read(num)

    def _parseDict(self, f):
        print("Starting dict")
        self.stateStack.append({})
        self.isKey.append(True)

    def _parseList(self, f):
        print("Starting list")
        self.stateStack.append([])

    def _addData(self, struct, data):
        if type(struct) is dict:
            if self.isKey[-1]:
                self.keyStack.append(data)
            else:
                key = self.keyStack.pop()
                struct[key] = data
            self.isKey[-1] = not self.isKey[-1]

        elif type(struct) is list:
            struct.append(data)

        else:
            print("Ooops...")

    def getData(self):
        """Return the parsed torrent file data."""
        return self.parsedFile

    def parseFile(self, filename):
        """Parse a torrent file."""
        with open(filename, "rb") as f:
            byte = f.read(1)
            while byte:
                if byte == b'd':
                    self._parseDict(f)

                elif byte == b'i':
                    curStruct = self.stateStack[-1]
                    num = self._parseInt(f)
                    self._addData(curStruct, num)
                    print("Got integer: " + str(num))

                elif byte == b'l':
                    self._parseList(f)

                elif byte == b'e':
                    data = self.stateStack.pop()
                    if type(data) is dict:
                        self.isKey.pop()
                    if len(self.stateStack) == 0:
                        self.parsedFile = data
                        print("Ending" + str(type(data)))
                    else:
                        curStruct = self.stateStack[-1]
                        self._addData(curStruct, data)
                        print("Ending" + str(type(curStruct)))

                elif byte >= b'0' and byte <= b'9':
                    curStruct = self.stateStack[-1]
                    data = self._parseByteString(f, byte)

                    self._addData(curStruct, data)

                    print("Got byte string: " + str(data))

                else:
                    print("That's probably not right...")

                byte = f.read(1)

def processTorrent(filename):
    tp = TorrentParser()
    tp.parseFile(filename)
    pp = pprint.PrettyPrinter()
    pp.pprint(tp.getData())

def main():
    """
Torrent file parsing library. Testable from command line with:
    TorrentParse.py <torrent file> [<torrent file> ...]
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error as msg:
        print(msg)
        print("For help use --help")
        sys.exit(1)

    for o, a in opts:
        if o in ("-h", "--help"):
            print(main.__doc__)
            sys.exit(0)

    if len(args) == 0:
        print(main.__doc__)
        sys.exit(1)

    for arg in args:
        processTorrent(arg) # process() is defined elsewhere

if __name__ == "__main__":
    main()

