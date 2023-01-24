import os
import requests
import sys
import vim

def buffer_query():

    params = {
        "run": ' Run Query ',
        "timeout": 30000,
        "default_graph_uri": '',
        "format": "text/plain",

    }
    buffer_query = '\n'.join(vim.current.buffer)
    params['query'] = buffer_query
    endpoint = "https://lod.openlinksw.com/sparql/"

    vim.command(":new")

    # vim.command("sblast")
    tmp_file = "/tmp/test.sq"

    result = requests.get(endpoint, params=params)

    vim.current.window.buffer[:] = result.text.split('\n')
    vim.current.window.buffer.options['buftype'] = 'nofile'
