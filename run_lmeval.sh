#!/bin/bash

export CUDA_VISIBLE_DEVICES="2,3"
source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate
export GEMINI_KEY_FILE="/mnt/local/shared/abhishekm/projects/gemini_keys.txt"

#  ifeval-syn-ar,ifeval-inception-ar,aragen-inception-ar,ifeval_arabic_inception_hf 

PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
    --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp3_2epoch,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
    --tasks ifeval_arabic_inception_hf \
    --num_fewshot 0 \
    --batch_size auto \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-temp/8b_new_ift_exp3_2epoch/ \
    --apply_chat_template True \
    --log_samples 


# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/abhishekm/hf_ckpts/sft-11b-c5120,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks ifeval-syn-ar,ifeval-inception-ar,aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v3/11b/ \
#     --apply_chat_template True \
#     --log_samples





# Tasks 
# 1. ifeval-inception-ar
# 2. aragen-inception-ar
# 3. ifeval-syn-ar