# first line: 236
@memory.cache
def get_num_results(name):
    params = {'key': secrets.google_custom_search_api_key,
              'cx': search_engine_id,
              'q': name}
    query = ("https://www.googleapis.com/customsearch/v1?" +
             "alt=json&fields=queries(request(totalResults))&" +
            urlencode(params))
    response = requests.get(query)
    return int(response.json()['queries']['request'][0]['totalResults'])
