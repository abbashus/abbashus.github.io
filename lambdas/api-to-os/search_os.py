import boto3
import json
import requests
import os
from requests.auth import HTTPBasicAuth
# from requests_aws4auth import AWS4Auth

region = 'us-west-2' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
username = os.getenv('SEARCH_USER')
password =   os.getenv('SEARCH_PASS')
http_basic_auth = HTTPBasicAuth(username, password)

host = 'https://search-website-search-hmukl66qvipodicpaoxwwh67zi.us-west-2.es.amazonaws.com' # The ES domain endpoint with https:// and a trailing slash
index = 'docs'
url = host + '/' + index + '/_search'
# url = host + '_cat/indices?v'

# Lambda execution starts here
def lambda_handler(event, context):

    print("query: " + event['queryStringParameters']['q'])

    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query =  {
          "query": {
            "match": {
              "content": {
                "query": event['queryStringParameters']['q']
              }
            }
          }
          , "_source":  ["url", "version" , "type" , "summary"]
        }


    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=http_basic_auth, headers=headers, data=json.dumps(query))
    # r = requests.get(url, auth=http_basic_auth, headers=headers)

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = r.text
    return response