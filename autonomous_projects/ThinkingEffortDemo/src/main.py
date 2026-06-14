import argparse
import time

# Simulated LLM response generator

def generate_response(prompt, effort):
    # Map effort levels to simulated computation time
    effort_map = {
        "low": 0.5,
        "medium": 1.0,
        "high": 2.0,
        "xhigh": 3.0
    }
    delay = effort_map.get(effort, 1.0)
    print(f"[Thinking] ({effort})...", flush=True)
    time.sleep(delay)
    return f"Response to: {prompt} (effort={effort})"


def main():
    parser = argparse.ArgumentParser(description="Demo LLM with adjustable thinking effort")
    parser.add_argument("--prompt", required=True, help="Prompt to send to the model")
    parser.add_argument("--effort", default="medium", choices=["low","medium","high","xhigh"], help="Thinking effort level")
    args = parser.parse_args()

    response = generate_response(args.prompt, args.effort)
    print("\n---\n")
    print(response)

if __name__ == "__main__":
    main()
