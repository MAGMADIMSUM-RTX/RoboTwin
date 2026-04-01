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

# 强制关闭 SSL 验证
export CURL_CA_BUNDLE=""
export REQUESTS_CA_BUNDLE=""
export HF_HUB_DISABLE_SSL_VERIFICATION=1

# 强烈建议：同时使用国内镜像站，既防拦截又提速
# export HF_ENDPOINT=https://hf-mirror.com

# bash eval.sh open_laptop_right RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50
# bash eval.sh open_laptop_left RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50

echo "======================="
echo "20 task start"
echo "======================="


# bash eval.sh place_phone_stand_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50
# bash eval.sh place_phone_stand_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50

# bash eval.sh move_pillbottle_pad_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
# bash eval.sh move_pillbottle_pad_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 

# bash eval.sh place_container_plate_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50
# bash eval.sh place_container_plate_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50

# bash eval.sh adjust_bottle_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
# bash eval.sh adjust_bottle_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 

# bash eval.sh open_laptop_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50
# bash eval.sh open_laptop_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50


# bash eval.sh click_alarmclock_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
# bash eval.sh click_alarmclock_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 

# bash eval.sh rotate_qrcode_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50
# bash eval.sh rotate_qrcode_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50

# bash eval.sh stamp_seal_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
# bash eval.sh stamp_seal_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 

# bash eval.sh turn_switch_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
# bash eval.sh turn_switch_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 

bash eval.sh place_can_basket_right RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 
bash eval.sh place_can_basket_left RoboTwin_aloha pi0_aloha_20_tasks_fast_delta_lora RoboTwin_aloha 0 0 50 



echo "======================="
echo "new 8 task start"
echo "======================="


bash eval.sh place_phone_stand_right RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50
bash eval.sh place_phone_stand_left RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50

bash eval.sh move_pillbottle_pad_right RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50 
bash eval.sh move_pillbottle_pad_left RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50 

bash eval.sh place_container_plate_right RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50
bash eval.sh place_container_plate_left RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50

bash eval.sh adjust_bottle_right RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50 
bash eval.sh adjust_bottle_left RoboTwin_aloha pi0_aloha_8_tasks_fast_delta_lora_3.30 RoboTwin_aloha 0 0 50 


echo "======================="
echo "old 8 task start"
echo "======================="


bash eval.sh place_phone_stand_right RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50
bash eval.sh place_phone_stand_left RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50

bash eval.sh move_pillbottle_pad_right RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50 
bash eval.sh move_pillbottle_pad_left RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50 

bash eval.sh place_container_plate_right RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50
bash eval.sh place_container_plate_left RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50

bash eval.sh adjust_bottle_right RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50 
bash eval.sh adjust_bottle_left RoboTwin_aloha pi0_aloha_8_tasks_fast_lora RoboTwin_aloha 0 0 50 

