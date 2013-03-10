#!/usr/bin/env python
# Copyright (C) 2013 Tobias Gruetzmacher
"""
This script takes the JSON file created by 'dosage -o json' and uses the
metadata to build a symlink farm in the deduced order of the comic. It created
those in a subdirectory called 'inorder'.
"""
from __future__ import print_function
import sys
import os
import codecs
import json

def jsonFn(d):
    return os.path.join(d, 'dosage.json')

def loadJson(d):
    with codecs.open(jsonFn(d), 'r', 'utf-8') as f:
        data = json.load(f)
    return data

def prepare_output(d):
    outDir = os.path.join(d, 'inorder')
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    for f in os.listdir(outDir):
        f = os.path.join(outDir, f)
        if os.path.islink(f):
            os.remove(f)
    return outDir

def create_symlinks(d):
    data = loadJson(d)
    outDir = prepare_output(d)

    unseen = data["pages"].keys()
    while len(unseen) > 0:
        latest = work = unseen[0]
        while work in unseen:
            unseen.remove(work)
            if "prev" in data["pages"][work]:
                work = data["pages"][work]["prev"]
    print("Latest page: %s" % (latest))

    order = []
    work = latest
    while work in data["pages"]:
        order.extend(data["pages"][work]["images"].values())
        if "prev" in data["pages"][work]:
            work = data["pages"][work]["prev"]
        else:
            work = None
    order.reverse()

    for i, img in enumerate(order):
        os.symlink(os.path.join('..', img), os.path.join(outDir, '%05i_%s' % (i, img)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for d in sys.argv[1:]:
            if os.path.exists(jsonFn(d)):
                create_symlinks(d)
            else:
                print("No JSON file found in '%s'." % (d))
    else:
        print("Usage: %s comic-dirs" % (os.path.basename(sys.argv[0])))

