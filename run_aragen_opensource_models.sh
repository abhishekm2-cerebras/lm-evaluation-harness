#!/bin/bash

export CUDA_VISIBLE_DEVICES="0,1"
export HF_HOME="/mnt/local/shared/riturajj/.cache/huggingface"
source /mnt/local/shared/abhishekm/venvs/ifeval-ar/bin/activate

# Array of HuggingFace models to evaluate
# You can modify this array to include the models you want to test
MODELS=(
    "Qwen/Qwen2.5-7B-Instruct"
    "Qwen/Qwen3-8B" 
    "meta-llama/Llama-3.1-8B-Instruct"
    "ALLaM-AI/ALLaM-7B-Instruct-preview"
    "FreedomIntelligence/AceGPT-v2-8B-Chat"
    "CohereLabs/aya-expanse-8b"
    "CohereLabs/c4ai-command-r7b-arabic-02-2025"
)

# Base output directory
BASE_OUTPUT_PATH="/mnt/local/shared/abhishekm/projects/lm-eval/results-v4"

# Function to extract model name from path for folder naming
get_model_name() {
    local model_path="$1"
    # Extract the last part of the path and clean it for folder naming
    basename "$model_path" | sed 's/[^a-zA-Z0-9_-]/_/g'
}

# Loop through each model and run evaluation
for MODEL in "${MODELS[@]}"; do
    echo "=========================================="
    echo "Starting evaluation for model: $MODEL"
    echo "=========================================="
    
    # Get a clean model name for the output folder
    MODEL_NAME=$(get_model_name "$MODEL")
    OUTPUT_DIR="${BASE_OUTPUT_PATH}/${MODEL_NAME}"
    
    # Create output directory if it doesn't exist
    mkdir -p "$OUTPUT_DIR"
    
    echo "Results will be saved to: $OUTPUT_DIR"
    
    # Run the evaluation
    PYTHONPATH=/mnt/local/shared/abhishekm/projects/lm-evaluation-harness python lm_eval/__main__.py --model vllm \
        --model_args pretrained="$MODEL",gpu_memory_utilization=0.95,tensor_parallel_size=2,dtype="bfloat16",trust_remote_code=True \
        --tasks aragen-inception-ar \
        --num_fewshot 0 \
        --batch_size auto \
        --output_path "$OUTPUT_DIR" \
        --apply_chat_template True \
        --log_samples
    
    # Check if the evaluation was successful
    if [ $? -eq 0 ]; then
        echo "✅ Evaluation completed successfully for $MODEL"
    else
        echo "❌ Evaluation failed for $MODEL"
    fi
    
    echo "Finished evaluation for: $MODEL"
    echo ""
done

echo "=========================================="
echo "All model evaluations completed!"
echo "=========================================="
