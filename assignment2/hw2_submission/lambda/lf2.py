import json
import os
import boto3
import logging
import inflect
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def process_search_list(search_list):
	singular = inflect.engine()
	validate_list = []
	for label in search_list:
		label = label.lower()
		single_label = singular.singular_noun(label)
		if single_label:
			# label is plural
			validate_list.append((single_label, label))
		else:
			validate_list.append((None, label))

	return validate_list


def extractResponse(response, result1, result2, i):
	if "hits" in response and "hits" in response["hits"]:
		images = response["hits"]["hits"]
		for item in images:
			if "_id" not in item:
				continue

			if i == 0:
				if item["_id"] in result1:
					continue
				result1[item["_id"]] = item
			else:
				if item["_id"] in result2:
					continue
				result2[item["_id"]] = item

def queryIndex(validate_list):
	index_name = "photos"
	host = os.environ["ES_ENDPOINT"]
	credentials = boto3.Session().get_credentials()
	region = os.environ["REGION"]
	service = "es"
	awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,
	                   session_token=credentials.token)
	client = OpenSearch(
		hosts=[{'host': host, 'port': 443}],
		http_auth=awsauth,
		use_ssl=True,
		verify_certs=True,
		connection_class=RequestsHttpConnection
	)

	result1 = dict()
	result2 = dict()
	for i in range(len(validate_list)):
		s_keyword, p_keyword = validate_list[i]
		s_response, p_response = {}, {}
		if s_keyword:
			try:
				print("start search s: %s in open search" % s_keyword)
				s_response = client.search(
					index=index_name,
					q=s_keyword
				)
			except:
				# Handle index_not_found_exception
				s_response = {}

		if p_keyword:
			try:
				print("start search p: %s in open search" % p_keyword)
				p_response = client.search(
					index=index_name,
					q=p_keyword
				)
			except:
				# Handle index_not_found_exception
				p_response = {}

		extractResponse(s_response, result1, result2, i)
		extractResponse(p_response, result1, result2, i)

	if not result2:
		return result1

	result = dict()
	for key, val in result1.items():
		if key in result2:
			result[key] = val

	return result


def extractKeywords(query):
	client = boto3.client("lex-runtime")
	response = client.post_text(
		botName="PhotoSearchBot",
		botAlias="SearchBot",
		userId="test",
		inputText=query,
	)
	search_list = set()
	if "ResponseMetadata" not in response or "HTTPStatusCode" not in response["ResponseMetadata"]:
		return search_list
	if str(response["ResponseMetadata"]["HTTPStatusCode"]) != "200":
		return search_list
	if "slots" not in response:
		return search_list

	slots = response["slots"]
	for key, val in slots.items():
		print("slot: ", key, val)
		if val:
			search_list.add(val)

	search_list = list(search_list)
	validate_list = process_search_list(search_list)
	return validate_list


def process_results(results):
	return_format = []
	for _id, item in results.items():
		if "_source" not in item:
			continue
		source = item["_source"]
		if "objectKey" not in source or "bucket" not in source or "labels" not in source:
			continue
		objectKey = source["objectKey"]
		bucket = source["bucket"]
		labels = source["labels"]
		image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
		return_format.append({"url": image_url, "labels": labels})
	return return_format


def dispatch(event):
	query = event["queryStringParameters"]["q"]
	keywords_list = extractKeywords(query)
	print("labels: ", keywords_list)
	results = queryIndex(keywords_list)
	print("photos: ", results)
	return_format = process_results(results)
	print("search results: ", return_format)

	response = {
		"statusCode": 200,
		"headers": {
			"Content-Type": "application/json",
			"Access-Control-Allow-Origin": "*"
		},
		"body": json.dumps(return_format),
		"isBase64Encoded": False
	}

	return response


def lambda_handler(event, context):
	# TODO implement
	print("event: ", event)
	logger.debug(event)
	return dispatch(event)
