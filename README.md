# MCPVerse: An Expansive, Real-World Benchmark for Agentic Tool Use 

[![python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

[![arXiv](https://img.shields.io/badge/cs.AI-arXiv%3A2508.16260-B31B1B.svg?logo=arxiv&logoColor=red)](https://arxiv.org/abs/2508.16260)




## Overview
![MCPVerse Overview](assets/overview.png)
MCPVerse is a comprehensive benchmark built on a large-scale set of executable, real-world tools. With three evaluation modes, it tests LLMs from using a minimal, per-question toolset to mounting 550+ tools at once—approaching an OS-like environment. MCPVerse thus provides a realistic, execution-grounded benchmark of current LLM agentic capabilities.

The evaluation system is build on top of [CAMEL](https://github.com/camel-ai/camel), thanks to their excellent work.

## Leadboard
| Model               | Context Window | Max Tool Count | **Oracle Mode** SR | L1  | L2  | L3  | **Standard Mode** SR | L1  | L2  | L3  | **Max-Scale Mode** SR | L1  | L2  | L3  |
|----------------------|----------------|----------------|-------------------:|----:|----:|----:|---------------------:|----:|----:|----:|----------------------:|----:|----:|----:|
| **Claude-4-Sonnet**  | 200k           | —              | 62.3 | 71.6 | 62.7 | 52.5 | **62.4** | **75.9** | 60.4 | **50.9** | 44.2 | 45.8 | 40.5 | 46.2 |
| **GLM-4.5**          | 128k           | —              | 55.0 | 70.9 | 58.5 | 35.6 | **59.1** | 67.4 | **60.7** | 49.2 | — | — | — | — |
| **Qwen3-235B-2507**  | 1M             | —              | 44.8 | 62.5 | 44.8 | 27.1 | **53.2** | 63.9 | 51.8 | 43.9 | 31.6 | 44.3 | 23.7 | 26.7 |
| **DeepSeek-V3.1-Terminus** | 128k     | 128            | 56.6 | 64.4 | 57.3 | 48.3 | **52.1** | 62.0 | 49.4 | 45.0 | — | — | — | — |
| **DeepSeek-R1-0528** | 64k            | 128            | 56.4 | 70.5 | 56.4 | 42.4 | **49.9** | 65.1 | 47.4 | 37.3 | — | — | — | — |
| **Gemini-2.5-Pro**   | 1M             | 512            | 48.7 | 66.3 | 42.6 | 37.3 | **45.3** | 62.4 | 41.9 | 31.6 | 31.4* | 37.7* | 35.7* | 20.8* |
| **DeepSeek-V3-0324** | 64k            | 128            | 46.8 | 62.7 | 45.1 | 32.7 | **32.2** | 47.0 | 27.7 | 22.0 | — | — | — | — |
| **Qwen3-235B-A22B**  | 128k           | —              | 42.1 | 61.6 | 34.8 | 30.0 | **37.7** | 52.3 | 35.9 | 25.0 | — | — | — | — |
| **GPT-4o-20241120**  | 128k           | 128            | 42.1 | 59.1 | 40.2 | 27.1 | **31.4*** | 37.7* | 35.7* | 20.8* | — | — | — | — |
| **GPT-5**            | 400k           | —              | **68.1** | **80.5** | **67.8** | **55.9** | **23.4*** | 30.6* | 19.7* | 20.0* | — | — | — | — |
| **Qwen3-30B-A3B**    | 128k           | —              | 27.7 | 46.5 | 18.1 | 18.3 | **18.9** | 27.9 | 12.9 | 15.8 | — | — | — | — |
| **Kimi-K2-0711**     | 128k           | 128            | 59.4 | 70.9 | 59.8 | 47.5 | **16.3*** | 24.4* | 24.4* | 0.0* | — | — | — | — |


*Notes:* Context = max context length; Tools = native tool limit. Dashes (–) mean not evaluated for that mode. Scores with `*` used prompt-based function calling instead of native tools due to context limits. Bold numbers are column bests.




## Installation
1. Clone the repository
```bash
git clone https://github.com/hailsham/mcpverse
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

#### MCP Service API Keys (Required)
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


#### LLM API Keys
To provide your API keys,  edit `.env` to include your LLM API keys.
```bash
QWEN_API_BASE_URL="YOUR_API_KEY"
QWEN_API_KEY="YOUR_API_KEY"
ANTHROPIC_API_BASE_URL="YOUR_API_KEY"
ANTHROPIC_API_KEY="YOUR_API_KEY"
```




### Run Evaluation

#### Debug Mode
To run a test evaluation on a debug mode, run
```bash
cd mcpverse
# Q: How many files in {MCPVerse_ROOT}/test_data/txt ? 
# Mounted MCP list:  ["filesystem", "fetch", "time"]
python runner.py --mode debug --model_name deepseek-v3
```

#### Running Benchmark
1. prepare test_data
    ```bash
    cd test_data
    chmod +x generate_repo.sh
    ./generate_repo.sh
    ```


2. Get reference for time-sensetive tasks
    ```bash
    python runner.py --mode get_ref --inout_path results/input_with_ref.csv
    ```

3. inference
    run **oracle** mode using FC
    ```bash
    python runner.py --mode infer --infer_mode oracle --fc_mode FC --model_name deepseek-v3 --inout_path results/input_with_ref.csv
    ```


    run **stanrdard** mode using FC
    ```bash
    python runner.py --mode infer --infer_mode standard --fc_mode FC --model_name deepseek-v3 --inout_path results/input_with_ref.csv
    ```

    run **standard** mode using Prompt
    ```bash
    python runner.py --mode infer --infer_mode standard --fc_mode Prompt --model_name deepseek-v3 --inout_path results/input_with_ref.csv
    ```


4. evaluate
    setup judge model at `judger.py` and run
    ```bash
    python runner.py --mode eval --model_name deepseek-v3 --inout_path results/input_with_ref.csv --judege_model GPT4o
    ```

5. calculate score
    ```bash
    python stats.py -i results/gpt5_input_with_ref_oracle.csv
    ```


Tips:
1. Both inference and evaluation stages can **automatically resume** from inout file.
2. The chat history during inference will be saved in the `logs` folder.
3. The model's intermediate output files will be saved in the `outputs` folder.


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


## Citation
If you find this work useful, please cite our paper:
```bibtex
@misc{lei2025mcpverse,
    title={MCPVerse: An Expansive, Real-World Benchmark for Agentic Tool Use}, 
    author={Fei Lei and Yibo Yang and Wenxiu Sun and Dahua Lin},
    year={2025},
    eprint={2508.16260},
    archivePrefix={arXiv},
    primaryClass={cs.AI},
    url={https://arxiv.org/abs/2508.16260}, 
}
```