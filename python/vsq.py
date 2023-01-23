import os
import requests
import sys
import vim

def test_query():
    params = {
        "query": """SELECT * WHERE {?s a ?o} limit 100""",
        "run": ' Run Query ',
        "timeout": 30000,
        "default_graph_uri": '',
        "format": "text/plain",

    }
    endpoint = "https://lod.openlinksw.com/sparql/"

    vim.command(":new")
    vim.command("sbNext")

    result = requests.get(endpoint, params=params)
    print(result.status_code)
    print(result.text)

    vim.current.buffer[:] = result.text.split('\n')
