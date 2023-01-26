import json
import os
import requests
import sys
import vim


results_buffer = None

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


def buffer_query():
    global results_buffer
    endpoint_config = get_config()

    query_endpoint = endpoint_config['endpoint']
    auth = (endpoint_config['auth']['username'], endpoint_config['auth']['password'])

    data = {
        "query": '\n'.join(vim.current.buffer)
    }

    query_type = get_query_type()
    headers = {}
    if query_type in endpoint_config['headers'].keys():
        headers = endpoint_config['headers'][query_type]

    if results_buffer is None:
        vim.command(":new")
        vim.current.window.buffer.options['buftype'] = 'nofile'
        results_buffer = vim.current.buffer

    result = requests.post(query_endpoint, data=data, auth=auth, headers=headers)
    results_buffer[:] = result.text.split('\n')

