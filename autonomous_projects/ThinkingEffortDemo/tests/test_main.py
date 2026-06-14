import subprocess, sys, os

def run_cli(prompt, effort):
    cmd = [sys.executable, os.path.join('src','main.py'), '--prompt', prompt, '--effort', effort]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def test_low_effort():
    out = run_cli("Hello", "low")
    assert "(low)" in out
    assert "Response to: Hello (effort=low)" in out

def test_medium_effort():
    out = run_cli("Hello", "medium")
    assert "(medium)" in out
    assert "Response to: Hello (effort=medium)" in out

if __name__ == "__main__":
    test_low_effort()
    test_medium_effort()
    print("All tests passed")
