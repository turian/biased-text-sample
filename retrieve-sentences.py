#!/usr/bin/env python
"""
Read one-sentence-per-line from stdin.
Retrieve closest Lucene matches for each sentence, without duplicating retrieved sentences.
(We use a Bloom filter to detect duplicates.)

TODO:
    * Detect duplicates in input sentences too?
    * Remove this bizarre special case:
        querytext = querytext.replace("AND OR", "and or")
        querytext = querytext.replace("OR OR", "or or")
        querytext = querytext.replace("AND and", "and and")
        querytext = querytext.replace("OR AND", "or and")
    http://stackoverflow.com/questions/3452162/lucene-queryparser-interprets-and-or-as-a-command
"""

import sys
import string
import sets

from common.stats import stats
from common.str import percent

DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT = 10

BLOOM_FILTER_SIZE = 1000000000
import numpy
import murmur

import lucene
from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexSearcher, Version, QueryParser

def retrieve(querytext, searcher, queryparser, maxresults=1000):
    querytext = querytext.replace("AND OR", "and or")
    querytext = querytext.replace("OR OR", "or or")
    querytext = querytext.replace("AND and", "and and")
    querytext = querytext.replace("OR AND", "or and")
    query = queryparser.parse(queryparser.escape(querytext))
#    query = QueryParser(analyzer).parse("Find this sentence please")
    hits = searcher.search(query, maxresults)

#    print >> sys.stderr, "Found %d document(s) that matched query '%s':" % (hits.totalHits, query)

    for hit in hits.scoreDocs:
#        print >> sys.stderr, "\t", hit.score, hit.doc, hit.toString()
        doc = searcher.doc(hit.doc)
#        print >> sys.stderr, "\t", doc.get("text").encode("utf-8")
        yield doc.get("text")

if __name__ == "__main__":
    usedsentences = numpy.zeros((BLOOM_FILTER_SIZE,), dtype=numpy.bool)
    print >> sys.stderr, "Just created bloom filter with %d entries" % usedsentences.shape[0]
    print >> sys.stderr, stats()

    lucene.initVM()
    # create an index called 'index-dir' in a temp directory
#    indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
#                            'index-dir')
#    indexDir = "/Tmp/REMOVEME.index-dir"
    indexDir = "lucene.ukwac"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    queryparser = QueryParser(Version.LUCENE_30, "text", analyzer)
    searcher = IndexSearcher(dir)

    nonzeros = 0

    for i, l in enumerate(sys.stdin):
        if i % 100 == 0:
            print >> sys.stderr, "Read %d lines from sys.stdin (bloom filter has %s nonzeros)..." % (i, percent(nonzeros, BLOOM_FILTER_SIZE))
            print >> sys.stderr, stats()
        l = string.strip(l)
        
        added_this_sentence = 0
        for newl in retrieve(l, searcher, queryparser):
            # Iterate until we have added DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT documents
            if added_this_sentence >= DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT: break

            newl = string.strip(newl)

            # Hash the sentence
            idx = murmur.string_hash(newl.encode("utf-8")) % BLOOM_FILTER_SIZE
            # Don't use duplicate sentences
            if usedsentences[idx]: continue

            usedsentences[idx] = True
            nonzeros += 1
            added_this_sentence += 1
            print newl.encode("utf-8")
