#!/bin/bash

export CUDA_VISIBLE_DEVICES="3"

source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate
export GEMINI_KEY_FILE="/mnt/local/shared/abhishekm/projects/gemini_keys.txt"

# Run3 2nd epoch
# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp3_2epoch,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_run3_2epoch-temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples

# # Run2 2nd epoch 
# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp2_2epoch,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_run2_2epoch-temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples

# # Run1 2nd epoch
# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp1,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_run1_2epoch-temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples



# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/11c_sft,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/11c-temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples

# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/abhishekm/hf_ckpts/sft-11b-c5120,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/11b-temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples


# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp4_3epoch,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_new_ift_exp4_3epoch_temp=0/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=0,top_p=0.5 \
#     --log_samples

# PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
#     --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp4_3epoch,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
#     --tasks aragen-inception-ar \
#     --num_fewshot 0 \
#     --batch_size auto \
#     --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_new_ift_exp4_3epoch_temp=1/ \
#     --apply_chat_template True \
#     --gen_kwargs temperature=1,top_p=0.5 \
#     --log_samples


PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
    --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp5_3epoch,gpu_memory_utilization=0.95,tensor_parallel_size=1,dtype="bfloat16",trust_remote_code=True \
    --tasks aragen-inception-ar \
    --num_fewshot 0 \
    --batch_size auto \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_new_ift_exp5_3epoch_temp=0/ \
    --apply_chat_template True \
    --gen_kwargs temperature=0,top_p=0.5 \
    --log_samples

PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
    --model_args pretrained=/mnt/local/shared/riturajj/ckpts/8b_new_ift_exp5_3epoch,gpu_memory_utilization=0.95,tensor_parallel_size=1,dtype="bfloat16",trust_remote_code=True \
    --tasks aragen-inception-ar \
    --num_fewshot 0 \
    --batch_size auto \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v4/8b_new_ift_exp5_3epoch_temp=1/ \
    --apply_chat_template True \
    --gen_kwargs temperature=1,top_p=0.5 \
    --log_samples



# Tasks 
# 1. ifeval-inception-ar
# 2. aragen-inception-ar
# 3. ifeval-syn-ar
