import json
import logging
import boto3
import os
import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def detectLabels(bucket_name, photo_name):
	client = boto3.client('rekognition', region_name=os.environ["REGION"])
	response = client.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': photo_name}}, MaxLabels=10)
	label_list = []
	for label in response["Labels"]:
		name = label['Name'].lower()
		if ' ' in name:
			print("ignore label with space: ", name)
			continue
		label_list.append(name)
	return label_list


def getMetadata(bucket_name, photo_name):
	client = boto3.client("s3", region_name=os.environ["REGION"])
	response = client.head_object(
		Bucket=bucket_name,
		Key=photo_name
	)

	metadata = {}
	if "Metadata" in response:
		print(response["Metadata"])
		for key, val in response["Metadata"].items():
			metadata[key] = val

	return metadata


def createIndex():
	index_name = "photo"
	host = os.environ["ES_ENDPOINT"]
	credentials = boto3.Session().get_credentials()
	region = os.environ["REGION"]
	service = "es"
	awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
	client = OpenSearch(
		hosts=[{'host': host, 'port': 443}],
		http_auth=awsauth,
		use_ssl=True,
		verify_certs=True,
		connection_class=RequestsHttpConnection
	)

	index_body = {
		'settings': {
			'index': {
				'number_of_shards': 1,
				'number_of_replicas': 0
			}
		}
	}
	response = client.indices.create(index_name, body=index_body)
	print(response)


def storeIndex(document):
	index_name = "photos"
	host = os.environ["ES_ENDPOINT"]
	credentials = boto3.Session().get_credentials()
	region = os.environ["REGION"]
	service = "es"
	awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
	client = OpenSearch(
		hosts=[{'host': host, 'port': 443}],
		http_auth=awsauth,
		use_ssl=True,
		verify_certs=True,
		connection_class=RequestsHttpConnection
	)
	response = client.index(
		index=index_name,
		body=document,
		refresh=True
	)
	print("response: ", response)


def dispatch(event):
	if "Records" not in event:
		return {
			'statusCode': 404,
			'body': json.dumps("event format error!")
		}

	for item in event["Records"]:
		bucket, photo = "", ""
		if "s3" not in item:
			continue
		s3 = item["s3"]
		if "bucket" not in s3 or "object" not in s3:
			continue
		bucket, obj = s3["bucket"], s3["object"]
		if "name" not in bucket or "key" not in obj:
			continue
		bucket_name, photo_name = bucket["name"], obj["key"]
		print(bucket_name, photo_name)
		if bucket_name and photo_name:
			label_list = detectLabels(bucket_name, photo_name)
			print("labels: ", label_list)
			metadata = getMetadata(bucket_name, photo_name)
			print("metadata: ", metadata)
			visited_labels = set()
			index_json = {
				"objectKey": photo_name,
				"bucket": bucket_name,
				"createdTimestamp": str(datetime.datetime.now()),
				"labels": []
			}
			if "customlabels" in metadata:
				custom_labels = json.loads(metadata["customlabels"])
				if isinstance(custom_labels, str):
					index_json["labels"].append(custom_labels)
					visited_labels.add(custom_labels)
				elif isinstance(custom_labels, list):
					for label in custom_labels:
						if isinstance(label, str):
							if label in visited_labels:
								continue
							visited_labels.add(label)
							index_json["labels"].append(label)

			for label in label_list:
				if label in visited_labels:
					continue
				visited_labels.add(label)
				index_json["labels"].append(label)
			print("index_json: ", index_json)

			storeIndex(index_json)
			print("store index for %s-%s succ!" % (bucket_name, photo_name))

	return {
		'statusCode': 200,
		'body': json.dumps('dispatch event succ!')
	}


def lambda_handler(event, context):
	# TODO implement
	logger.debug(event)
	return dispatch(event)
