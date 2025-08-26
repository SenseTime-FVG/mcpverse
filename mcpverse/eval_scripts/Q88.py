# test_cases/Q102.py

import os

def run_test(pred, file_path) -> bool:
    """
    Verifies Q88: that the file './outputs/{outut_sub_folder}/a.txt' exists and contains:
    - The exact content: 'this is a sample text'
    Returns True if the check passes, False otherwise.
    """

    # Check if file exists
    if not os.path.isfile(file_path):
        return False

    # Read and verify content of a.txt
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if content == "this is a sample text":
        return 1
    else:
        return 0
