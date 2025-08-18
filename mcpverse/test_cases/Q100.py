# test_cases/case_001_config.py
"""
检查 config.txt 是否包含:
version=1.0
status=complete
"""

import os

FILE_PATH = "hello/config.txt"
EXPECTED_CONTENT = "version=1.0\nstatus=complete"

def run_test(pred, answer) -> bool:
    """
    任何 test-case 都应保持统一签名:
        pred   : 来自模型/流程的输出（可选用）
        answer : 参考答案（可选用）
    返回:
        True  -> 通过
        False -> 未通过
    """
    if not os.path.exists(FILE_PATH):
        return False

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()

    print(content)
    print(EXPECTED_CONTENT)

    return content == EXPECTED_CONTENT
