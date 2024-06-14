import datetime
from io import StringIO
import json
import os
import requests
import sys
from mdtable import MDTable

query_type_method = {
    'SELECT': requests.get,
    'ASK': requests.get,
    'CONSTRUCT': requests.get,
    'INSERT': requests.post,
    'DELETE': requests.post
}


def get_config():
    python_dir_ary = sys.path[0].split(os.path.sep)
    config_dir = os.path.sep.join(python_dir_ary[:len(python_dir_ary) - 1])
    config_filepath = os.path.sep.join([config_dir, 'config.json'])
    with open(config_filepath, 'r') as f:
        config = json.load(f)
    return config


def get_query_type(query):
    lines = query.split('\n')
    curr_index = 0
    curr_line = lines[0]
    while curr_index < len(lines) and curr_line.startswith('#'):
        curr_index += 1
        curr_line = lines[curr_index]
    query_keyword = curr_line.split(' ')[0]
    return query_keyword


def format_rdf(raw_rdf):
    return raw_rdf


def format_result(result):
    if 'Content-Type' in result.headers.keys() and result.headers['Content-Type'] == 'application/trig':
        return format_rdf(result.text)
    else:
        markdown = MDTable(StringIO(result.text))
        output = StringIO()
        output.write(markdown.get_table())
        return output.getvalue()


def submit_query(request_method, query_endpoint, data, auth, headers):
    result = request_method(query_endpoint, params=data, auth=auth, headers=headers)
    return result


def set_buffer_text(result, query_type):
    if query_type in ["ASK", "SELECT", "CONSTRUCT"]:
        buffer_text = format_result(result)
        print(buffer_text)
    else:
        if result.status_code == 200:
            print("Database was successfully updated")
        else:
            print(f"ERROR {str(result.status_code)}: {result.text}")


def buffer_query(query):

    endpoint_config = get_config()

    query_endpoint = endpoint_config['endpoint']
    auth = (endpoint_config['auth']['username'], endpoint_config['auth']['password'])

    data = {
        "query": query,
        "timeout": 0,
        "useNamespaces": True
    }

    query_type = get_query_type(query)
    headers = endpoint_config.get(query_type, {}).get("headers", {})
    endpoint_suffix = endpoint_config.get(query_type, {}).get("endpoint", "")

    print("Query submitted", str(datetime.datetime.now()))
    result = submit_query(query_type_method[query_type], query_endpoint + endpoint_suffix, data, auth, headers)
    set_buffer_text(result, query_type)


if __name__ == "__main__":
    lines = [line for line in sys.stdin.readlines()]
    input_string = ''.join([line.replace('\\n', '\n') for line in lines])
    buffer_query(input_string)
