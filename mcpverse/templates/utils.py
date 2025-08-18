
import pandas as pd
import json
from camel.utils.mcp_client import MCPClient
from camel.toolkits.mcp_toolkit import MCPToolkit

async def get_node_res(node):
    # breakpoint()
    mcp = node[0]['mcp']
    tool = node[0]['tool']
    args = node[0]['args']
    with open('tool_full.json', "r", encoding="utf-8") as f:
        config = json.load(f)
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