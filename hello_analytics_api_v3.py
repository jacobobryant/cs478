#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple intro to using the Google Analytics API v3.
This application demonstrates how to use the python client library to access
Google Analytics data. The sample traverses the Management API to obtain the
authorized user's first profile ID. Then the sample uses this ID to
contstruct a Core Reporting API query to return the top 25 organic search
terms.
Before you begin, you must sigup for a new project in the Google APIs console:
https://code.google.com/apis/console
Then register the project to use OAuth2.0 for installed applications.
Finally you will need to add the client id, client secret, and redirect URL
into the client_secrets.json file that is in the same directory as this sample.
Sample Usage:
  $ python hello_analytics_api_v3.py
Also you can also get help on all the command-line flags the program
understands by running:
  $ python hello_analytics_api_v3.py --help
"""
# from __future__ import print_function

__author__ = 'api.nickm@gmail.com (Nick Mihailovski)'

import argparse
import sys
import numpy as np 

from googleapiclient.errors import HttpError
from googleapiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError



def hello_analytics_main(argv, start_date, end_date, max_results=str(1000), metrics='ga:sessions', dimensions='ga:pagePath', samplingLevel='HIGHER_PRECISION', include_empty_rows=False, filters='None'):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'analytics', 'v3', __doc__, __file__,
      scope='https://www.googleapis.com/auth/analytics.readonly')

  # Try to make a request to the API. Print the results or handle errors.
  try:
    first_profile_id = get_first_profile_id(service)
    if not first_profile_id:
      print('Could not find a valid profile for this user.')
    else:
      results = get_top_keywords(service, start_date, end_date, first_profile_id, max_results, metrics, dimensions, samplingLevel, include_empty_rows, filters)
      return np.array(results['rows'])
      # print_results(results)

  except TypeError as error:
    # Handle errors in constructing a query.
    print(('There was an error in constructing your query : %s' % error))

  except HttpError as error:
    # Handle API errors.
    print(('Arg, there was an API error : %s : %s' %
           (error.resp.status, error._get_reason())))

  except AccessTokenRefreshError:
    # Handle Auth errors.
    print ('The credentials have been revoked or expired, please re-run '
           'the application to re-authorize')


def get_first_profile_id(service):
  """Traverses Management API to return the first profile id.
  This first queries the Accounts collection to get the first account ID.
  This ID is used to query the Webproperties collection to retrieve the first
  webproperty ID. And both account and webproperty IDs are used to query the
  Profile collection to get the first profile id.
  Args:
    service: The service object built by the Google API Python client library.
  Returns:
    A string with the first profile ID. None if a user does not have any
    accounts, webproperties, or profiles.
  """

  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      if profiles.get('items'):
        return profiles.get('items')[0].get('id')

  return None


def get_top_keywords(service, start_date, end_date, profile_id, max_results, metrics, dimensions, samplingLevel, include_empty_rows, filters):
  """Executes and returns data from the Core Reporting API.
  This queries the API for the top 25 organic search terms by visits.
  Args:
    service: The service object built by the Google API Python client library.
    profile_id: String The profile ID from which to retrieve analytics data.
  Returns:
    The response returned from the Core Reporting API.
  """

  if filters == 'None':
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions=dimensions,
        sort='-'+metrics,
        start_index='1',
        max_results=max_results).execute()                                                                                                                                                                          

  else:
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions=dimensions,
        sort='-'+metrics,
        filters=filters,
        start_index='1',
        max_results=max_results).execute()


def print_results(results):
  """Prints out the results.
  This prints out the profile name, the column headers, and all the rows of
  data.
  Args:
    results: The response returned from the Core Reporting API.
  """

  print
  print('Profile Name: %s' % results.get('profileInfo').get('profileName'))
  print

  # Print header.
  output = []
  for header in results.get('columnHeaders'):
    output.append('%30s' % header.get('name'))
  print(''.join(output))

  # Print data table.
  if results.get('rows', []):
    for row in results.get('rows'):
      output = []
      for cell in row:
        output.append('%30s' % cell)
      print(''.join(output))

  else:
    print('No Rows Found')


def get_views_from_facebook(service, post_page, profile_id, post_date, days_viewed=4):
  global max_results

  #Add a few days after the link was posted to see how much it bumped.
  end_date = post_date.split('-')
  end_date[2] = str(int(end_date[2])+days_viewed)
  end_date = '-'.join(end_date)

  #Then pass that in
  to_return = service.data().ga().get(
    ids='ga:' + profile_id,
    start_date=post_date,
    end_date=end_date,
    metrics='ga:sessions',
    dimensions=post_page,
    sort='-'+metrics,
    filters='ga:medium==organic', #This doesn't make sense, we don't want to filter for just organic if we're trying to find the influence of Facebook.
    start_index='1',
    max_results=max_results).execute() 

if __name__ == '__main__':
  start='2017-08-08'
  end='2017-08-15'
  print hello_analytics_main('0', start, end)