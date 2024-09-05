#!/usr/bin/env python
# _*_encoding: utf-8 _*_
import os
import time

import boto3
import json
from pprint import pprint
from decimal import Decimal
from datetime import datetime
from time import strftime


TYPES = ['korean', 'japanese', 'indpak', 'turkish', 'newamerican', 'italian', 'portuguese', 'french', 'chinese', 'mexican']


def create_table(dynamodb=None):
    if not dynamodb:
        # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='yelp-restaurants',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table


def put_restaurants(business_path, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('yelp-restaurants')
    with open(business_path, 'r') as f:
        record = json.load(f, parse_float=Decimal)

    save_fields = dict()
    save_fields["insertedAtTimestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if "id" not in record:
        return "err"

    save_fields["id"] = record["id"] # business id
    save_fields["name"] = ""
    if "name" in record:
        save_fields["name"] = record["name"]

    save_fields["address"] = ""
    save_fields["zip_code"] = ""
    if "location" in record:
        if "display_address" in record["location"]:
            if isinstance(record["location"]["display_address"], list):
                save_fields["address"] = ",".join(record["location"]["display_address"])
            elif isinstance(record["location"]["display_address"], str):
                save_fields["address"] = record["location"]["display_address"]
        elif "address1" in record:
            save_fields["address"] = record["address1"]

        if "zip_code" in record["location"]:
            save_fields["zip_code"] = record["location"]["zip_code"]

    save_fields["coordinates"] = {}
    if "coordinates" in record:
        save_fields["coordinates"] = record["coordinates"]

    save_fields["review_count"] = Decimal(0)
    if "review_count" in record:
        save_fields["review_count"] = record["review_count"]

    save_fields["rating"] = Decimal(0)
    if "rating" in record:
        save_fields["rating"] = record["rating"]

    save_fields["hours"] = ""
    if "hours" in record:
        save_fields["hours"] = record["hours"]

    response = table.put_item(Item=save_fields)
    return response


if __name__ == '__main__':
    # step1: create table using web service
    movie_table = create_table()
    print("Table status:", movie_table.table_status)

    # step2: put items
    business_path = "yelp_data"
    fs = os.listdir(business_path)
    processed_count = 0
    for f in fs:
        if '.' in f:
            continue
        _path = os.path.join(business_path, f)
        resp = put_restaurants(_path)
        if resp == "err":
            print("Put restaurant failed: ", _path)
        else:
            print("Put restaurant succeeded: ", _path)
        pprint(resp, sort_dicts=False)
        time.sleep(1)

        # processed_count += 1
        # if processed_count % 5 == 0:
        #     print("already load: %d items" % processed_count)
        #     time.sleep(5)


