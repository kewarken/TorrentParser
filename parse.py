#!/usr/bin/env python

import sys
import getopt
import pprint
from TorrentParse import TorrentParser, TorrentParserError


def processTorrent(filename):
    tp = TorrentParser()
    try:
        tp.parseFile(filename)
    except TorrentParserError as ex:
        print(ex)
        return
    pp = pprint.PrettyPrinter()
    pp.pprint(tp.getData())

def main():
    """
Test driver for torrent file parsing library:
    parse.py <torrent file> [<torrent file> ...]
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
        processTorrent(arg)

if __name__ == "__main__":
    main()

