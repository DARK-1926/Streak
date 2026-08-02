import argparse
import json
import mmap
import os
import sys

import auditor


def main(log_path: str, robots_path: str) -> int:
    """
    Main entry point for the ScrapeDefianceAuditor CLI.
    
    Args:
        log_path: Path to the access log file.
        robots_path: Path to the robots.txt file.
        
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        # Win32 mmap guard: check file sizes before attempting to map
        if os.path.getsize(log_path) == 0:
            print(f"Error: Log file '{log_path}' is empty.", file=sys.stderr)
            return 1
            
        if os.path.getsize(robots_path) == 0:
            print(f"Error: Robots file '{robots_path}' is empty.", file=sys.stderr)
            return 1

        # Parse robots.txt rules
        with open(robots_path, 'r', encoding='utf-8') as f_robots:
            rules = auditor.parse_robots_rules(f_robots)

        # Process log file using mmap
        with open(log_path, 'rb') as f_log:
            with mmap.mmap(f_log.fileno(), 0, access=mmap.ACCESS_READ) as mmap_obj:
                log_lines = (
                    line.decode('utf-8', errors='ignore') 
                    for line in iter(mmap_obj.readline, b'')
                )
                results = auditor.audit_scrape_defiance(log_lines, rules)

        # Output results as formatted JSON
        print(json.dumps(results, indent=4))
        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Audit web server logs for robots.txt defiance."
    )
    parser.add_argument(
        "log_path",
        type=str,
        help="Path to the web server access log file."
    )
    parser.add_argument(
        "robots_path",
        type=str,
        help="Path to the robots.txt file."
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(args.log_path, args.robots_path))