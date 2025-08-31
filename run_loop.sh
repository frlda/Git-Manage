#!/bin/bash

# 日志文件夹和日志文件名
LOG_DIR="log"
LOG_FILE_NAME="run_$(date +%Y-%m-%d).log"
LOG_PATH="${LOG_DIR}/${LOG_FILE_NAME}"

# 确保日志文件夹存在
mkdir -p "$LOG_DIR"

while true
do
    # 运行 Python 脚本，同时将输出重定向到文件和命令行
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Hoshino Starting..." | tee -a "$LOG_PATH"
    python run.py 2>&1 | tee -a "$LOG_PATH"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - The Python script exited. Restarting in 3 seconds (press Ctrl + C to cancel)." | tee -a "$LOG_PATH"
    sleep 3
done