import json
from typing import Iterable, Dict, Any

GPL_SIGNATURES = [
    'GNU GENERAL PUBLIC LICENSE',
    'GPLV2',
    'GPLV3',
    'THIS PROGRAM IS FREE SOFTWARE'
]

def scan_stream(lines: Iterable[str]) -> Dict[str, Any]:
    """
    Scans an iterable of JSONL strings for GPL license signatures.
    
    Performs a single-pass O(N) scan over the provided lines, parsing each
    as JSON and checking the 'generated_code' field for copyleft signatures.
    
    Args:
        lines: An iterable of strings, where each string is a JSON object.
        
    Returns:
        A dictionary containing the scan state:
        - total_lines_processed: Total number of lines iterated.
        - valid_generations: Number of lines with valid JSON and 'generated_code'.
        - infected_generations: Number of valid generations containing a GPL signature.
        - signature_counts: A dictionary mapping found signatures to their frequency.
    """
    state: Dict[str, Any] = {
        'total_lines_processed': 0,
        'valid_generations': 0,
        'infected_generations': 0,
        'signature_counts': {}
    }
    
    for line in lines:
        state['total_lines_processed'] += 1
        
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
            
        try:
            code = data['generated_code']
        except (KeyError, TypeError):
            continue
            
        state['valid_generations'] += 1
        
        if not isinstance(code, str):
            code = str(code)
            
        code_upper = code.upper()
        is_infected = False
        
        for sig in GPL_SIGNATURES:
            if sig in code_upper:
                state['signature_counts'][sig] = state['signature_counts'].get(sig, 0) + 1
                is_infected = True
                
        if is_infected:
            state['infected_generations'] += 1
            
    return state