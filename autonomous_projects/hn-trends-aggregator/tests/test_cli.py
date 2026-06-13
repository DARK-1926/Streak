import subprocess, sys, json, os

def test_cli_success():
    # Run the CLI script and capture output
    result = subprocess.run([sys.executable, '-m', 'hn_trends_aggregator.cli'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    # basic sanity check on first item if present
    if data:
        first = data[0]
        for key in ["title", "url", "author", "points", "comments"]:
            assert key in first
