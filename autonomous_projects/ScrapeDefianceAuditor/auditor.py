import re
from typing import Iterable, List, Optional, Dict, Any
from collections import defaultdict

# Pre-compiled regex for Combined Log Format
# Example: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08"
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[.*?\]\s+"(?:\S+\s+)?(?P<path>\S+)(?:\s+\S+)?"\s+\d+\s+\S+\s+".*?"\s+"(?P<user_agent>.*?)"'
)

def parse_robots_rules(lines: Iterable[str]) -> List[re.Pattern]:
    """
    Parse robots.txt lines and compile Disallow directives into regex patterns.
    
    Args:
        lines: Iterable of strings representing lines from a robots.txt file.
        
    Returns:
        List of compiled regex patterns for disallowed paths.
    """
    rules: List[re.Pattern] = []
    for line in lines:
        line = line.strip()
        if line.lower().startswith('disallow:'):
            path = line.split(':', 1)[1].strip()
            if path:
                # Escape the path and anchor it to the start, allowing any suffix
                pattern_str = f"^{re.escape(path)}.*"
                try:
                    rules.append(re.compile(pattern_str))
                except re.error:
                    continue
    return rules

def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single Combined Log Format line.
    
    Args:
        line: A string representing a single log line.
        
    Returns:
        Dictionary with 'ip', 'path', and 'user_agent', or None if parsing fails.
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    
    return {
        'ip': match.group('ip'),
        'path': match.group('path'),
        'user_agent': match.group('user_agent')
    }

def audit_scrape_defiance(log_lines: Iterable[str], rules: List[re.Pattern]) -> Dict[str, Dict[str, Any]]:
    """
    Audit log lines against robots.txt rules using a single-pass state machine.
    
    Args:
        log_lines: Iterable of log line strings.
        rules: List of compiled regex patterns representing disallowed paths.
        
    Returns:
        Dictionary mapping IP addresses to their state, filtered to only 
        include IPs with at least one violation.
    """
    ip_states: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {'seen_robots': False, 'user_agent': None, 'violations': 0}
    )
    
    for line in log_lines:
        try:
            # Handle potential bytes if iterable yields them, though typed as str
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='ignore')
                
            parsed = parse_log_line(line)
            if not parsed:
                continue
                
            ip = parsed['ip']
            path = parsed['path']
            user_agent = parsed['user_agent']
            
            if path == '/robots.txt':
                ip_states[ip]['seen_robots'] = True
                ip_states[ip]['user_agent'] = user_agent
                
            for rule in rules:
                if rule.match(path):
                    ip_states[ip]['violations'] += 1
                    break  # Count one violation per log line even if multiple rules match
                    
        except Exception:
            # Gracefully skip malformed lines or decoding errors
            continue
            
    return {
        ip: state for ip, state in ip_states.items() 
        if state['violations'] > 0
    }