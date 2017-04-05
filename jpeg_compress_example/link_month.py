#!/usr/bin/env python3

import collections
import argparse
import os.path
import os

from pprint import pprint

FileInfo = collections.namedtuple('FileInfo', ['label', 'source', 'dest'])


def link_month(month, sourcedir, destdir):
    sourcedir = os.path.abspath(sourcedir)
    destdir = os.path.abspath(destdir)
    # Find all the files with the given month in the specified path
    sourcepaths = [os.path.join(sourcedir, path)
                   for path in os.listdir(sourcedir)
                   if path.split('-')[1] == month]

    # Collect our file information, assembling the current location of each
    # file, and the source location.
    infos = [FileInfo(
        label=os.path.basename(path),
        source=path,
        dest=os.path.join(destdir, os.path.basename(path)))
             for path in sourcepaths]

    for entry in infos:
        if os.path.exists(entry.dest):
            print(
                "File named '{}' has destination '{}' that already exists; skipping".
                format(entry.label, entry.dest))
            continue
        os.symlink(entry.source, entry.dest)


def main():
    parser = argparse.ArgumentParser(
        description='Link the pictures in some month into another folder.')
    parser.add_argument('--month', type=str)
    parser.add_argument('--sourcedir', type=str)
    parser.add_argument('--destdir', type=str)

    args = parser.parse_args()
    link_month(args.month, args.sourcedir, args.destdir)


if __name__ == '__main__':
    main()
