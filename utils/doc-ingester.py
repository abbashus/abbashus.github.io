#!/usr/bin/env python3

'''
- create an index with mapping

    #mappings and analyzer settings
    PUT docs/
    {
      "mappings": {
        "properties": {
          "url" : { "type": "text" },
          "content" : {
            "type": "text",
            "analyzer": "html_analyzer",
            "search_analyzer": "standard"
          },
          "version" : { "type": "keyword" },
          "summary" : {
            "type": "text",
            "index": false
          },
          "type" : {"type": "keyword"}
        }
      },
      "settings": {
        "analysis": {
          "analyzer": {
            "html_analyzer" : {
              "type" :"custom",
              "char_filter": [
                "html_strip"
              ],
              "tokenizer" : "standard",
              "filter" : [
                "lowercase" ,
                "asciifolding" ,
                "stop",
                "edge_ngram"
              ]
            }
          },
          "filter": {
            "edge_ngram" : {
              "type" : "edge_ngram",
              "min_gram": 3,
              "max_gram": 20
            }
          }
        }
      }
    }
- create an alias pointing to created above index
- Ingest the data
    - traverse the doc path until you reach an html file
    - extract heading (or title) and summary from html
    -


- search the queries against the alias
        POST docs/_search
        {
          "query": {
            "match": {
              "content": {
                "query": "disc"
              }
            }
          }
          , "_source":  ["url", "version" , "type" , "summary"]
        }

'''

import sys
from argparse import ArgumentParser
from elasticsearch import Elasticsearch as OpenSearch


def parse_args(argv):
    desc = 'Tool to ingest documentation to OpenSearch cluster for search functionality on opensearch.org'
    usage = '%(prog)s [options]'
    parser = ArgumentParser(description=desc, usage=usage)
    args = parser.parse_args(argv)
    validate_args(args)
    return args


def validate_args(args):
    pass


def main(argv=None):
    args = parse_args(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
