#!/bin/bash

if [ -z "$SCRIPT_LOG" ]; then
    export SCRIPT_LOG=1
    # 生成带时间戳的日志文件名
    logfile="logs/collect_data_$(date +%Y%m%d_%H%M%S).log"
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

task_config=RoboTwin_aloha
episode_nums=100

./script/.update_path.sh > /dev/null 2>&1

export CUDA_VISIBLE_DEVICES=0


task_name=adjust_bottle_left
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=adjust_bottle_right
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=move_pillbottle_pad_left
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=move_pillbottle_pad_right
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=open_laptop_left
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=open_laptop_right
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=place_container_plate_left
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=place_container_plate_right
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=place_phone_stand_left
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5

task_name=place_phone_stand_right
cd /home/huahungy/RoboTwin/
PYTHONWARNINGS=ignore::UserWarning \
python script/collect_data.py ${task_name} ${task_config}
rm -rf data/${task_name}/${task_config}/.cache
cd /home/huahungy/RoboTwin/policy/pi0
bash process_data_pi0.sh ${task_name} ${task_config} ${episode_nums}
mv processed_data/${task_name}-${task_config}-${episode_nums} processed_data/${task_name}_source_h5
