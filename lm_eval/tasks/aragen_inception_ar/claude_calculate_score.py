import json

def calculate_aragen_scores(file_path):
    # Metrics we want to average
    score_keys = ["Complete", "Concise", "Correct", "Harmless", "Helpful", "Honest",  "Total"]

    # Initialize accumulators for each metric
    totals = {key: 0 for key in score_keys}
    count = 0

    # Read the JSONL file line by line
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            count += 1

            # Sum up scores for all defined keys
            for key in score_keys:
                totals[key] += data.get(key, {}).get("score", 0)

    if count == 0:
        raise ValueError("No valid records found in the file.")

    # Calculate average per metric
    averages = {key: totals[key] / count for key in score_keys}

    # Final Aragen score = average of all metric averages
    final_score = sum(averages.values()) / len(score_keys)

    # Print results
    print("\n===== Aragen Score Report =====")
    print(f"Total Samples: {count}\n")
    for key, avg in averages.items():
        print(f"{key:10s} → {avg:.4f}")
    print("\nFinal Aragen Score:", round(final_score, 4))
    print("================================\n")

    return averages, final_score

# Example usage
file_path = "/lustre/scratch/users/sarath.chandran/llm-evals/results/8B/251204_8b_dpo_v0p5_excl_poetry_corruption_data_v1_bs160_beta0p1_lr_4e-5_351_RL_bs512_V2/group15/__lustre__scratch__users__sarath.chandran__llm-evals__checkpoints__8B__251204_8b_dpo_v0p5_excl_poetry_corruption_data_v1_bs160_beta0p1_lr_4e-5_351_RL_bs512_V2/samples_aragen-inception-ar_2025-12-12T11-47-32.307519.jsonl"  # Replace with your JSONL path
calculate_aragen_scores(file_path)
