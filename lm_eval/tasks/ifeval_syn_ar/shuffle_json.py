import json
import random
import argparse
from pathlib import Path

def shuffle_jsonl(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Read all records from the input file
    with input_path.open("r", encoding="utf-8") as fp:
        records = [json.loads(line) for line in fp if line.strip()]

    # Shuffle records
    random.shuffle(records)

    # Write to output file with Arabic-safe encoding
    with output_path.open("w", encoding="utf-8") as fp:
        for r in records:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Shuffled {len(records)} records and saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shuffle rows in a JSONL file with proper Unicode handling.")
    parser.add_argument("input", help="Input JSONL file path")
    parser.add_argument("output", help="Output JSONL file path")

    args = parser.parse_args()
    shuffle_jsonl(args.input, args.output)