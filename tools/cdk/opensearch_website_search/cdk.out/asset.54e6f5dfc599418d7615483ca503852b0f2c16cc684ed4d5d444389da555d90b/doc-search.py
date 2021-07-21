import json
import requests
import os
from requests.auth import HTTPBasicAuth

#region = 'us-west-2'
#service = 'es'

nlb_opensearch_port = '443'
username = os.getenv('SEARCH_USER')
password = os.getenv('SEARCH_PASS')
nlb_endpoint = os.getenv('NLB_ENDPOINT')
host = 'https://' + nlb_endpoint + ':' + nlb_opensearch_port

http_basic_auth = HTTPBasicAuth(username, password)

def handler(event, context):

  # if the user and password for search is present in Env variable invoke a CW alarm
  # 5XX error from ELB
  # 5XX from OpenSearch cluster

  cluster_health_url = host + '/_cluster/health?pretty'

  # ES 6.x requires an explicit Content-Type header
  # headers = {"Content-Type": "application/json"}

  # r = requests.get(cluster_health_url, auth=http_basic_auth, headers=headers, verify=False) # with headers
  r = requests.get(cluster_health_url, auth=http_basic_auth, verify=False)

  response = {
    "statusCode": 200,
    "headers": {
      "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False,
    "body": r.text}   # Add the search results to the response

  # return {
  #   'statusCode': 200,
  #   'body': 'Lambda was invoked successfully.'
  # }

  return response
