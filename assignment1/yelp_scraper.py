# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.

This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.

This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import os.path
import pprint
import requests
import sys
import urllib


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

API_KEY = "5QgaeDBM5yIAMvRW2hBmPeXAFFZJnbpqzH8_rs0_FkQUfwJCVPTqgklNzEJILsfRpiyTLgu67N525RXXQZj7wt31FKkTuIm45Za4A3WZNKrG8gQHyO3mDvF2ATD_YXYx"

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

STORE_PATH = 'yelp_data'


# Defaults for our simple example.
DEFAULT_TERM = 'restaurants'
# DEFAULT_LOCATION = 'San Francisco, CA'
DEFAULT_LOCATION = 'Manhattan, NY'
SEARCH_LIMIT = 50

DEFAULT_CATEGORIES = 'newamerican'


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location, categories, offset):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': int(SEARCH_LIMIT),
        'categories': categories.replace(' ', '+'),
        'offset': int(offset),
        'radius': int(40000)
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(term, location, categories, offset):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(API_KEY, term, location, categories, offset)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, location))
        return

    print(u'{0} businesses found...'.format(len(businesses)))
    for i in range(len(businesses)):
        business_id = businesses[i]['id']
        filepath = os.path.join(STORE_PATH, business_id)
        if os.path.exists(filepath):
            continue

        response = get_business(API_KEY, business_id)
        print(u'Result for business "{0}" found:'.format(business_id))
        with open(filepath, 'w') as f:
            json.dump(response, f, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')
    parser.add_argument('-c', '--categories', default=DEFAULT_CATEGORIES,
                        type=str, help='Search cuisine')

    input_values = parser.parse_args()
    try:
        offset = 1
        while offset < 1000:
            query_api(input_values.term, input_values.location, input_values.categories, offset)
            offset += 50

    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
