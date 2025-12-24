import os
import re
import json


from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

from camel.logger import get_logger

logger = get_logger(__name__)


class LLMJudger:
    def __init__(self, args):
        self.args = args


    def build_judger(self):
        judge_sys_prompt = """
You are a grading assistant. Your task is to evaluate whether a model output and a reference answer are semantically consistent. Please note: the expressions do not need to be exactly the same — as long as the meanings are the same or equivalent, they should be considered consistent. Even if the model output and the reference answer are written in different languages, they should still be considered consistent as long as their meanings are the same or equivalent.

If they are consistent in meaning, output the score in the following JSON format, before you output the score, you should give your reason first.

```json
{
"score": 1
}
```

If they are not consistent in meaning, output:

```json
{
"score": 0
}

```
""".strip()
        if self.args.judge_model == 'GPT4o':
            model = ModelFactory.create(
                    model_platform=ModelPlatformType.AZURE,
                    model_type='gpt-4o-2024-11-20',
                    model_config_dict=dict(temperature=0.1, max_completion_tokens=4096),
            )
        elif self.args.judge_model == 'QwQ':
            model = ModelFactory.create(
                    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                    model_type='QwQ',
                    url=os.getenv("QwQ_API_BASE_URL"),
                    api_key=os.getenv("QwQ_API_KEY"),
                    model_config_dict=dict(temperature=0.1),
            )
        elif self.args.judge_model == 'Qwen25-72B':
            model = ModelFactory.create(
                    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                    model_type='Qwen25-72B',
                    url=os.getenv("QWEN25_72B_BASE_URL"),
                    api_key=os.getenv("QWEN25_72B_API_KEY"),
                    model_config_dict=dict(temperature=0.1),
            )



        agent = ChatAgent(system_message=judge_sys_prompt, model=model)
        return agent


    def extract_response(self, response):
        try:
            judgement = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if judgement:
                answer = judgement.group(1)
                content = json.loads(answer)
                score = content['score']
            else:
                score = ""
        except:
            score = ""

        return score


    def judge(self, question, pred, answer):
        prompt = f"""
the following is the question, model output and reference answer

<question>
{question}


<reference>
{answer}


<model output>
{pred}

now give your judgement
""".strip()
        
        agent = self.build_judger()
        response = agent.step(prompt)
        try:
            answer = response.msgs[0].content

            score = self.extract_response(answer)
            logger.info(f"score: {score}")
        except Exception as e:
            # score = str(e)
            logger.info(f"judge failed: {e}")

        return score, answer
