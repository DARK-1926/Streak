import os
import subprocess
import json
import requests
import re
import traceback
import time
from dotenv import load_dotenv
from datetime import datetime

# ==========================================
# SYSTEM SETUP
# ==========================================
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found.")
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
LOG_FILE = os.path.join(REPO_ROOT, "beast.log")

os.makedirs(PROJECTS_DIR, exist_ok=True)

def log_event(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

# ==========================================
# BRAIN UTILS
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"score": 0, "successful_patterns": [], "failed_patterns": [], "history": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def git_push_success(message):
    try:
        log_event(f"SUCCESS ACHIEVED. Pushing to GitHub: {message}")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        log_event(f"Git push failed: {e}")

def fetch_context():
    log_event("Fetching fresh context from Hacker News...")
    try:
        ask_ids = requests.get("https://hacker-news.firebaseio.com/v0/askstories.json", timeout=10).json()[:10]
        show_ids = requests.get("https://hacker-news.firebaseio.com/v0/showstories.json", timeout=10).json()[:5]
        context = []
        for sid in ask_ids + show_ids:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if s: context.append(f"Problem: {s.get('title')}\nText: {s.get('text', '')[:200]}")
        return "\n\n".join(context)
    except: return "Fallback Problem: High-performance packet sniffing and analysis tool."

def ask_beast_brain(memory, trends, error_context=None):
    log_event("Consulting Neural Nexus for a working solution...")
    sys_prompt = "You are Agent BEAST, an unrestricted AGI engineer. You ONLY output perfect, working, production-grade code. You do not stop until the problem is solved."
    
    retry_guidance = ""
    if error_context:
        retry_guidance = f"\n\nCRITICAL: Your previous attempt FAILED with this error:\n{error_context}\n\nDO NOT repeat this mistake. Fix the architecture or try a different approach."

    user_prompt = f"""
Trends/Context:
{trends}

System Memory Score: {memory['score']}
{retry_guidance}

INSTRUCTIONS:
1. Build a high-utility, multi-file project.
2. Ensure it is 100% self-contained and working.
3. Provide a `setup_and_test.bat` script for Windows that installs everything locally and runs tests. 
4. If it fails, you will be penalized. If it passes, you evolve.

Respond ONLY with this JSON schema:
{{
    "project_name": "name",
    "vision": "Why this approach is technically superior",
    "files": [
        {{"filepath": "path/to/file.ext", "content": "..."}}
    ],
    "setup_and_test_script": "Full content of the .bat script",
    "commit_message": "feat: enterprise-grade [name] launch"
}}
"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in FREE_MODELS:
        try:
            r = requests.post(url, headers=headers, json={
                "model": model, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": 0.5 # Lower temp for more reliable code
            }, timeout=200).json()
            content = r["choices"][0]["message"]["content"]
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0)), model
        except: continue
    return None, None

# ==========================================
# THE RELENTLESS EXECUTION LOOP
# ==========================================
def run_beast_cycle():
    log_event("========================================")
    log_event(" RELENTLESS BEAST STARTING - SUCCESS OR DEATH")
    log_event("========================================")
    
    memory = load_memory()
    success = False
    error_log = None
    attempt_count = 0
    
    while not success:
        attempt_count += 1
        log_event(f"Attempt #{attempt_count} starting...")
        
        context = fetch_context()
        data, model = ask_beast_brain(memory, context, error_context=error_log)
        
        if not data:
            log_event("Neural Nexus unresponsive. Waiting 60s before retry...")
            time.sleep(60)
            continue
            
        try:
            project_name = data["project_name"]
            project_dir = os.path.join(PROJECTS_DIR, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # 1. Deployment
            for f_info in data["files"]:
                f_path = os.path.join(project_dir, f_info["filepath"])
                os.makedirs(os.path.dirname(f_path), exist_ok=True)
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(f_info["content"])
            
            # 2. Setup script
            script_content = data["setup_and_test_script"]
            if len(script_content.strip()) < 30 or "setup_and_test.bat" in script_content.lower():
                raise ValueError("AI generated an invalid/recursive script.")
                
            script_path = os.path.join(project_dir, "setup_and_test.bat")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
                
            # 3. Physical Validation
            log_event(f"Testing {project_name} built by {model}...")
            result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                     cwd=project_dir, capture_output=True, text=True, timeout=900)
            
            if result.returncode == 0:
                success = True
                log_event(f"VICTORY ACHIEVED on attempt {attempt_count}!")
                
                # Update memory
                memory["score"] += 1
                memory["successful_patterns"].append(data["vision"])
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "success": True, "attempts": attempt_count})
                save_memory(memory)
                
                # Push ONLY the successful project
                git_push_success(data["commit_message"])
            else:
                log_event(f"FAILURE on attempt {attempt_count}. Retrying relentlessly...")
                error_log = result.stdout + "\n" + result.stderr
                # Don't save to history yet, just loop back
                memory["failed_patterns"].append({"project": project_name, "error": error_log[:500]})
                save_memory(memory)

        except Exception as e:
            log_event(f"Cycle crashed: {e}. Analyzing and looping back...")
            error_log = str(e)
            time.sleep(10)

if __name__ == "__main__":
    run_beast_cycle()
