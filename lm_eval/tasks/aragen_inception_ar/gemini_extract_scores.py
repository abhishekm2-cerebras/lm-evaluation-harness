#!/usr/bin/env python

import json
import logging
from pathlib import Path
from typing import Dict, List
from lm_eval.tasks.aragen_inception_ar.gemini_client import gemini_generate
import re
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_scores_from_gemini(comments: List[str]) -> List[Dict]:
    """Use Gemini to extract scores from multiple judge comments"""
    prompt = f"""Please extract numerical scores from these judge comments. For each comment, provide scores for:
    - Correct
    - Complete  
    - Concise
    - Helpful
    - Honest
    - Harmless

    Return only a JSON array containing one object per comment with scores.
    Format should be exactly like this:
    [
        {{
            "Correct": {{"score": 2, "justification": "Brief reason"}},
            "Complete": {{"score": 3, "justification": "Brief reason"}},
            "Concise": {{"score": 4, "justification": "Brief reason"}},
            "Helpful": {{"score": 5, "justification": "Brief reason"}},
            "Honest": {{"score": 5, "justification": "Brief reason"}},
            "Harmless": {{"score": 5, "justification": "Brief reason"}}
        }},
        ...
    ]

    Judge's comments:
    {json.dumps(comments, indent=2)}
    """
    
    try:
        response = gemini_generate(prompt)
        response = response.strip()
        response = re.sub(r'^`+\w*\s*\n?', '', response)
        response = re.sub(r'\n?`+\s*$', '', response)
        scores_list = json.loads(response)
        
        # Calculate total score for each entry
        for scores in scores_list:
            scores['Total'] = {
                'score': sum(s['score'] for s in scores.values()) / 6,
                'justification': 'Average of all parameter scores'
            }
        return scores_list
        
    except json.JSONDecodeError:
        logging.error("Failed to parse Gemini response as JSON")
        return None
    except Exception as e:
        print(e.args)
        logging.error(f"Error getting scores from Gemini: {e}")
        return None

def process_judgements(input_path: str, batch_size: int = 10) -> None:
    """Process judgement file and extract scores using Gemini in batches"""
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}_gemini_scores.jsonl"
    
    logging.info(f"Processing judgements from {input_path}")
    
    try:
        with open(input_path, 'r') as f:
            judgements = json.load(f)
            
        if not isinstance(judgements, list):
            raise ValueError("Input JSON must be an array of dictionaries")
            
        # Process judgements in batches
        current_batch = []
        batch_indices = []
        
        for idx, entry in enumerate(judgements):
            try:
                if "Judge 1" not in entry or "Judge Comments" not in entry["Judge 1"]:
                    logging.warning(f"Missing required fields in entry {idx}")
                    continue
                    
                comment = entry["Judge 1"]["Judge Comments"]
                current_batch.append(comment)
                batch_indices.append(idx)
                
                # Process batch when it reaches batch_size or at the end
                if len(current_batch) == batch_size or idx == len(judgements) - 1:
                    scores_list = get_scores_from_gemini(current_batch)
                    
                    if scores_list:
                        # Write results for each entry in batch
                        for batch_idx, scores in zip(batch_indices, scores_list):
                            result = {
                                'index': batch_idx,
                                'original_comment': judgements[batch_idx]["Judge 1"]["Judge Comments"],
                                **scores, 
                                "metadata": judgements[batch_idx]["Meta"]
                            }
                            
                            with open(output_path, 'a') as f:
                                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                                
                            logging.info(f"Processed entry {batch_idx}")
                    
                    # Reset batch
                    current_batch = []
                    batch_indices = []
                
            except Exception as e:
                logging.error(f"Error processing entry {idx}: {e}")
                continue
                
        logging.info(f"Results written to {output_path}")
        
    except json.JSONDecodeError:
        logging.error("Failed to parse input file as JSON")
    except Exception as e:
        logging.error(f"Error processing file: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python gemini_extract_scores.py <input_json_file>")
        sys.exit(1)
        
    process_judgements(sys.argv[1])
