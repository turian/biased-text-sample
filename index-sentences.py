#!/usr/bin/env python
"""
Read one-sentence-per-line from stdin.
Index each line in Lucene as a separate document.

TODO:
    * Remove previous index, start from scratch.

USAGE:
    /u/turian/data/web_corpus/WaCky2/sentencesplit.py  | ./index-sentences.py

NB we use the StandardAnalyzer, but should try the SnowballAnalyzer
"""

import sys
import string

from common.stats import stats

import lucene
from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexWriter, Version

if __name__ == "__main__":
    lucene.initVM()
    # create an index called 'index-dir' in a temp directory
#    indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
#                            'index-dir')
    indexDir = "/Tmp/REMOVEME.index-dir"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    writer = IndexWriter(dir, analyzer, True, IndexWriter.MaxFieldLength(512))

#    # set variables that affect speed of indexing
#    writer.setMergeFactor(int(argv[2]))
#    writer.setMaxMergeDocs(int(argv[3]))
#    writer.setMaxBufferedDocs(int(argv[4]))
#    # writer.infoStream = System.out
#
#    print "Merge factor:  ", writer.getMergeFactor()
#    print "Max merge docs:", writer.getMaxMergeDocs()
#    print "Max buffered docs:", writer.getMaxBufferedDocs()

    print >> sys.stderr, "Currently there are %d documents in the index..." % writer.numDocs()

    i = 0
    print >> sys.stderr, "Reading lines from sys.stdin..."
    for l in sys.stdin:
        i += 1

        if string.strip(l) == "": continue

        doc = Document()
        doc.add(Field("text", l, Field.Store.YES, Field.Index.ANALYZED))
        writer.addDocument(doc)

        if i % 10000 == 0:
            print >> sys.stderr, "Read %d lines from stdin (%d documents in index)..." % (i, writer.numDocs())
            print >> sys.stderr, stats()
#        if i > 100000: break

    print >> sys.stderr, "Indexed a total of %d lines from stdin (%d documents in index)" % (i, writer.numDocs())
    print >> sys.stderr, "About to optimize index of %d documents..." % writer.numDocs()
    print >> sys.stderr, stats()
    writer.optimize()
    print >> sys.stderr, "...done optimizing index of %d documents" % writer.numDocs()
    print >> sys.stderr, "Closing index of %d documents..." % writer.numDocs()
    print >> sys.stderr, stats()
    writer.close()
    print >> sys.stderr, "...done closing index of %d documents" % writer.numDocs()
    print >> sys.stderr, stats()
