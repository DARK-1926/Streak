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
# DYNAMIC NEURAL GRID
# ==========================================
def fetch_live_free_models():
    log_event("Syncing with OpenRouter Neural Grid...")
    try:
        url = "https://openrouter.ai/api/v1/models"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        free_models = [m["id"] for m in data.get("data", []) if ":free" in m["id"]]
        if not free_models:
            log_event("WARNING: No free models found in the grid response.")
            return []
        log_event(f"Discovery complete. Found {len(free_models)} free architects online.")
        random.shuffle(free_models)
        return free_models
    except Exception as e:
        log_event(f"Failed to sync with grid: {e}")
        return []

class NeuralGrid:
    def __init__(self, memory):
        self.memory = memory
        self.models = fetch_live_free_models()
        self.unhealthy_models = set()
        self.models.sort(key=lambda m: self.memory.get("model_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)

    def get_next_architect(self):
        if not self.models: return None
        for model in self.models:
            if model not in self.unhealthy_models: return model
        return None

    def mark_unhealthy(self, model):
        log_event(f"Marking {model} as UNHEALTHY. Rotating to next model...")
        self.unhealthy_models.add(model)
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
                if "past_projects" not in data: data["past_projects"] = []
                if "lessons_learned" not in data: data["lessons_learned"] = []
                return data
        except: pass
    return {"score": 0, "history": [], "model_ratings": {}, "past_projects": [], "lessons_learned": []}

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

# ==========================================
# MULTI-STAGE API CALLS
# ==========================================
def call_openrouter(model, sys_prompt, user_prompt):
    time.sleep(3.5) # Respect 20 RPM limit
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json={
            "model": model,
            "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.4
        }, timeout=180)
        res_data = response.json()
        if "error" in res_data:
            err_msg = res_data['error'].get('message', 'Unknown')
            log_event(f"OpenRouter Error ({model}): {err_msg}")
            if "rate limit" in err_msg.lower() or "timeout" in err_msg.lower() or "502" in err_msg:
                return "RATE_LIMIT_OR_SERVER_ERROR"
            return None
        return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        log_event(f"API Request Failed ({model}): {e}")
        return "RATE_LIMIT_OR_SERVER_ERROR"

def extract_json(content):
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except: pass
    return None

def strip_markdown(content):
    if content.startswith("```"):
        lines = content.splitlines()
        if len(lines) >= 2 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1])
    return content

def plan_project(model, trends, memory, error_context=None):
    log_event(f"Stage 1: Planning Project with Architect {model}...")
    sys_prompt = "You are the Lead AGI Architect. Respond ONLY with valid JSON."
    retry_guidance = f"\nPREVIOUS RUN FAILED. FIX ERRORS:\n{error_context}" if error_context else ""
    past_projects = "\n".join(memory.get("past_projects", [])[-10:])
    user_prompt = f"""
    Design a new, small, fully functional software application. It MUST be modular and minimal (max 8 files) to respect free-tier LLM token limits.
    Trends: {trends}
    Past Projects: {past_projects}
    {retry_guidance}
    
    CRITICAL: 
    1. Include a .gitignore to ignore venv, node_modules, __pycache__.
    2. Include a README.md.
    
    Respond ONLY with this JSON schema:
    {{
        "project_name": "name",
        "vision": "Why this works and what it does",
        "lessons_learned": "What novel approach avoids past mistakes",
        "commit_message": "feat: enterprise-grade launch",
        "files_to_generate": [
            {{
                "filepath": "path/to/file.ext",
                "instructions": "Extremely detailed prompt on exactly what logic this file must contain."
            }}
        ]
    }}
    """
    content = call_openrouter(model, sys_prompt, user_prompt)
    if content == "RATE_LIMIT_OR_SERVER_ERROR": return "ERROR"
    if not content: return None
    return extract_json(content)

def generate_file_chunked(model, project_name, vision, filepath, instructions):
    log_event(f"Stage 2: Generating File -> {filepath} (Chunked)...")
    sys_prompt = "You are an Expert Software Engineer. You write clean, robust code."
    if "gitignore" in filepath.lower():
        sys_prompt += "\nYou are writing a .gitignore file. Never include venv, node_modules, or cache."
        instructions += "\nCRITICAL: Ignore .venv, node_modules, __pycache__."
    elif "readme" in filepath.lower():
        instructions += "\nCRITICAL: Include a 'How it Works' section."
        
    base_prompt = f"""
    Project: {project_name}
    Vision: {vision}
    Task: Write ONLY the exact contents for the file: `{filepath}`.
    Instructions: {instructions}
    
    RULES:
    1. Write proper, lengthy production code.
    2. Return ONLY raw file contents. No explanations.
    3. CRITICAL: When you are COMPLETELY FINISHED writing the entire file, append the exact token `[EOF]` at the very end. Do NOT use `[EOF]` until the entire file is complete.
    """
    
    full_content = ""
    chunks_completed = 0
    max_chunks = 8
    
    while chunks_completed < max_chunks:
        if chunks_completed == 0:
            user_prompt = base_prompt
        else:
            last_lines = full_content[-300:]
            user_prompt = f"""
            You hit the output limit while generating `{filepath}`.
            CONTINUE EXACTLY from where you left off. Do NOT repeat code you already wrote. Do NOT apologize.
            The last part you generated was:
            ```
            {last_lines}
            ```
            Start typing the exact next characters seamlessly. Remember to output `[EOF]` when fully done.
            """
            log_event(f"Requesting Continuation Chunk {chunks_completed+1} for {filepath}...")
            
        content = call_openrouter(model, sys_prompt, user_prompt)
        if content == "RATE_LIMIT_OR_SERVER_ERROR":
            return "ERROR"
        if not content:
            break
            
        content = strip_markdown(content)
        
        if "[EOF]" in content:
            full_content += content.replace("[EOF]", "")
            break
        else:
            full_content += content
            chunks_completed += 1
            
    return full_content

def generate_tests(model, project_name, file_list):
    log_event(f"Stage 3: Generating Integration Script for {project_name}...")
    sys_prompt = "You are a QA Lead. Respond ONLY with the raw script contents."
    user_prompt = f"""
    Project: {project_name}
    Files created: {', '.join(file_list)}
    
    Write a Windows .bat script named 'setup_and_test.bat'.
    1. Setup venv (Python) or npm install (Node).
    2. Install dependencies.
    3. Run tests. If no tests exist, run the main file to see if it parses/starts properly for 5 seconds.
    4. MUST Exit with code 0 if success, 1 if fail.
    Output ONLY raw script. No explanations.
    """
    content = call_openrouter(model, sys_prompt, user_prompt)
    if content == "RATE_LIMIT_OR_SERVER_ERROR": return "ERROR"
    if not content: return None
    return strip_markdown(content)

def fix_error(model, project_dir, files_created, error_log):
    log_event(f"Stage 4: Identifying Fixes...")
    sys_prompt = "You are a Debugger. You fix code and respond ONLY with valid JSON."
    user_prompt = f"""
    The test script failed.
    Files in project: {', '.join(files_created)}
    Error Log:
    {error_log}
    
    Identify which files need fixing to resolve this syntax/runtime error.
    Respond ONLY with this JSON schema:
    {{
        "files_to_update": [
            {{
                "filepath": "path/to/file.ext",
                "instructions": "Detailed instructions on what lines to change to fix the error."
            }}
        ]
    }}
    """
    content = call_openrouter(model, sys_prompt, user_prompt)
    if content == "RATE_LIMIT_OR_SERVER_ERROR": return "ERROR"
    if not content: return None
    return extract_json(content)

# ==========================================
# THE RELENTLESS EXECUTION LOOP
# ==========================================
def run_beast_cycle():
    log_event("========================================")
    log_event(" AGENT BEAST V6.0: RESILIENT ARCHITECT")
    log_event("========================================")
    
    memory = load_memory()
    
    while True: # Outer infinite loop for continuous operation
        grid = NeuralGrid(memory)
        if not grid.models:
            log_event("Grid sync failed. Sleep 5m...")
            time.sleep(300)
            continue
            
        success = False
        project_state_file = os.path.join(PROJECTS_DIR, "active_project_state.json")
        
        # Load active project state if it exists
        project_state = {}
        if os.path.exists(project_state_file):
            try:
                with open(project_state_file, "r", encoding="utf-8") as f:
                    project_state = json.load(f)
                log_event("Found an active project state! Resuming from where we left off...")
            except: pass
            
        while not grid.is_depleted() and not success:
            model = grid.get_next_architect()
            if not model: break
            
            log_event(f"--- Assigning Model: {model} ---")
            
            # STAGE 1: PLAN (if not already planned)
            if not project_state.get("plan"):
                trends = fetch_trends()
                plan = plan_project(model, trends, memory)
                if plan == "ERROR":
                    grid.mark_unhealthy(model)
                    continue
                if not plan or "files_to_generate" not in plan:
                    log_event(f"Architect {model} failed planning phase.")
                    grid.mark_unhealthy(model) 
                    continue
                    
                project_state["plan"] = plan
                project_state["files_created"] = []
                with open(project_state_file, "w", encoding="utf-8") as f: 
                    json.dump(project_state, f, indent=4)
                
            plan = project_state["plan"]
            project_name = plan.get("project_name", f"AI_Project_{int(time.time())}")
            project_dir = os.path.join(PROJECTS_DIR, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            log_event(f"Working on '{project_name}'...")
            
            # STAGE 2: GENERATE FILES
            generation_failed = False
            for f_info in plan["files_to_generate"]:
                filepath = f_info.get("filepath")
                instructions = f_info.get("instructions", "")
                if not filepath or filepath in project_state["files_created"]:
                    continue # Already generated by a previous model
                    
                content = generate_file_chunked(model, project_name, plan.get("vision", ""), filepath, instructions)
                if content == "ERROR":
                    generation_failed = True
                    grid.mark_unhealthy(model) # Rate limit hit, switch model
                    break
                if not content:
                    generation_failed = True
                    grid.mark_unhealthy(model)
                    break
                
                full_path = os.path.join(project_dir, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                
                project_state["files_created"].append(filepath)
                with open(project_state_file, "w", encoding="utf-8") as f: 
                    json.dump(project_state, f, indent=4)
                log_event(f"Saved {filepath} ({len(content)} bytes).")
                
            if generation_failed:
                log_event(f"Generation interrupted. Model {model} swapped. Progress saved.")
                continue # Next model will pick up where it left off
                
            # STAGE 3: TESTS & FIX LOOP
            files_created = project_state["files_created"]
            test_script = generate_tests(model, project_name, files_created)
            if test_script == "ERROR" or not test_script:
                grid.mark_unhealthy(model)
                continue
                
            script_path = os.path.join(project_dir, "setup_and_test.bat")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(test_script.strip())
                
            # Fix Loop: Same model fixes syntax errors up to 3 times
            fix_attempts = 0
            while fix_attempts < 3:
                log_event(f"Validating {project_name} (Attempt {fix_attempts+1}/3)...")
                try:
                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                             cwd=project_dir, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        success = True
                        break # Exits the fix loop successfully
                    else:
                        log_event(f"FAILURE. Syntax/Test error. Asking SAME model to fix...")
                        error_log = f"STDOUT:\n{result.stdout[-1500:]}\nSTDERR:\n{result.stderr[-1500:]}"
                        
                        fix_plan = fix_error(model, project_dir, files_created, error_log)
                        if fix_plan == "ERROR" or not fix_plan or "files_to_update" not in fix_plan:
                            log_event("Model failed to provide a fix plan. Aborting fix attempt.")
                            break
                            
                        # Apply fixes using chunked generation
                        for f_info in fix_plan["files_to_update"]:
                            filepath = f_info.get("filepath")
                            instructions = f_info.get("instructions", "")
                            if not filepath: continue
                            
                            log_event(f"Applying fix to {filepath}...")
                            content = generate_file_chunked(model, project_name, "Fixing errors", filepath, instructions)
                            if content and content != "ERROR":
                                full_path = os.path.join(project_dir, filepath)
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write(content.strip())
                        fix_attempts += 1
                except subprocess.TimeoutExpired:
                    log_event("Test script timed out. Likely a hanging process.")
                    break
                    
            if success:
                grid.mark_healthy(model)
                log_event(f"VICTORY ACHIEVED! Code is fully working.")
                memory["score"] += 1
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": model})
                save_memory(memory)
                
                # Push
                try:
                    subprocess.run(["git", "add", "."], check=True, cwd=REPO_ROOT)
                    subprocess.run(["git", "commit", "-m", plan.get("commit_message", "feat: resilient ai launch")], check=True, cwd=REPO_ROOT)
                    subprocess.run(["git", "push", "origin", "main"], check=True, cwd=REPO_ROOT)
                    log_event("Code successfully pushed to GitHub.")
                except Exception as e:
                    log_event(f"Git push failed: {e}")
                    
                # Clean up state for next project
                if os.path.exists(project_state_file):
                    os.remove(project_state_file)
                break # Exit the model assignment loop, ready for a new project
            else:
                log_event(f"Model {model} failed to fix the project after 3 attempts. Rotating model...")
                grid.mark_unhealthy(model)
                time.sleep(2)

        if not success:
            log_event("ENTIRE NEURAL GRID CONGESTED. Entering Deep Meditation (Sleep 10m)...")
            time.sleep(600)

if __name__ == "__main__":
    run_beast_cycle()
