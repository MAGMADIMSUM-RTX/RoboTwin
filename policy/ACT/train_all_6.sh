#!/bin/bash

if [ -z "$SCRIPT_LOG" ]; then
    export SCRIPT_LOG=1
    # 生成带时间戳的日志文件名
    logfile="logs/train_all_6$(date +%Y%m%d_%H%M%S).log"
    # 使用数组安全地重建命令
    cmd=(bash "$0" "$@")
    # 转义参数以避免特殊字符问题
    printf -v cmd_str '%q ' "${cmd[@]}"
    # 启动 script，捕获输出并实时显示
    script -e -q /dev/null -c "$cmd_str" | tee /dev/stderr | sed -u -e $'s/\\r$//' -e $'s/.*\\r//' > "$logfile"
    # 返回 script 的退出码
    exit ${PIPESTATUS[0]}
fi
# 以下是脚本的正常内容...


bash process_data.sh move_pillbottle_pad_right RoboTwin_aloha 100
bash train.sh move_pillbottle_pad_right RoboTwin_aloha 100 0 5


sleep 1

bash process_data.sh place_phone_stand_right RoboTwin_aloha 100
bash train.sh place_phone_stand_right RoboTwin_aloha 100 0 5

