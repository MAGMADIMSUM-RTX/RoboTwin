#!/bin/bash

# 如果还没有开启记录，则通过 script 命令启动，这样能伪装成 TTY 从而保留彩色输出
if [ -z "$SCRIPT_LOG" ]; then
    export SCRIPT_LOG=1
    # 生成带时间戳的日志文件名
    logfile="logs/eval_all_$(date +%Y%m%d_%H%M%S).log"
    # 使用数组安全地重建命令
    cmd=(bash "$0" "$@")
    # 转义参数以避免特殊字符问题
    printf -v cmd_str '%q ' "${cmd[@]}"
    # 启动 script，捕获输出并实时显示
    script -e -q /dev/null -c "$cmd_str" | tee /dev/stderr | sed -u -e $'s/\\r$//' -e $'s/.*\\r//' > "$logfile"
    # 返回 script 的退出码
    exit ${PIPESTATUS[0]}
fi

export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform

bash eval.sh turn_switch_left RoboTwin_aloha RoboTwin_aloha 100 0 0
bash eval.sh turn_switch_right RoboTwin_aloha RoboTwin_aloha 100 0 0
