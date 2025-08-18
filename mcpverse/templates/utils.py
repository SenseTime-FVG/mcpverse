
import pandas as pd
import json
from camel.utils.mcp_client import MCPClient
from camel.toolkits.mcp_toolkit import MCPToolkit
import os

async def get_node_res(node):
    # breakpoint()
    mcp = node[0]['mcp']
    tool = node[0]['tool']
    args = node[0]['args']

    with open('tool_full.json', "r", encoding="utf-8") as f:
        raw = f.read()

    # raw = raw.replace("${MCPVERSE_ROOT}", os.environ["MCPVERSE_ROOT"])
    raw = raw.replace("${SMITHERY_API_KEY}", os.environ["SMITHERY_API_KEY"])
    raw = raw.replace("${AMAP_API_KEY}", os.environ["AMAP_API_KEY"])
    raw = raw.replace("${ALPHAVANTAGE_API_KEY}", os.environ["ALPHAVANTAGE_API_KEY"])
    raw = raw.replace("${RIJKSMUSEUM_API_KEY}", os.environ["RIJKSMUSEUM_API_KEY"])
    raw = raw.replace("${NASA_API_KEY}", os.environ["NASA_API_KEY"])
    raw = raw.replace("${VARFLIGHT_API_KEY}", os.environ["VARFLIGHT_API_KEY"])

    config = json.loads(raw)

    meta_mcp_servers = config.get("mcpServers", {})
    mcp_servers = meta_mcp_servers[mcp]

    async with MCPClient(mcp_servers) as client:
        # tools = client.get_tools()
        results = await client.call_tool(tool, args)
        results = results.content[0].text

    output = {node[0]['id']: results}
    return output    



async def get_node_res_toolkit(node):
    # breakpoint()
    mcp = node[0]['mcp']
    tool = node[0]['tool']
    args = node[0]['args']
    with open('tool.json', "r", encoding="utf-8") as f:
        config = json.load(f)
    meta_mcp_servers = config.get("mcpServers", {})
    mcp_servers = {name: meta_mcp_servers[name] for name in [mcp]}

    async with MCPToolkit(config_dict={"mcpServers": mcp_servers}, timeout=30) as mcp_toolkit:
        results = await mcp_toolkit.call_tool(tool, args)
        results = results.content[0].text
    
    output = {node[0]['id']: results}
    
    return output    