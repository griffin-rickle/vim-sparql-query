import json
import os
import requests
import sys
import vim


def get_config():
    python_dir_ary = sys.path[0].split(os.path.sep)
    config_dir = os.path.sep.join(python_dir_ary[:len(python_dir_ary) - 1])
    config_filepath = os.path.sep.join([config_dir, 'config.json'])
    with open(config_filepath, 'r') as f:
        config = json.load(f)
    return config


def buffer_query():
    endpoint_config = get_config()
    print(json.dumps(endpoint_config, indent=4))

    query_endpoint = endpoint_config['endpoint']
    auth = (endpoint_config['auth']['username'], endpoint_config['auth']['password'])

    data = {
        "query": '\n'.join(vim.current.buffer)
    }

    vim.command(":new")
    result = requests.post(query_endpoint, data=data, auth=auth, headers=endpoint_config['headers'])
    vim.current.window.buffer[:] = result.text.split('\n')
    vim.current.window.buffer.options['buftype'] = 'nofile'
