#!/usr/bin/env bash
set -e  # 只要有一步出错就停下来，方便发现问题
set -u  # 用到未定义变量时报错

# 切换到脚本所在目录，确保无论从哪里调用都能正确工作
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --------- 0) 可选：全局只做一次的配置（已经配过可删除）---------
# git config --global user.name  "Your Name"
# git config --global user.email "you@example.com"

# --------- 1) 演示仓库准备 ----------------------------------------
rm -rf git-api-demo
mkdir  git-api-demo
cd     git-api-demo

# 初始化并把首分支固定为 main，这样后面 checkout main 一定存在
git init
git checkout -b main

# 本地(仅这个仓库)设置用户名邮箱，避免污染全局
git config user.name  "Demo User"
git config user.email "demo@example.com"


# --------- 2) 提交第一版内容 --------------------------------------
echo "# Git API Demo" > README.md
git add README.md
git commit -m "Initial commit: add README"

# --------- 3) 再加一个文件，作为基线 -------------------------------
echo "Line 1" > example.txt
git add example.txt
git commit -m "Add example.txt"

# --------- 4) 制造 **未暂存** 改动 (git_diff_unstaged) ------------
echo "Line 2 (unstaged)" >> example.txt

# --------- 5) 制造 **已暂存** 改动 (git_diff_staged) --------------
echo "## Subtitle" >> README.md
git add README.md   # 暂存区里只有 README.md

# --------- 6) 分支差异 (git_diff / git_show) ----------------------
git checkout -b feature
echo "Feature branch line" >> example.txt
git commit -am "feature: add line in example.txt"

git checkout main   # 回到 main，供后续 diff / show 使用
