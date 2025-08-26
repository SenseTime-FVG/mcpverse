# test_cases/Q101.py

import os

def run_test(pred, dir_path) -> bool:
    """
    Verifies that the directory `dir_path` exists and contains:
    - alpha.txt with content 'Hello Alpha'
    - beta.txt with content 'Hello Beta'
    Returns True if all checks pass, False otherwise.
    """
    alpha_path = os.path.join(dir_path, "alpha.txt")
    beta_path = os.path.join(dir_path, "beta.txt")

    # Check if directory exists
    if not os.path.isdir(dir_path):
        return False

    # Check if both files exist
    if not os.path.isfile(alpha_path) or not os.path.isfile(beta_path):
        return False

    # Read and verify content of alpha.txt
    with open(alpha_path, "r", encoding="utf-8") as f:
        alpha_content = f.read().strip()
    # Read and verify content of beta.txt
    with open(beta_path, "r", encoding="utf-8") as f:
        beta_content = f.read().strip()

    print(alpha_content, beta_content)
    return alpha_content == "Hello Alpha" and beta_content == "Hello Beta"
