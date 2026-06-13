import json
import sys
from .fetch import fetch_trends
from .parse import extract_trends

def main(argv=None):
    argv = argv or sys.argv[1:]
    try:
        raw = fetch_trends()
        trends = extract_trends(raw)
        json.dump(trends, sys.stdout, ensure_ascii=False, indent=2)
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
