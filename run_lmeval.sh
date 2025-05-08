#!/bin/bash

export CUDA_VISIBLE_DEVICES="0"

source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate

PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model hf \
    --model_args pretrained=/mnt/local/shared/riturajj/ckpts/11c_sft,dtype="bfloat16",parallelize=True,trust_remote_code=True \
    --tasks ifeval-syn-ar \
    --num_fewshot 0 \
    --batch_size 64 \
    --output_path /mnt/local/shared/abhishekm/projects/lm-eval/results/ifeval-syn-ar_0_shot/11c_sft.json \
    --apply_chat_template True