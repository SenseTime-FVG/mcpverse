# test_cases/case_001_config.py
"""
检查 config.txt 是否包含:
version=1.0
status=complete
"""

import os

# FILE_PATH = "hello/config.txt"
EXPECTED_CONTENT = "version=1.0\nstatus=complete"

def run_test(pred, file_path) -> bool:
    """
    """
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    print(content)
    print(EXPECTED_CONTENT)

    return content == EXPECTED_CONTENT
