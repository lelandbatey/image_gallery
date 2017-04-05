#!/usr/bin/env python3

import collections
import argparse
import os.path
import os

FileInfo = collections.namedtuple('FileInfo', ['label', 'source', 'dest'])

def compress(cmd, sourcedir, destdir):
    sourcedir = os.path.abspath(sourcedir)
    destdir = os.path.abspath(destdir)
    # Find all the files in the specified path
    sourcepaths = [os.path.join(sourcedir, path)
                   for path in os.listdir(sourcedir) if path.endswith('jpg')]
    # Collect our file information, assembling the current location of each
    # file, and the source location.
    infos = [FileInfo(
        label=os.path.basename(path),
        source=path,
        dest=os.path.join(destdir, os.path.basename(path)))
             for path in sourcepaths]
    for entry in infos:
        torun = cmd.format(input=entry.source, output=entry.dest)
        os.system(torun)


def main():
    parser = argparse.ArgumentParser(
        description='Compress the jpeg images in a source directory and output each to the given destination directory.')
    parser.add_argument('--sourcedir', type=str)
    parser.add_argument('--destdir', type=str)
    parser.add_argument('--cmd', type=str, help="Must contain two '{}' literals of input and output")
    args = parser.parse_args()

    compress(args.cmd, args.sourcedir, args.destdir)


main()
