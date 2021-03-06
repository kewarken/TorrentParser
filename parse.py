#!/usr/bin/env python

import sys
import time
import getopt
import pprint
from TorrentParse import TorrentParser, TorrentParserError

suffixes = ['B', 'K', 'M', 'G', 'T']

def getLengthStr(length):
    suffixIndex = 0
    while length > 1024:
        length = length / 1024
        suffixIndex = suffixIndex + 1
    return "{}{}".format(round(length,1), suffixes[suffixIndex])

def processTorrent(filename, verbose):
    tp = TorrentParser()
    try:
        tp.parseFile(filename)
    except TorrentParserError as ex:
        print(ex)
        return

    pp = pprint.PrettyPrinter()
    if verbose:
        pp.pprint(tp.getData())

    print("Name: " + tp.getKey("info.name"))
    print("Tracker: " + tp.getKey("announce"))
    print("Created by: " + str(tp.getKey("created by")))
    creationDate = tp.getKey("creation date")
    if(creationDate):
        print("Created on: " + time.ctime(creationDate))
    length = tp.getKey("info.length")
    if length:
        print("Length: " + getLengthStr(length))
    files = tp.getKey("info.files")
    if files:
        for f in files:
            # Not perfectly handled since "path" is a list and I don't know
            # exactly how multiple entries should be used or printed
            print("File: ", end='')
            for p in f["path"] :
                print(p, end="")
            print(" ({})".format(getLengthStr(f["length"])), end='')
            if "md5sum" in f:
                print(" md5sum: " + f["md5sum"])
            else:
                print()
    pieces = tp.getKey("info.pieces")
    if pieces:
        print("Number of pieces: {}".format(len(pieces)))

def main():
    """
Test driver for torrent file parsing library:
    parse.py [-h] [-v] <torrent file> [<torrent file> ...]
        -v: Verbose. Print entire structure.
        -h: Help. Print this message.
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "--verbose"])
    except getopt.error as msg:
        print(msg)
        print("For help use --help")
        sys.exit(1)

    verbose = False

    for o, a in opts:
        if o in ("-h", "--help"):
            print(main.__doc__)
            sys.exit(0)
        elif o in ("-v", "--verbose"):
            verbose = True

    if len(args) == 0:
        print(main.__doc__)
        sys.exit(1)

    for arg in args:
        processTorrent(arg, verbose)
        print()

if __name__ == "__main__":
    main()
