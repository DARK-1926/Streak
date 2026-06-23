import sys
from typing import Optional, Any

from llm_chat import initialize_llm, generate_response

def handle_input(llm: Any, user_input: str) -> Optional[str]:
    """
    Handle the user input and generate a response from the LLM.
    
    :param llm: An initialized instance of LightweightLLM.
    :param user_input: The user's input text.
    :return: The generated response string if successful, otherwise None.
    """
    try:
        response = generate_response(llm, user_input)
        return response
    except Exception as e:
        print(f"Error handling input: {e}", file=sys.stderr)
        return None

def main(model_path: str) -> None:
    """
    Main function to run the CLI. Initializes the LLM and handles user input in a loop.
    
    :param model_path: The file path to the LLM model.
    """
    llm = initialize_llm(model_path)
    if not llm:
        print("Failed to initialize LLM. Exiting.", file=sys.stderr)
        sys.exit(1)

    print("LocalLLMChat is ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting LocalLLMChat. Goodbye!")
                break
            response = handle_input(llm, user_input)
            if response:
                print(f"LLM: {response}")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting LocalLLMChat. Goodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cli.py <path-to-model>", file=sys.stderr)
        sys.exit(1)
    model_path = sys.argv[1]
    main(model_path)