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
    Document, Field, StandardAnalyzer, IndexSearcher, Version, QueryParser

if __name__ == "__main__":
    lucene.initVM()
    # create an index called 'index-dir' in a temp directory
#    indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
#                            'index-dir')
    indexDir = "/Tmp/REMOVEME.index-dir"
#    indexDir = "lucene.ukwac"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    searcher = IndexSearcher(dir)

    query = QueryParser(Version.LUCENE_30, "text", analyzer).parse("Find this sentence please")
#    query = QueryParser(analyzer).parse("Find this sentence please")
    hits = searcher.search(query, 1000)

    print "Found %d document(s) that matched query '%s':" % (hits.totalHits, query)

    for hit in hits.scoreDocs:
        print hit.score, hit.doc, hit.toString()
        doc = searcher.doc(hit.doc)
        print doc.get("text").encode("utf-8")
