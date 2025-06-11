#!/bin/bash

export CUDA_VISIBLE_DEVICES="0,1"

source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate
export GEMINI_KEY_FILE="/mnt/local/shared/abhishekm/projects/gemini_keys.txt"

PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
    --model_args pretrained=/mnt/local/shared/ahmedf/checkpoints/AR1-ar-exp12ct-c240,gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
    --tasks arabic_gsm8k \
    --num_fewshot 0 \
    --batch_size auto \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results-v3/AR1-ar-exp12ct-c240/ \
    --apply_chat_template True \
    --log_samples \
    --gen_kwargs "max_gen_toks=65536,max_tokens_thinking=auto,thinking_n_ignore=2,thinking_n_ignore_str=Wait,thinking_start=<|begin_of_thought|>,thinking_end=<|end_of_thought|>,until_thinking=<|begin_of_solution|>,until_thinking_2=<|end_of_thought|>"





# Tasks 
# 1. ifeval-inception-ar
# 2. aragen-inception-ar
# 3. ifeval-syn-ar