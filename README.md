# MCPVerse: An Expansive, Real-World Benchmark for Agentic Tool Use 


## Overview
MCPVerse is a comprehensive benchmark built on a large-scale set of executable, real-world tools. 

The evaluation system is build on top of [CAMEL](https://github.com/camel-ai/camel), thanks to their excellent work.

## Installation
1. Clone the repository
```bash
git clone 
cd mcpverse
```

2. using uv to install the dependencies
```bash
pip install uv
uv venv .venv --python=3.10
source .venv/bin/activate

uv pip install -e ".[all, dev]"
```

## Quick Start

### Setup API Keys

#### LLM API Keys
To provide your API keys,  edit `.env` to include your LLM API keys.
```bash
QWEN_API_BASE_URL="YOUR_API_KEY"
QWEN_API_KEY="YOUR_API_KEY"
ANTHROPIC_API_BASE_URL="YOUR_API_KEY"
ANTHROPIC_API_KEY="YOUR_API_KEY"
```

#### MCP Service API Keys
In the entire MCP Pool are under `mcpverse/tool_full.json`, some MCP services also require API Key registration. Below are the links to these APIs.
- [Amap-maps](https://lbs.amap.com/api/webservice/create-project-and-key)
- [alphavantage](https://www.alphavantage.co/)
- [rijksmuseum-server](https://data.rijksmuseum.nl/docs/api/)
- [nasa-mcp](https://api.nasa.gov/)
- [varflight](https://dataworks.variflight.com/blog/smarter-travel-with-ai--introducing-variflight-s-aviation-mcp-server)

After get your API keys, edit `.env` to include your API keys.
```bash
SMITHERY_API_KEY = "YOUR_API_KEY"
AMAP_API_KEY = "YOUR_API_KEY"
ALPHAVANTAGE_API_KEY = "YOUR_API_KEY"
RIJKSMUSEUM_API_KEY = "YOUR_API_KEY"
NASA_API_KEY = "YOUR_API_KEY"
VARFLIGHT_API_KEY = "YOUR_API_KEY"
```

### Run Evaluation

#### Debug Mode
To run a test evaluation on a debug mode, run
```bash
# Q: How many files in {MCPVerse_ROOT}/test_data/txt ? 
# Mounted MCP list:  ["filesystem", "fetch", "time"]
python runner.py --mode debug --model_name deepseek-v3
```

#### Running Benchmark
1. Get reference for time-sensetive tasks
```bash
python runner.py --mode get_ref --inout_path results/input_with_ref.csv
```

2. inference
```bash
python runner.py --mode infer --infer_mode standard --fc_mode FC --model_name deepseek-v3 --inout_path results/input_with_ref.csv
```


3. evaluate
```bash
python runner.py --mode eval --model_name deepseek-v3 --inout_path results/input_with_ref.csv
```


### Add New Model
add new model in `MCPAgentRunner::_init_model()` under `mcpverse/mcp_agent_runner.py` 
```python
self.model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type='Model_Name',
    url="Model_Endpoint"
    api_key='Your_Key'
)
```


### Change Score Model
The default score model is `GPT-4o-20241120`, you can change it by editing `mcpverse/judger.py`


