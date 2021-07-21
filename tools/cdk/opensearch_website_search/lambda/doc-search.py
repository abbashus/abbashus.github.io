import json
import requests
import os
from requests.auth import HTTPBasicAuth

# region = 'us-west-2'
# service = 'es'

nlb_opensearch_port = '80'
username = os.getenv('SEARCH_USER')
password = os.getenv('SEARCH_PASS')
nlb_endpoint = os.getenv('NLB_ENDPOINT')
host = 'http://' + nlb_endpoint + ':' + nlb_opensearch_port
index = 'docs'

http_basic_auth = HTTPBasicAuth(username, password)


def handler(event, context):
  print(event)

  # print("query: " + event['queryStringParameters']['q'])

  # if the user and password for search is present in Env variable invoke a CW alarm
  # 5XX error from ELB
  # 5XX from OpenSearch cluster

  # Put the user query into the query DSL for more accurate search results.
  # Note that certain fields are boosted (^).

  query = {
    "query": {
      "match": {
        "content": {
          "query": "security"  # event['queryStringParameters']['q'] # 'security'
        }
      }
    },
    "_source": ["url", "version", "type", "summary"],
    "size": 20
  }

  # cluster_health_url = host + '/_cluster/health?pretty'
  search_url = host + '/' + index + '/_search'

  # ES 6.x requires an explicit Content-Type header
  headers = {"Content-Type": "application/json"}

  # r = requests.get(cluster_health_url, auth=http_basic_auth, headers=headers, verify=False)
  r = requests.get(search_url, auth=http_basic_auth, headers=headers, data=json.dumps(query), verify=False)

  response = {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False,
    "body": r.text}  # Add the search results to the response

  return response
