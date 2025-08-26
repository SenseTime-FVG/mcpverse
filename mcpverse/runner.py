
import os
import json
import time
import pathlib
import argparse

from dotenv import load_dotenv
from datetime import datetime


from threading import Lock
import pandas as pd
import importlib
import asyncio

from concurrent.futures import ThreadPoolExecutor, as_completed


from camel.toolkits import CodeExecutionToolkit
from camel.logger import get_logger, set_log_level, set_log_file
from camel.toolkits import MCPToolkit

from judger import LLMJudger
from utils import read_data, write_data
from mcp_agent_runner import MCPAgentRunner


logger = get_logger(__name__)


class Evaluator:
    def __init__(self, args):
        self.args = args

        base_dir = pathlib.Path(__file__).parent.parent
        env_path = base_dir / ".env"
        load_dotenv(dotenv_path=str(env_path))

        self.setup()
        self.runner = MCPAgentRunner(args)
        self.judger = LLMJudger(args)

        self.df, self.logs = self.load_data()

        self.lock = Lock()
        self.parallel = args.parallel
        self.eval_mode = args.eval_mode

    def setup(self):
        self.model_name = args.model_name
        self.suffix = args.suffix
        self.infer_mode = args.infer_mode
        self.fc_mode = args.fc_mode

        self.workers = args.workers

        self.tool_path = args.tool_path
        time_str = datetime.today().strftime('%Y-%m-%d')
        # self.reference_path = f'tmp/Qlist-{time_str}.xlsx'
        self.inout_path = args.inout_path

        filename = self.inout_path.split('/')[-1]
        self.rollout_path = f"logs/{filename}.json"
        self.log_path = f"logs/{filename}.log"

        set_log_file(self.log_path)
        set_log_level(level="INFO")


    def load_data(self):
        if os.path.isfile(self.inout_path):
            logger.info(f"resume from {self.inout_path}")
            df = read_data(self.inout_path)
        else:
            df = read_data('data/mcpverse_benchmark.csv')

        base_name = os.path.basename(self.inout_path)
        outut_sub_folder = os.path.splitext(base_name)[0]

        df = df.applymap(lambda x: x.replace('{OUTPUT_SUB_FOLDER}', outut_sub_folder) if isinstance(x,  str) else x)


        if os.path.isfile(self.rollout_path):
            with open(self.rollout_path, 'r') as f:
                logs = json.load(f)
        else:
            logs = {}

        if f'{self.model_name}-answer' not in df.columns:
            df[f'{self.model_name}-answer'] = None

        if f'{self.model_name}-score' not in df.columns:
            df[f'{self.model_name}-score'] = None

        return df, logs



    def dump_results(self, stage, index, Qid, results):
        with self.lock:
            if stage == 'infer':
                self.df.loc[index, f'{self.model_name}-answer'] = results['answer']
                self.logs[Qid] = {'rollout': results['memory'], 'answer': results['answer']}
                write_data(self.inout_path, self.df)
                with open(self.rollout_path, 'w', encoding='utf-8') as json_file:
                    json.dump(self.logs, json_file, indent=4, ensure_ascii=False)

                logger.info(f"=> save results to {self.inout_path}")
                logger.info(f"=> save rollout to {self.rollout_path}")
                logger.info(f"=> save log to {self.log_path}")

            elif stage == 'eval':
                score = results['score']
                reason = results['reason']
                self.df.loc[index, f'{self.model_name}-score'] = score
                self.df.loc[index, f'{self.model_name}-reason'] = reason
                write_data(self.inout_path, self.df)
                # logger.info(f"=> save to {self.inout_path}")
            elif stage == 'get_ref':
                os.makedirs(os.path.dirname(self.inout_path), exist_ok=True)
                answer = results['answer']
                self.df.loc[index, 'answer'] = answer
                write_data(self.inout_path, self.df)


    async def predict_row(self, index, row, tools):
        if self.fc_mode == 'FC':
            agent = self.runner.build_agent(tools=tools)
        elif self.fc_mode == 'Prompt':
            agent = self.runner.build_mcp_prompt_agent(tools=tools)
        task = row['question']
        logger.info(f"=> {row['question_id']}: {task}")
        try:
            results = await self.runner.run_task(agent, task)
        except Exception as e:
            results = None
            logger.error(f"=> error, {e}")
        return results

    def _predict_with_tools(self, index, row, tools):
        agent = self.runner.build_agent(tools=tools)
        task = row['question']
        logger.info(f"=> {row['question_id']}: {task}")
        try:
            return self.runner.run_task_sync(agent, task)
        except Exception as e:
            logger.error(f"=> error during prediction: {e}")
            return None

    def predict_row_sync(self, index, row):
        Qid = row['question_id']
        task = row['question']
        logger.info(f"=> {Qid}: {task}")

        if '+' in row['MCP']:
            mcps = row['MCP'].split('+')
            mcp_list = [m.strip() for m in mcps]
        else:
            mcp_list = [row['MCP']]

        try: 
            tools = []

            if 'code' in mcp_list:
                logger.info("=> load tool: code")
                tools.extend(CodeExecutionToolkit(sandbox="subprocess", verbose=False).get_tools())

            non_code_mcps = [m for m in mcp_list if m != 'code']

            if not non_code_mcps:
                return index, self._predict_with_tools(index, row, tools)

            config = self.runner._load_mcp_config(non_code_mcps)
            with MCPToolkit(config_dict=config, timeout=20) as mcp_toolkit:
                tools.extend(mcp_toolkit.get_tools())
                return index, self._predict_with_tools(index, row, tools)
            
        except Exception as e:
            logger.error(f"=> error in predict_row_sync for {Qid}: {e}")
            return index, None
        

    def evaluate_row(self, index, row):
        eval_method = row.get('eval_method', 'llm_as_a_judge')
        pred = row[f'{self.model_name}-answer']
        answer = row['answer']
        Qid = row['question_id']
        question = row['question']
        score = None

        try:
            if eval_method == 'llm_as_a_judge':
                score, reason = self.judger.judge(question, pred, answer)

            elif eval_method == 'eval_script':
                reason = ""
                try:
                    logger.info(f"=> import eval_scripts.{Qid}")
                    module = importlib.import_module(f"eval_scripts.{Qid}")
                except ModuleNotFoundError as exc:
                    raise KeyError(f"Test case module '{Qid}' not found.")

                try:
                    passed: bool = module.run_test(pred, answer)
                    score = 1 if passed else 0
                except Exception as exc:
                    print(f"[TestCaseError] {exc}")
                    score = 0
                    
            return {
                'score': score,
                'reason': reason
            }

        except Exception as e:
            logger.error(f"=> error during evaluation: {e}")
            return None


    def get_reference_row(self, ref_id):
        answer = None
        for retry in range(3):  # Maximum 3 retries
            try:
                module = importlib.import_module(f"templates.{ref_id}")
                answer = module.get_reference()
                break
            except Exception as e:
                logger.warning(
                    f"=> get reference failed {ref_id} (attempt {retry+1}/3): {e}"
                )
                if retry < 2:  # Still has chances → wait 10 seconds and retry
                    time.sleep(10)
        return {'answer': answer}


    def get_references(self):
        for i, row in self.df.iterrows():
            if row['time-sensitive'] == 'No':
                continue
            Qid = row['question_id']
            ref_id = row["get_answer_id"]

            logger.info(f"=> get reference: {Qid}")

            try:
                results = self.get_reference_row(ref_id)

                if results is None:  # All three attempts failed, move to next row
                    continue
                
                logger.info(f"===> Done: {Qid}")
                self.dump_results('get_ref', i, Qid, results)

            except Exception as exc:
                logger.info(f"===> FAILED!! {Qid}: {ref_id}/{exc}")


    def get_target_tools(self):
        if self.infer_mode == 'maxscale':
            filtered = pd.Series([
                "amap-maps", "fetch", "mcp-deepwiki", "howtocook-mcp", "variflight", "time", "excel",  "memory", "sqlite", "airbnb", "alphavantage", "calculator", "dataset-viewer", "mindmap", "rijksmuseum-server", "nasa-mcp", "datagov", "simple-arxiv", "world_bank", "weather", "context7", "mcp-server-hotnews", "filesystem", "git", "puppeteer", "Office-PowerPoint-MCP-Server", "exa", "geeknews-mcp-server", "domain-search-server", "mcp-document-reader", "appinsightmcp", "poker_win_calculator", "mcp-paperswithcode", "mcp-visit-korea", "Bazi", "investor", "arxiv-mcp-server", "kospi-kosdaq", "whois", "weibo", "anilist", "berlin-transport", "yahoo-finance", "wuwa-mcp", "pixiv-mcp", "poke-mcp", "FinanceMCP", "bilibili", "opgg-mcp", "metmuseum-mcp", "12306-mcp", "famxplor", "ptcg-mcp", "opendota-mcp-server", "jinko-mcp", "youtube-download", "mcp-server-chinarailway", "mcp_weather_server", "bilibili-mcp-server", "fdp_basic", "macrostrat", "wikipedia", "3rd_party_mcp_server_shuidi"
            ])
        elif self.infer_mode == 'standard':
            filtered = pd.Series(['simple-arxiv', 'context7', 'world_bank', 'git', 'variflight', 'excel', 'dataset-viewer', 'macrostrat', 'kospi-kosdaq', 'wikipedia', 'nasa-mcp', 'howtocook-mcp', 'yahoo-finance', 'weather', 'amap-maps', 'fdp_basic', 'geeknews-mcp-server', 'filesystem', 'whois', 'appinsightmcp', 'sqlite', 'Bazi', 'mcp-paperswithcode', 'wuwa-mcp', 'datagov', 'bilibili', 'calculator', '12306-mcp', 'arxiv-mcp-server', 'weibo', 'poker_win_calculator', 'fetch', 'investor', '3rd_party_mcp_server_shuidi', 'time'])

        mcp_list = []
        for item in filtered.dropna():  
            parts = str(item).split('+')
            mcp_list.extend([p.strip() for p in parts if p.strip()]) 
        
        mcp_list = list(set(mcp_list))

        return mcp_list

    async def run_with_all_mcp(self):
        # connect mcp
        mcp_list = self.get_target_tools()
        tools = await self.runner.connect(mcp_list)
        failed_clients = self.runner.get_failed_tools()
        logger.info(f"=> failed clients: {failed_clients}")

        print(f"=> total tools: {len(tools)}")

        retry_count = 0
        # connect failed clients again
        while len(failed_clients) > 0 and retry_count < 3:
            logger.info(f"=> connect failed clients {retry_count}")
            failed_tools = await self.runner.connect(failed_clients)
            logger.info(f"=> failed clients after retry {retry_count}: {failed_clients}")

            tools.extend(failed_tools)
            failed_clients = self.runner.get_failed_tools()
            retry_count += 1


        logger.info(f"=> add tool: code excution")
        tools.extend(CodeExecutionToolkit(sandbox="subprocess", verbose=False).get_tools())

        # add code
        logger.info(f"=> total tools: {len(tools)}")
        logger.info(f"=> failed clients: {failed_clients}")


        try:
            # sequential process
            for index, row in self.df.iterrows():
                if row['eval_method'] == 'test_case':
                    continue
                
                if not pd.isnull(row[f'{self.model_name}-answer']):
                    logger.info(f"skip {row['question_id']}")
                    continue
    
                results = await self.predict_row(index, row, tools)
                if results is not None:
                    self.dump_results('infer', index, row['question_id'], results)
        finally:
            # disconnect
            await self.runner.disconnect()

    def skip_this_row(self, row):
        if '+' in row['MCP']:
            mcps = row['MCP'].split('+')
            mcp_list = [m.strip() for m in mcps]
        else:
            mcp_list = [row['MCP']]

        if not pd.isnull(row[f'{self.model_name}-answer']):
            return True
        
        if any(mcp in ['alphavantage', 'geeknews-mcp-server', 'claudedesktopcommander', 'biomcp', 'haiguitangmcp', 'google-maps', 'macrostrat', 'mcp_weather_server', 'bingcn'] for mcp in mcp_list):
            return True

        return False

    def run_with_oracle_mode_sync(self):
        for index, row in self.df.iterrows():
            Qid = row['question_id']
            logger.info(f"=> process: {Qid}")
            
            if Qid != 'Q171':
                continue

            if not pd.isnull(row[f'{self.model_name}-answer']):
                logger.info(f"skip {row['question_id']}")
                continue

            try:
                _, results = self.predict_row_sync(index, row)
                if results is not None:
                    self.dump_results('infer', index, Qid, results)
            except Exception as e:
                logger.error(f"=> error on {Qid}: {e}")

    async def run_sequential_with_target_mcp(self):
        # connect mcp        
        try:
            # sequential process
            for index, row in self.df.iterrows():
                Qid = row['question_id']
                logger.info(f"=> process: {Qid}")
                if not pd.isnull(row[f'{self.model_name}-answer']):
                    logger.info(f"skip {Qid}")
                    continue
                
                if int(Qid.split('Q')[-1]) < 177:
                    continue
                
                if '+' in row['MCP']:
                    mcps = row['MCP'].split('+')
                    mcp_list = [m.strip() for m in mcps]
                else:
                    mcp_list = [row['MCP']]

                tools = await self.runner.connect(mcp_list)
    
                results = await self.predict_row(index, row, tools)
                if results is not None:
                    self.dump_results('infer', index, results)
        finally:
            # disconnect
            try:
                await self.runner.disconnect()
            except Exception as e:
                logger.info(f"Disconnect failed {str(e)}")

    async def debug(self):
        # mcp_list_debug = ["filesystem", "fetch", "time"]
        mcp_list_debug = ["variflight", "amap-maps", "exa", "filesystem"]
        # mcp_list_debug = ['dataset-viewer', 'macrostrat', 'world_bank', 'simple-arxiv']
        
        tools = await self.runner.connect(mcp_list_debug)
        tools.extend(CodeExecutionToolkit(sandbox="subprocess", verbose=False).get_tools())

        MCPVerse_ROOT = os.getcwd()
        # print("current: ", MCPVerse_ROOT)

        row = {
            'question_id': "debug-000",
            'question': f"How many files in {MCPVerse_ROOT}/test_data/txt",
        }
        results = await self.predict_row(0, row, tools)
        # print(f"\033[94mAnswer: {results['answer']}\033[0m")

        await self.runner.disconnect()
            

    def eval_sequential(self):
        for index, row in self.df.iterrows():
            Qid = row['question_id']
            logger.info(f"=> process: {Qid}")

            if Qid != 'Q171':
                continue

            if not pd.isnull(row[f'{self.model_name}-score']):
                logger.info(f"skip {Qid}")
                continue
            
            results = self.evaluate_row(index, row)
            if results is not None:
                self.dump_results('eval', index, Qid, results)

    def eval_parallel(self):
        futures = {}
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            for index, row in self.df.iterrows():
                futures[executor.submit(self.evaluate_row, index, row)] = index
                

            for future in as_completed(futures):
                index = futures[future]
                try:
                    results = future.result()
                    if results is not None:
                        self.dump_results('eval', index, self.df.loc[index,'question_id'], results)
                except Exception as e:
                    logger.error(f"=> Unhandled error in worker thread: {e}")


    def eval(self):
        if self.eval_mode == 'parallel':
            self.eval_parallel()
        else:
            self.eval_sequential()
            


    def print_score(self):
        logger.info(f"=> score: {self.df['score'].mean()}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run selected MCP tools.")

    parser.add_argument('--mode',help='Running mode. Allowed options: debug, infer, eval', nargs='+', default=['all'], type=str, choices=['debug', 'get_ref', 'infer', 'eval', 'all'])
    parser.add_argument("--model_name", type=str, default="deepseek-v3")
    parser.add_argument("--tool_path", type=str, default="tool_full.json", help="MCP configuration file path.")
    parser.add_argument("--suffix", type=str, default="")
    parser.add_argument("--inout_path", type=str, default="")
    parser.add_argument("--infer_mode", type=str, default="oracle", help="Three mode: oracle, standard, maxscale")
    parser.add_argument("--fc_mode", type=str, default="FC")
    parser.add_argument("--judge_model", type=str, default="QwQ")
    parser.add_argument("--eval_mode", type=str, default="sequential")
    parser.add_argument("--tool_test", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--eval", action="store_true")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--workers", type=int, default=10)


    args = parser.parse_args()
    processer = Evaluator(args)

    # debug 
    if any(mode in ['debug'] for mode in args.mode):
        asyncio.run(processer.debug())

    # get reference stage
    if any(mode in ['all', 'get_ref'] for mode in args.mode):
        processer.get_references()

    # infer stage
    if any(mode in ['all', 'infer'] for mode in args.mode):
        if args.infer_mode == 'oracle':
            processer.run_with_oracle_mode_sync()
        elif args.infer_mode == 'standard' or args.infer_mode == 'maxscale':
            asyncio.run(processer.run_with_all_mcp())

    # eval stage
    if any(mode in ['all', 'eval'] for mode in args.mode):
        processer.eval()