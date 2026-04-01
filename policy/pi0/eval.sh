#!/bin/bash

export PYTHONFAULTHANDLER=1

# 2. 显存隔离：让 JAX 预先安全地划走 30% 显存，剩下的留给 PyTorch 和环境
export XLA_PYTHON_CLIENT_MEM_FRACTION=0.3
export XLA_PYTHON_CLIENT_ALLOCATOR=platform

# 3. 绕过 ptxas 编译器崩溃：关闭 XLA 的 GPU 自动调优
export XLA_FLAGS="--xla_gpu_autotune_level=0"

policy_name=pi0
task_name=${1}
task_config=${2}
train_config_name=${3}
model_name=${4}
seed=${5}
gpu_id=${6}
test_num=${7:-100}

echo "Start Time: $(date)"

export CUDA_VISIBLE_DEVICES=${gpu_id}
echo -e "\033[33mgpu id (to use): ${gpu_id}\033[0m"

source .venv/bin/activate
cd ../.. # move to root

PYTHONWARNINGS=ignore::UserWarning \
python script/eval_policy.py --config policy/$policy_name/deploy_policy.yml \
    --overrides \
    --task_name ${task_name} \
    --task_config ${task_config} \
    --train_config_name ${train_config_name} \
    --model_name ${model_name} \
    --ckpt_setting ${model_name} \
    --seed ${seed} \
    --policy_name ${policy_name} \
    --test_num ${test_num}
