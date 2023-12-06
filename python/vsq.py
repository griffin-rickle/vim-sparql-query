import datetime
from io import StringIO
import json
import os
import requests
import sys
import vim
from mdtable import MDTable
import concurrent.futures


results_buffer = None
results_buffer_idx = None


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


def get_query_type():
    curr_index = 0
    curr_line = vim.current.buffer[0]
    while curr_index < len(vim.current.buffer) and curr_line.startswith('#'):
        curr_index += 1
        curr_line = vim.current.buffer[curr_index]
    query_keyword = curr_line.split(' ')[0]
    return query_keyword


def format_rdf(raw_rdf):
    # return json.dumps(json.loads(raw_rdf), indent=4)
    return raw_rdf
    # ds = rdflib.Dataset()
    # ds.parse(data=raw_rdf, format='json-ld')
    # return ds.serialize(format='trig')


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


def set_buffer_text(completed_future, query_type):
    result = completed_future.result()
    if query_type in ["ASK", "SELECT", "CONSTRUCT"]:
        buffer_text = format_result(result)
        results_buffer[:] = buffer_text.split('\n')
    else:
        if result.status_code == 200:
            print("Database was successfully updated")
        else:
            print(f"ERROR {str(result.status_code)}: result.text")


def buffer_query():
    global results_buffer
    global results_buffer_idx
    endpoint_config = get_config()

    query_endpoint = endpoint_config['endpoint']
    auth = (endpoint_config['auth']['username'], endpoint_config['auth']['password'])

    data = {
        "query": '\n'.join(vim.current.buffer),
        "timeout": 0,
        "useNamespaces": True
    }

    query_type = get_query_type()
    headers = endpoint_config.get(query_type, {}).get("headers", {})
    endpoint_suffix = endpoint_config.get(query_type, {}).get("endpoint", "")

    # if results_buffer hasn't been instantiated yet or the buffer had previously been closed, want
    # to create a new buffer and use that.
    if results_buffer is None:
        vim.command(":new")
        vim.current.window.buffer.options['buftype'] = 'nofile'
        results_buffer = vim.current.buffer
        results_buffer_idx = vim.current.buffer.number
    elif results_buffer.options['bufhidden'] == b'h' or results_buffer.options['bufhidden'] == b'':
        results_buffer[:] = []
        vim.command(f":sb{results_buffer.number}")
    vim.command(':set nowrap')

    # results_buffer[:] = ["Query submitted", str(datetime.datetime.now())]
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(submit_query, query_type_method[query_type], query_endpoint + endpoint_suffix, data, auth, headers)
        result.add_done_callback(lambda x: set_buffer_text(x, query_type))


def new_query():
    vim.command('set hidden')
    vim.command(':vnew')
    vim.command('set syntax=sparql')
