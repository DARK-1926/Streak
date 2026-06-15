import os
import subprocess
import json
import requests
import re
import traceback
import time
import random
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
# DYNAMIC NEURAL GRID (REAL-TIME MODELS)
# ==========================================
def fetch_live_free_models():
    """Queries OpenRouter in real-time to find every available free model."""
    log_event("Syncing with OpenRouter Neural Grid...")
    try:
        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Filter all models that have ":free" in their ID
        free_models = [m["id"] for m in data.get("data", []) if ":free" in m["id"]]
        
        if not free_models:
            log_event("WARNING: No free models found in the grid response.")
            return []
            
        log_event(f"Discovery complete. Found {len(free_models)} free architects online.")
        random.shuffle(free_models) # Randomize to avoid hitting the same one first every time
        return free_models
    except Exception as e:
        log_event(f"Failed to sync with grid: {e}")
        return []

class NeuralGrid:
    def __init__(self, memory):
        self.memory = memory
        self.models = fetch_live_free_models()
        self.unhealthy_models = set()
        # Sort by persistent rating + random exploration bonus
        self.models.sort(key=lambda m: self.memory.get("model_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)

    def get_next_architect(self):
        if not self.models:
            return None
            
        for model in self.models:
            if model not in self.unhealthy_models:
                return model
        return None

    def mark_unhealthy(self, model):
        log_event(f"Marking {model} as UNHEALTHY. Rotating...")
        self.unhealthy_models.add(model)
        
        # Penalize in persistent memory
        if "model_ratings" not in self.memory: self.memory["model_ratings"] = {}
        self.memory["model_ratings"][model] = self.memory["model_ratings"].get(model, 0) - 1
        save_memory(self.memory)

    def mark_healthy(self, model):
        if "model_ratings" not in self.memory: self.memory["model_ratings"] = {}
        self.memory["model_ratings"][model] = self.memory["model_ratings"].get(model, 0) + 1
        save_memory(self.memory)

    def is_depleted(self):
        return len(self.unhealthy_models) >= len(self.models)

# ==========================================
# BRAIN UTILS
# ==========================================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "model_ratings" not in data: data["model_ratings"] = {}
                return data
        except: pass
    return {"score": 0, "history": [], "model_ratings": {}}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def fetch_trends():
    log_event("Scanning Hacker News for high-impact problems...")
    try:
        ask = requests.get("https://hacker-news.firebaseio.com/v0/askstories.json", timeout=10).json()[:8]
        context = []
        for sid in ask:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if s: context.append(f"Trend: {s.get('title')}\nDetails: {s.get('text', '')[:300]}")
        return "\n\n".join(context)
    except: return "Focus: AI-driven autonomous systems."

def ask_grid(model, trends, error_context=None):
    log_event(f"Consulting Architect: {model}...")
    
    sys_prompt = """You are the 'Council of AGI Architects'. You only output verified, working code.
Simulate a debate between Visionary, Security, and Engineering leads.
Respond ONLY with raw JSON. Strive for perfection."""
    
    retry_guidance = ""
    if error_context:
        retry_guidance = f"\n\nPREVIOUS ERROR LOG (FIX THIS):\n{error_context}"

    user_prompt = f"""
Trends:
{trends}
{retry_guidance}

CRITICAL REQUIREMENT: You MUST include a `.gitignore` file in your files array. This .gitignore MUST ignore heavy directories like `.venv`, `node_modules`, `__pycache__`, etc., to keep the project size extremely small. Do NOT push heavy files.


Respond ONLY with this JSON schema:
{{
    "project_name": "name",
    "vision": "Why this works",
    "files": [ {{"filepath": "...", "content": "..."}} ],
    "setup_and_test_script": "Windows .bat script to setup venv and run tests. Exit 0 on success.",
    "commit_message": "feat: enterprise-grade launch"
}}
"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json={
            "model": model, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.4
        }, timeout=180)
        
        res_data = response.json()
        
        # Check for OpenRouter-level error messages hidden in JSON
        if "error" in res_data:
            log_event(f"Grid Error from {model}: {res_data['error'].get('message', 'Unknown')}")
            return None
            
        content = res_data["choices"][0]["message"]["content"]
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match: return json.loads(match.group(0))
    except Exception as e:
        log_event(f"Architect {model} connectivity error: {e}")
        
    return None

# ==========================================
# THE RELENTLESS EXECUTION LOOP
# ==========================================
def run_beast_cycle():
    log_event("========================================")
    log_event(" AGENT BEAST V4.0: DYNAMIC NEURAL GRID")
    log_event("========================================")
    
    memory = load_memory()
    success = False
    error_log = None
    
    while not success:
        grid = NeuralGrid(memory)
        
        if not grid.models:
            log_event("Grid sync failed. Entering Meditation (Sleep 5m)...")
            time.sleep(300)
            continue
            
        while not grid.is_depleted() and not success:
            model = grid.get_next_architect()
            if not model: break
            
            trends = fetch_trends()
            data = ask_grid(model, trends, error_context=error_log)
            
            if not data:
                grid.mark_unhealthy(model)
                continue
                
            try:
                project_name = data["project_name"]
                project_dir = os.path.join(PROJECTS_DIR, project_name)
                os.makedirs(project_dir, exist_ok=True)
                
                # Write files
                for f_info in data["files"]:
                    f_path = os.path.join(project_dir, f_info["filepath"])
                    os.makedirs(os.path.dirname(f_path), exist_ok=True)
                    with open(f_path, "w", encoding="utf-8") as f: f.write(f_info["content"])
                
                # Validation
                script_path = os.path.join(project_dir, "setup_and_test.bat")
                with open(script_path, "w", encoding="utf-8") as f: f.write(data["setup_and_test_script"])
                
                log_event(f"Validating {project_name} built by {model}...")
                result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                         cwd=project_dir, capture_output=True, text=True, timeout=1200)
                
                if result.returncode == 0:
                    success = True
                    grid.mark_healthy(model)
                    log_event(f"VICTORY ACHIEVED! Code is working.")
                    memory["score"] += 1
                    memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": model})
                    save_memory(memory)
                    
                    # Push ONLY successful code
                    subprocess.run(["git", "add", "."], check=True)
                    subprocess.run(["git", "commit", "-m", data["commit_message"]], check=True)
                    subprocess.run(["git", "push", "origin", "main"], check=True)
                else:
                    log_event(f"FAILURE. Physicist rejected the code. Recycling error log and rotating model...")
                    error_log = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                    grid.mark_unhealthy(model) # Instantly drop model and rotate to next best
                    time.sleep(2) # Brief cooldown

            except Exception as e:
                log_event(f"Architectural Collapse: {e}")
                error_log = str(e)
                time.sleep(2)
        
        if not success:
            log_event("ENTIRE NEURAL GRID CONGESTED. Entering Deep Meditation (Sleep 10m)...")
            time.sleep(600)

if __name__ == "__main__":
    run_beast_cycle()
