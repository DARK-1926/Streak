import os
import subprocess
import json
import requests
import re
import traceback
from dotenv import load_dotenv
from datetime import datetime

# ==========================================
# SYSTEM SETUP & CONSTANTS
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
PROJECTS_DIR = os.path.join(REPO_ROOT, "autonomous_projects")

os.makedirs(PROJECTS_DIR, exist_ok=True)

# ==========================================
# MEMORY & LEARNING SYSTEM
# ==========================================
def load_memory():
    default_mem = {
        "score": 0,
        "successful_patterns": [],
        "failed_patterns": [],
        "history": []
    }
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    default_mem["history"] = data
                    return default_mem
                return data
        except Exception as e:
            print(f"Memory load error: {e}")
            return default_mem
    return default_mem

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ==========================================
# TOOLING (SENSES)
# ==========================================
def fetch_real_world_context():
    print("[SYSTEM] Fetching real-world problems from Ask HN and Show HN...")
    trends = []
    try:
        # Fetch Ask HN for direct problems
        ask_url = "https://hacker-news.firebaseio.com/v0/askstories.json"
        ask_ids = requests.get(ask_url, timeout=10).json()[:6]
        for sid in ask_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if story and 'title' in story:
                trends.append(f"[Ask HN] {story['title']}")
                
        # Fetch Top HN for general trends
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        top_ids = requests.get(top_url, timeout=10).json()[:4]
        for sid in top_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if story and 'title' in story:
                trends.append(f"[Top HN] {story['title']}")
                
        return "\n".join(f"- {t}" for t in trends)
    except Exception as e:
        print(f"[SYSTEM] HN fetch failed: {e}")
        return "Fallback Trend: How do I batch rename files by date recursively?"

# ==========================================
# LLM ENGINE
# ==========================================
def ask_llm(system_prompt, user_prompt, temperature=0.7):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/DARK-1926/Streak",
        "X-Title": "Project BEAST - MultiAgent"
    }
    
    for model in FREE_MODELS:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=90)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"], model
        except Exception as e:
            print(f"[NETWORK] Model {model} failed: {e}")
            continue
    raise Exception("All LLM models offline or failed.")

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response.")
    return json.loads(match.group(0))

# ==========================================
# AGENTS
# ==========================================
def generate_project(memory, trends):
    print("\n[SYSTEM] Booting Multi-Agent Simulation Matrix...")
    sys_prompt = "You are an autonomous multi-agent developer system. You simulate 4 specialized agents working together to solve real-world problems."
    user_prompt = f"""
Here are the current real-world problems and trends from Hacker News:
{trends}

System Memory:
- AI Score: {memory['score']}
- Past Failures (Avoid these patterns): {json.dumps(memory['failed_patterns'][-3:])}

YOUR JOB:
1. Pick the most upvoted/interesting problem from the trends that involves software, tools, APIs, automation, or productivity.
2. Simulate a deep internal discussion between 4 agents:
   - AGENT 1 (RESEARCHER): Defines the concrete problem, who has it, and the CLI solution.
   - AGENT 2 (CODER): Writes the code. STRICT CONSTRAINTS: Use pure Python (stdlib + 'requests' library ONLY). Do not launch GUIs, browsers, or servers. Build CLI tools and scripts only.
   - AGENT 3 (AUDITOR): Mentally executes the code. Checks for import errors, unhandled exceptions, and logic bugs. Fixes them internally.
   - AGENT 4 (REVIEWER): Scores the code (1-10) on correctness and real-world usefulness. Modifies it if below 7.

3. After your internal simulation, output the FINAL result as a SINGLE RAW JSON OBJECT. 
You MUST provide a main.py, a run_tests.py (which imports main.py and uses assert statements to verify logic), and a README.md.

Respond ONLY with this exact JSON schema (do not wrap in markdown):
{{
    "simulation_log": "Summary of the 4 agents' thoughts, audits, and decisions.",
    "project_name": "folder_name_no_spaces",
    "commit_message": "feat: solve HN problem - [title] - Agent score X/10",
    "files": [
        {{"filepath": "main.py", "content": "full working code here"}},
        {{"filepath": "run_tests.py", "content": "import main\\n\\ndef test_logic():\\n    assert ...\\n\\nif __name__ == '__main__':\\n    test_logic()\\n    print('Tests passed')"}},
        {{"filepath": "README.md", "content": "..."}}
    ],
    "memory_update": {{
        "problem_source": "Hacker News",
        "solution_name": "name of script",
        "agent_score": 9,
        "what_worked": "what the simulated team feels is strong about this code"
    }}
}}
"""
    response, model = ask_llm(sys_prompt, user_prompt, 0.7)
    return extract_json(response)

def physical_reviewer(error_log, files_data):
    print("\n[AGENT: PHYSICAL REVIEWER] Analyzing real-world test failures and fixing code...")
    sys_prompt = "You are the QA Debugger AGI. Fix the broken Python code based on the error trace."
    user_prompt = f"""
The physical tests failed!
Error Trace:
{error_log}

Current Files:
{json.dumps(files_data)}

Fix the code to make `run_tests.py` execute successfully (exit code 0).
Remember the constraint: Python stdlib + 'requests' ONLY.

Respond ONLY with raw JSON in this format:
{{
    "files": [
        {{"filepath": "main.py", "content": "fixed code..."}},
        {{"filepath": "run_tests.py", "content": "fixed tests..."}}
    ]
}}
"""
    response, model = ask_llm(sys_prompt, user_prompt, 0.2)
    return extract_json(response)

# ==========================================
# EXECUTION & AUDIT ORCHESTRATOR
# ==========================================
def write_project_files(project_dir, files):
    for f in files:
        if not f.get("filepath"): continue
        path = os.path.join(project_dir, f["filepath"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(f.get("content", ""))

def run_physical_tests(project_dir):
    test_file = os.path.join(project_dir, "run_tests.py")
    if not os.path.exists(test_file):
        return False, "Error: run_tests.py missing from generated code."
    
    print(f"\n[SYSTEM] Executing physical tests in {project_dir}...")
    result = subprocess.run(["python", "run_tests.py"], cwd=project_dir, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[SYSTEM] Tests PASSED!")
        return True, result.stdout
    else:
        print(f"[SYSTEM] Tests FAILED. Exit code {result.returncode}")
        return False, result.stderr + "\n" + result.stdout

def orchestrate():
    print("========================================")
    print(" BEAST AGI - EVOLUTION CYCLE INITIATED")
    print(f" TIME: {datetime.now().isoformat()}")
    print("========================================")

    memory = load_memory()
    trends = fetch_real_world_context()
    
    try:
        # 1. Simulate Team & Generate Project
        project_data = generate_project(memory, trends)
        
        print(f"\n[SIMULATION LOG]: {project_data.get('simulation_log', 'No log provided.')}")
        
        project_name = project_data.get("project_name", f"project_{int(datetime.now().timestamp())}")
        project_dir = os.path.join(PROJECTS_DIR, project_name)
        write_project_files(project_dir, project_data.get("files", []))
        
        # 2. Physical Test & Review Loop
        max_retries = 2
        tests_passed = False
        final_error = ""

        for attempt in range(max_retries + 1):
            passed, output = run_physical_tests(project_dir)
            if passed:
                tests_passed = True
                break
            
            if attempt < max_retries:
                print(f"[SYSTEM] Attempt {attempt + 1} failed. Escalating to Physical Reviewer...")
                fixed_data = physical_reviewer(output, project_data.get("files", []))
                # Update files in our object
                for fixed_file in fixed_data.get("files", []):
                    for i, orig_file in enumerate(project_data["files"]):
                        if orig_file["filepath"] == fixed_file["filepath"]:
                            project_data["files"][i] = fixed_file
                            
                write_project_files(project_dir, fixed_data.get("files", []))
            else:
                final_error = output
        
        # Update history
        mem_update = project_data.get("memory_update", {})
        memory["history"].append({
            "date": datetime.now().isoformat(),
            "project": project_name,
            "success": tests_passed,
            "simulated_score": mem_update.get("agent_score", 0)
        })

        # 3. Audit & Reward
        if tests_passed:
            memory["score"] += 1
            print(f"\n[AUDIT] SUCCESS! Rewarding AI (+1). Total Score: {memory['score']}")
            memory["successful_patterns"].append(mem_update.get("what_worked", "Unknown success factor"))
            save_memory(memory)
            
            # Commit and push
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", project_data.get("commit_message", f"feat: {project_name}")], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("[SYSTEM] Code pushed to GitHub.")
        else:
            memory["score"] -= 1
            print(f"\n[AUDIT] FATAL FAILURE. Penalizing AI (-1). Total Score: {memory['score']}")
            memory["failed_patterns"].append({"error": final_error[:300]})
            save_memory(memory)
            
            print("[SYSTEM] Bad code retained for learning, but NOT pushed as a feature.")
            subprocess.run(["git", "add", MEMORY_FILE], check=True)
            try:
                subprocess.run(["git", "commit", "-m", f"chore: AGI penalized. Score: {memory['score']}"], check=True)
                subprocess.run(["git", "push", "origin", "main"], check=True)
            except subprocess.CalledProcessError:
                print("[SYSTEM] Git commit skipped (no changes detected).")

    except Exception as e:
        print(f"[CRITICAL FAILURE] Engine crash: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    orchestrate()
