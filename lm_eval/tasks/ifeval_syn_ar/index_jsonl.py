import json

def add_indices_to_jsonl(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for i, line in enumerate(f_in):
            data = json.loads(line)
            data['key'] = i
            f_out.write(json.dumps(data, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    input_file = '/mnt/local/shared/abhishekm/datasets/if-eval-arabic-synthetic/ifeval_gemini-2.0-flash-thinking-exp-01-21_shuffled.jsonl'
    output_file = '/mnt/local/shared/abhishekm/datasets/if-eval-arabic-synthetic/ifeval_gemini-2.0-flash-thinking-exp-01-21_shuffled_indexed.jsonl'
    add_indices_to_jsonl(input_file, output_file)
