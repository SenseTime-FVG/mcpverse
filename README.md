# MCPVerse: An Expansive, Real-World Benchmark for Agentic Tool Use 

[![python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

[![arXiv](https://img.shields.io/badge/cs.AI-arXiv%3A2508.16260-B31B1B.svg?logo=arxiv&logoColor=red)](https://arxiv.org/abs/2508.16260)


## Updates
### 2025.12.22

Some MCP servers in our original tool pool have been deprecated or taken offline, which makes a subset of questions in the original dataset no longer executable/reproducible. To address this, we release an updated version of the dataset. Please refer to `mcpverse/data/mcpverse_time_invariant_v1.1.csv`. Note that this version only includes **time-invariant** questions.


## Overview
![MCPVerse Overview](assets/overview.png)
MCPVerse is a comprehensive benchmark built on a large-scale set of executable, real-world tools. With three evaluation modes, it tests LLMs from using a minimal, per-question toolset to mounting 550+ tools at once—approaching an OS-like environment. MCPVerse thus provides a realistic, execution-grounded benchmark of current LLM agentic capabilities.

The evaluation system is build on top of [CAMEL](https://github.com/camel-ai/camel), thanks to their excellent work.

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

#### Preparation

1. Prepare test data
    ```bash
    cd test_data
    chmod +x generate_repo.sh
    ./generate_repo.sh
    ```

2. Get reference answers for time-sensitive tasks
    ```bash
    python runner.py --mode get_ref --inout_path results/input_with_ref.csv
    ```

#### Running

3. Quick test (debug mode)
    ```bash
    python runner.py --mode debug --model_name deepseek-v3.2 
    ```

4. Inference
    
    Run **Oracle** mode with Function Calling (FC):
    ```bash
    python runner.py --mode infer \
        --infer_mode oracle --fc_mode FC \
        --model_name deepseek-v3.2 \
        --dataset_path data/mcpverse_time_invariant_v1.1.csv \
        --inout_path results/deepseek_oracle.csv
    ```

    Run **Standard** mode with FC by changing `--infer_mode` to `standard`:
    ```bash
    --infer_mode standard
    ```

    Run **Standard** mode with Prompt-based tool use by changing `--fc_mode` to `Prompt`:
    ```bash
    --fc_mode Prompt
    ```

5. Evaluate
    
    Configure the judge model in `judger.py`, then run:
    ```bash
    python runner.py --mode eval \
        --model_name deepseek-v3.2 \
        --inout_path results/deepseek_oracle.csv \ 
        --judge_model GPT4o
    ```

6. Calculate scores
    ```bash
    python stats.py -i results/gpt5_input_with_ref_oracle.csv
    ```


**Tips:**
1. Both inference and evaluation stages support **automatic resumption** from the inout file.
2. Chat histories during inference are saved in the `logs/` directory.
3. Intermediate model outputs are saved in the `outputs/` directory.


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