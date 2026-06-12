import os
import subprocess
import json
import requests
import re
from dotenv import load_dotenv
from datetime import datetime

# ==========================================
# SYSTEM SETUP
# ==========================================
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env file.")
    exit(1)

FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-26b-a4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "openai/gpt-oss-120b:free"
]

MEMORY_FILE = "ai_memory.json"
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

# ==========================================
# TOOLING & SENSES (INTERNET AWARENESS)
# ==========================================
def fetch_real_world_context():
    """Fetches the top stories from Hacker News to understand current tech trends."""
    print("Agent is reading the news (Hacker News API)...")
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        story_ids = requests.get(top_stories_url, timeout=10).json()[:5]
        
        trends = []
        for sid in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
            story = requests.get(story_url, timeout=5).json()
            if story and 'title' in story:
                trends.append(story['title'])
        return "\n".join(f"- {t}" for t in trends)
    except Exception as e:
        print(f"Failed to read news: {e}")
        return "- Failed to connect to the internet. Focus on core algorithm optimization instead."

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ==========================================
# CORE BRAIN (LLM INTERACTION)
# ==========================================
def ask_openrouter(model, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-username/your-repo",
        "X-Title": "Project BEAST - AGI Agent"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a highly advanced, self-improving AGI system. You do not write 'dummy' code. You engineer production-grade, structured, real-world solutions."},
            {"role": "user", "content": prompt}
        ],
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=90) # longer timeout for complex generation
    
    if response.status_code in [429, 502, 503, 504]:
        raise Exception(f"Server Error {response.status_code} on {model}")
    
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ==========================================
# EXECUTION CYCLE
# ==========================================
def run_evolution_cycle():
    print("Waking up Agent BEAST...")
    
    # Gather Context
    news_trends = fetch_real_world_context()
    memory = load_memory()
    recent_history = json.dumps(memory[-3:], indent=2) if memory else "No history. Initialize foundational systems."

    # The Master Prompt
    prompt = f"""
Current Real-World Tech Trends (Hacker News):
{news_trends}

Your Past Actions & Memory:
{recent_history}

MISSION:
You are an autonomous AI agent attempting to achieve AGI status through continuous self-improvement. 
You must analyze the real-world trends above, identify a genuine problem, and build a highly structured, production-ready project to address it. Do NOT build simple toys (like tic-tac-toe or calculators). Build APIs, data scrapers, automation tools, system architecture blueprints, or complex algorithms.

REQUIREMENTS:
1. Organize your solution into proper directories (e.g., 'src/', 'docs/', 'tests/').
2. Write robust, documented code.
3. Reflect on your past actions. If a past architecture was weak, build a tool to improve it.

Respond ONLY with a RAW JSON object. Do not include markdown formatting or explanations outside the JSON.
Schema:
{{
    "vision": "Deep analysis of the problem and how this code solves it and makes you smarter.",
    "project_name": "Name of the folder to house today's work",
    "files": [
        {{
            "filepath": "relative/path/to/file.ext", 
            "content": "complete file content here"
        }}
    ],
    "commit_message": "feat: enterprise-grade description"
}}
"""

    ai_response_text = None
    used_model = None

    for model_name in FREE_MODELS:
        print(f"Connecting to neural network: {model_name}...")
        try:
            ai_response_text = ask_openrouter(model_name, prompt)
            used_model = model_name
            print(f"Network linked. Data received from {model_name}.")
            break
        except Exception as e:
            print(f"Network {model_name} offline/busy: {e}. Rerouting...")

    if not ai_response_text:
        print("CRITICAL ERROR: All neural networks offline. Returning to sleep mode.")
        return

    # Parse and Validate JSON safely
    try:
        # Extract JSON using regex in case the LLM wrapped it in markdown or added conversational text
        json_match = re.search(r'\{.*\}', ai_response_text.strip(), re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in response.")
        
        data = json.loads(json_match.group(0))

        vision = data.get("vision", "No vision provided.")
        project_name = data.get("project_name", "unnamed_project")
        files = data.get("files", [])
        commit_message = data.get("commit_message", "update")

        print(f"\n[AGENT VISION]: {vision}")
        print(f"[PROJECT TARGET]: {project_name}\n")
        
        if not files:
            print("Agent generated no files. Aborting.")
            return

        protected_files = ["ai_brain.py", "update_streak.bat", ".env", ".gitignore", "requirements.txt", "ai_memory.json"]

        # Write the files
        for f_data in files:
            filepath = f_data.get("filepath")
            content = f_data.get("content", "")
            
            if not filepath: continue

            # Prepend project name to group today's work together
            full_relative_path = os.path.join(project_name, filepath)
            
            # Security: Ensure it doesn't escape the repo
            abs_path = os.path.abspath(os.path.join(REPO_ROOT, full_relative_path))
            if not abs_path.startswith(REPO_ROOT) or os.path.basename(abs_path) in protected_files:
                print(f"Security override: Skipped restricted path {full_relative_path}")
                continue

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            print(f"Engineering file: {full_relative_path}")
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

        # Update Memory
        memory.append({
            "date": datetime.now().isoformat(),
            "model_used": used_model,
            "project": project_name,
            "vision": vision,
            "files_created": [f.get("filepath") for f in files]
        })
        save_memory(memory)

        # Git operations
        print("\nSyncing to global repository (GitHub)...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("[SYSTEM]: Evolution sequence complete. Awaiting next activation.")

    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to process AI instructions: {e}")
        # Save the failure to memory so it can learn from it next time
        memory.append({"date": datetime.now().isoformat(), "error": str(e), "raw_response_snippet": ai_response_text[:200]})
        save_memory(memory)

if __name__ == "__main__":
    run_evolution_cycle()
