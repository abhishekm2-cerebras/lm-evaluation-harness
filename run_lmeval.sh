#!/bin/bash

export CUDA_VISIBLE_DEVICES="0,1"

source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate

# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/11c_sft,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks ifeval-syn-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results/ifeval-syn-ar_0_shot/11c_sft.json \
#     --apply_chat_template True


PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
    --model_args pretrained=/mnt/local/shared/abhishekm/hf_ckpts/sft-11b-c5120,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
    --tasks ifeval-syn-ar \
    --num_fewshot 0 \
    --batch_size auto \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results/ifeval-syn-ar_0_shot/11b_sft.json \
    --apply_chat_template True