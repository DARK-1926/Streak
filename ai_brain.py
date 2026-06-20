import os
import subprocess
import json
import requests
import re
import traceback
import time
import random
import ast
import concurrent.futures
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
QUOTA_FILE = "quota.json"
MODELS_CACHE_FILE = "models_cache.json"
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECTS_DIR = os.path.join(REPO_ROOT, "autonomous_projects")
LOG_FILE = os.path.join(REPO_ROOT, "beast.log")

STYLE_GUIDE = """
- Use type hints for all function signatures.
- Write docstrings for all public classes and methods.
- Keep functions under 50 lines.
- Handle exceptions gracefully.
- Follow PEP 8 guidelines for Python code.
"""

os.makedirs(PROJECTS_DIR, exist_ok=True)

def log_event(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

# ==========================================
# QUOTA & LIMITS (Points 1 & 4)
# ==========================================
def load_quota():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(QUOTA_FILE):
        try:
            with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("date") == today:
                    return data
        except: pass
    return {"date": today, "count": 0}

def save_quota(quota):
    with open(QUOTA_FILE, "w", encoding="utf-8") as f:
        json.dump(quota, f, indent=4)

def increment_quota():
    quota = load_quota()
    quota["count"] += 1
    save_quota(quota)
    if quota["count"] >= 1000: # Assume max credit ceiling, adjust if free tier
        log_event("DAILY QUOTA EXHAUSTED (1000 requests). Exiting.")
        exit(1)

# ==========================================
# DYNAMIC NEURAL GRID (Points 5 & 15)
# ==========================================
def fetch_live_free_models():
    # Cache check (Point 5)
    if os.path.exists(MODELS_CACHE_FILE):
        if time.time() - os.path.getmtime(MODELS_CACHE_FILE) < 3600: # 1 hour cache
            try:
                with open(MODELS_CACHE_FILE, "r") as f:
                    return json.load(f)
            except: pass
            
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
        
        with open(MODELS_CACHE_FILE, "w") as f:
            json.dump(free_models, f)
            
        return free_models
    except Exception as e:
        log_event(f"Failed to sync with grid: {e}")
        return []

class NeuralGrid:
    def __init__(self, memory):
        self.memory = memory
        self.models = fetch_live_free_models()
        self.unhealthy_models = set()
        
    def get_planner_model(self):
        # Sort by ratings, favor reasoning
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        available.sort(key=lambda m: self.memory.get("model_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)
        return available[0]
        
    def get_coder_model(self):
        # Sort by ratings, could be a separate metric in future
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        available.sort(key=lambda m: self.memory.get("model_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)
        return available[0]

    def mark_unhealthy(self, model, reason="error"):
        if reason == "QUOTA_EXHAUSTED":
            log_event(f"Account Quota reached. Halting.")
            exit(1)
            
        log_event(f"Marking {model} as UNHEALTHY ({reason}). Rotating to next model...")
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

def fetch_hn_story(sid):
    try:
        return requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
    except:
        return None

def fetch_trends():
    log_event("Scanning Hacker News for high-impact problems (Parallel)...")
    try:
        ask = requests.get("https://hacker-news.firebaseio.com/v0/askstories.json", timeout=10).json()[:8]
        context = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            stories = list(executor.map(fetch_hn_story, ask))
            for s in stories:
                if s: context.append(f"Trend: {s.get('title')}\nDetails: {s.get('text', '')[:300]}")
        return "\n\n".join(context)
    except: return "Focus: AI-driven autonomous systems."

# ==========================================
# MULTI-STAGE API CALLS
# ==========================================
_request_timestamps = []

def enforce_rate_limit():
    global _request_timestamps
    now = time.time()
    _request_timestamps = [ts for ts in _request_timestamps if now - ts < 60]
    
    if len(_request_timestamps) >= 20:
        sleep_time = 60 - (now - _request_timestamps[0])
        if sleep_time > 0:
            log_event(f"Rate limit approaching (20 RPM). Sleeping for {sleep_time:.2f}s...")
            time.sleep(sleep_time)
            
    _request_timestamps.append(time.time())

def call_openrouter(model, sys_prompt, user_prompt, max_retries=3, temperature=0.4):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    
    for attempt in range(max_retries):
        enforce_rate_limit()
        increment_quota() # Track daily quota
        try:
            response = requests.post(url, headers=headers, json={
                "model": model,
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": temperature,
                "max_tokens": 8000 # Point 2
            }, timeout=180)
            res_data = response.json()
            
            # Point 7: Log token usage
            usage = res_data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            log_event(f"API Call ({model}) used {total_tokens} tokens.")
            
            if "error" in res_data:
                err_msg = res_data['error'].get('message', 'Unknown')
                err_code = res_data['error'].get('code', response.status_code)
                log_event(f"OpenRouter Error ({model}): {err_msg} (Code: {err_code})")
                
                if response.status_code == 429:
                    if "limit reached" in err_msg.lower() or "credits" in err_msg.lower():
                        return "QUOTA_EXHAUSTED" # Point 4
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    log_event(f"Transient 429. Exponential backoff: waiting {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 500:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    log_event(f"Server error. Exponential backoff: waiting {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
                return "SERVER_ERROR"
            return res_data["choices"][0]["message"]["content"]
        except Exception as e:
            log_event(f"API Request Failed ({model}): {e}")
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            log_event(f"Network error. Exponential backoff: waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(wait_time)
            
    return "SERVER_ERROR"

def extract_json(content, required_keys=None):
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if required_keys:
                for k in required_keys:
                    if k not in data:
                        log_event(f"JSON Validation Error: Missing key '{k}'")
                        return None
            return data
        except: pass
    return None

def strip_markdown(content):
    content = content.strip()
    content = re.sub(r'^```[a-zA-Z0-9_+-]*\n', '', content)
    content = re.sub(r'\n```$', '', content)
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

def extract_signatures(filepath, content):
    if not filepath.endswith('.py'):
        return f"File: {filepath} (Static/Config)"
    try:
        tree = ast.parse(content)
        signatures = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                signatures.append(f"def {node.name}")
            elif isinstance(node, ast.ClassDef):
                signatures.append(f"class {node.name}")
        sig_str = ", ".join(signatures) if signatures else "No public classes/functions"
        return f"File: {filepath} provides: {sig_str}"
    except:
        return f"File: {filepath} (Syntax error or unparseable)"

# ==========================================
# STAGES
# ==========================================
def plan_project(model, trends, memory, error_context=None):
    log_event(f"Stage 1: Planning Project with Architect {model}...")
    sys_prompt = "You are the Lead AGI Architect. Respond ONLY with valid JSON."
    retry_guidance = f"\nPREVIOUS RUN FAILED. FIX ERRORS:\n{error_context}" if error_context else ""
    past_projects = "\n".join(memory.get("past_projects", [])[-10:])
    lessons_learned = "\n".join(memory.get("lessons_learned", [])[-10:])
    
    user_prompt = f"""
    You are operating under the Get Shit Done (GSD) autonomous agent framework.
    Design a new, innovative, fully functional software application. 
    
    PROBLEM SELECTION (Agentic Gaps):
    Do not build generic CRUD apps. Build "Specialist Agents" or solve specific developer/agentic gaps (e.g., automated test case generators, RAG-based code analyzers, specialized linters).
    
    CRITICAL SCOPE LIMITS for Free LLMs:
    - You must keep the architecture extremely compact (maximum 8 files).
    - Avoid 'enterprise boilerplate'. Pack the complexity into dense, robust files.
    - Do NOT design things requiring paid external APIs or massive datasets.
    
    SPEC-DRIVEN DEVELOPMENT & DETERMINISTIC VALIDATION:
    1. Your plan must include explicit `interface_contracts` declaring function signatures for cross-file dependencies.
    2. Your plan must include a strict unit test suite (`test_main.py` or similar). The code MUST pass its own tests.
    3. Include a `.gitignore` to ignore venv, node_modules, __pycache__, .env.
    4. Include a `README.md` explaining the architecture.
    
    Trends: {trends}
    
    PAST PROJECTS COMPLETED:
    {past_projects}
    
    LESSONS LEARNED FROM PAST MISTAKES:
    {lessons_learned}
    
    {retry_guidance}
    
    Respond ONLY with this JSON schema:
    {{
        "project_name": "name",
        "vision": "A strict Spec Roadmap detailing the exact Agentic problem, atomic milestones, and Testing Strategy.",
        "interface_contracts": "Explicit mapping of which file provides which functions/classes.",
        "lessons_learned": "What novel approach avoids past mistakes",
        "commit_message": "Describe exactly what this project implements in one short sentence.",
        "files_to_generate": [
            {{
                "filepath": "path/to/file.ext",
                "instructions": "Extremely detailed prompt on exactly what logic this file must contain."
            }}
        ]
    }}
    """
    content = call_openrouter(model, sys_prompt, user_prompt, temperature=0.8) # High temp for planning
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return content
    if not content: return None
    return extract_json(content, required_keys=["project_name", "files_to_generate", "lessons_learned", "interface_contracts"])

def critique_plan(model, plan):
    log_event(f"Stage 1b: Critiquing Plan...")
    sys_prompt = "You are an Architecture Critic. You review JSON plans and improve them. Output JSON."
    user_prompt = f"""
    Review this proposed project plan:
    {json.dumps(plan)}
    
    Check for:
    1. Scope creep (more than 8 files).
    2. Hidden paid-API dependencies.
    3. Missing interfaces or missing test coverage.
    
    Respond ONLY with the completely fixed, valid JSON plan using the exact same schema.
    """
    content = call_openrouter(model, sys_prompt, user_prompt, temperature=0.2)
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return plan # fallback to original plan
    critique = extract_json(content, required_keys=["files_to_generate"])
    return critique if critique else plan

def check_dependencies(file_list, project_dir):
    log_event("Sanity checking dependencies...")
    # Very lightweight check. Look for requirements.txt
    req_path = os.path.join(project_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            pkgs = [line.split("==")[0].strip() for line in f if line.strip() and not line.startswith("#")]
        for pkg in pkgs:
            # Simple check
            if not pkg: continue
            try:
                res = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=3)
                if res.status_code == 404:
                    log_event(f"WARNING: Hallucinated package detected: {pkg}")
                    return False
            except: pass
    return True

def generate_file_chunked(model, project_name, vision, filepath, instructions, project_blueprint=""):
    log_event(f"Stage 2: Generating File -> {filepath} (Chunked)...")
    sys_prompt = "You are an Expert Software Engineer operating under the GSD framework. You write clean, robust code."
    if "gitignore" in filepath.lower():
        sys_prompt += "\nYou are writing a .gitignore file. Never include venv, node_modules, or cache."
        instructions += "\nCRITICAL: Ignore .venv, node_modules, __pycache__, .env."
    elif "readme" in filepath.lower():
        instructions += "\nCRITICAL: Include a 'How it Works' section."
        
    blueprint_section = f"\n    ROLLING BLUEPRINT (Context of previously generated files):\n    {project_blueprint}\n" if project_blueprint else ""
        
    base_prompt = f"""
    Project: {project_name}
    Vision: {vision}
    {blueprint_section}
    Task: Write ONLY the exact contents for the file: `{filepath}`.
    Instructions: {instructions}
    
    STYLE GUIDE:
    {STYLE_GUIDE}
    
    RULES:
    1. Write proper, lengthy production code. Ensure it integrates correctly with the Rolling Blueprint.
    2. Return ONLY raw file contents. No explanations.
    3. Do NOT wrap your output in markdown code blocks. Just plain text.
    4. CRITICAL: When you are COMPLETELY FINISHED writing the entire file, append the exact token `[EOF]` at the very end. Do NOT use `[EOF]` until the entire file is complete.
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
            Start typing the exact next characters seamlessly. Do NOT wrap output in markdown. Remember to output `[EOF]` when fully done.
            """
            log_event(f"Requesting Continuation Chunk {chunks_completed+1} for {filepath}...")
            
        content = call_openrouter(model, sys_prompt, user_prompt, temperature=0.1) # Point 20: low temp for coding
        if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]:
            return content
        if not content:
            break
            
        content = strip_markdown(content)
        
        if "[EOF]" in content:
            full_content += content.replace("[EOF]", "")
            return strip_markdown(full_content)
        else:
            full_content += content
            chunks_completed += 1
            
    # Point 13: Treat missing EOF at max_chunks as failure
    log_event(f"Failed to generate full file {filepath} within {max_chunks} chunks.")
    return "ERROR_TRUNCATED"

def generate_tests(model, project_name, file_list):
    log_event(f"Stage 3: Generating Integration Script for {project_name}...")
    sys_prompt = "You are a QA Lead. Respond ONLY with the raw script contents."
    user_prompt = f"""
    Project: {project_name}
    Files created: {', '.join(file_list)}
    
    Write a Windows .bat script named 'setup_and_test.bat'.
    1. Setup venv (Python) or npm install (Node).
    2. Install dependencies.
    3. Run rigorous unit tests (pytest for Python) to verify REAL coverage.
    4. MUST Exit with code 0 if success, 1 if fail.
    Output ONLY raw script. Do NOT wrap in markdown code blocks. No explanations.
    """
    content = call_openrouter(model, sys_prompt, user_prompt, temperature=0.1)
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR"
    if not content: return None
    return strip_markdown(content)

def fix_error(model, project_dir, files_created, error_log):
    log_event(f"Stage 4: Identifying Fixes (Reflect & Critique)...")
    
    # Point 8: Read actual file contents
    file_contents = {}
    for fname in files_created:
        full_path = os.path.join(project_dir, fname)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                file_contents[fname] = f.read()[:3000] # Cap size per file
                
    files_str = "\n".join([f"--- {k} ---\n{v}\n" for k, v in file_contents.items()])
                
    sys_prompt = "You are a Debugger operating under the GSD framework. You fix code and respond ONLY with valid JSON."
    user_prompt = f"""
    The test script failed.
    Error Log:
    {error_log}
    
    CURRENT SOURCE CODE:
    {files_str}
    
    Reflect on the error log and the source code. Perform a Root Cause Analysis before proposing a fix.
    Respond ONLY with this JSON schema:
    {{
        "root_cause_analysis": "Write a 2-sentence explanation of EXACTLY why the code failed according to the test logs.",
        "files_to_update": [
            {{
                "filepath": "path/to/file.ext",
                "instructions": "Detailed instructions on what exact lines to change to fix the error."
            }}
        ]
    }}
    """
    content = call_openrouter(model, sys_prompt, user_prompt, temperature=0.2)
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR"
    if not content: return None
    return extract_json(content, required_keys=["root_cause_analysis", "files_to_update"])

# ==========================================
# THE RELENTLESS EXECUTION LOOP
# ==========================================
def run_beast_cycle():
    log_event("========================================")
    log_event(" AGENT BEAST V6.1: RESILIENT ARCHITECT")
    log_event("========================================")
    
    memory = load_memory()
    
    while True: # Outer loop
        grid = NeuralGrid(memory)
        if not grid.models:
            log_event("Grid sync failed. Sleep 5m...")
            time.sleep(300)
            continue
            
        success = False
        project_state_file = os.path.join(PROJECTS_DIR, "active_project_state.json")
        
        project_state = {}
        if os.path.exists(project_state_file):
            try:
                with open(project_state_file, "r", encoding="utf-8") as f:
                    project_state = json.load(f)
                log_event("Found an active project state! Resuming from where we left off...")
            except: pass
            
        while not grid.is_depleted() and not success:
            # Specialization (Point 15)
            planner_model = grid.get_planner_model()
            coder_model = grid.get_coder_model()
            if not planner_model or not coder_model: break
            
            # STAGE 1: PLAN
            if not project_state.get("plan"):
                log_event(f"--- Assigning Planner Model: {planner_model} ---")
                trends = fetch_trends()
                plan = plan_project(planner_model, trends, memory)
                
                if plan == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during planning.")
                    exit(1)
                if plan == "SERVER_ERROR":
                    grid.mark_unhealthy(planner_model, "SERVER_ERROR")
                    continue
                if not plan or "files_to_generate" not in plan:
                    log_event(f"Architect {planner_model} failed planning phase.")
                    grid.mark_unhealthy(planner_model, "BAD_PLAN") 
                    continue
                    
                # Plan Critique
                plan = critique_plan(planner_model, plan)
                    
                project_state["plan"] = plan
                project_state["files_created"] = []
                with open(project_state_file, "w", encoding="utf-8") as f: 
                    json.dump(project_state, f, indent=4)
                
            plan = project_state["plan"]
            project_name = plan.get("project_name", f"AI_Project_{int(time.time())}")
            project_dir = os.path.join(PROJECTS_DIR, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            log_event(f"Working on '{project_name}'...")
            log_event(f"--- Assigning Coder Model: {coder_model} ---")
            
            # STAGE 2: GENERATE FILES
            generation_failed = False
            for f_info in plan["files_to_generate"]:
                filepath = f_info.get("filepath")
                instructions = f_info.get("instructions", "")
                if not filepath or filepath in project_state["files_created"]:
                    continue 
                    
                blueprint_context = "\n".join(project_state.get("blueprint", []))
                content = generate_file_chunked(coder_model, project_name, plan.get("vision", ""), filepath, instructions, blueprint_context)
                
                if content == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during coding.")
                    exit(1)
                if content in ["SERVER_ERROR", "ERROR_TRUNCATED"] or not content:
                    generation_failed = True
                    grid.mark_unhealthy(coder_model, "GENERATION_FAIL")
                    break
                
                # Path security (Point 10)
                full_path = os.path.abspath(os.path.join(project_dir, filepath))
                if not full_path.startswith(os.path.abspath(project_dir)):
                    log_event(f"Security: skipping path outside project dir: {full_path}")
                    continue
                if os.path.isdir(full_path):
                    log_event(f"Skipping invalid directory filepath: {full_path}")
                    continue
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                    
                # Local Linting (Point 3)
                if filepath.endswith(".py"):
                    try:
                        lint_res = subprocess.run(["python", "-m", "py_compile", full_path], capture_output=True, text=True)
                        if lint_res.returncode != 0:
                            log_event(f"Local Lint Failed for {filepath}. Triggering internal fast-fix.")
                            # We could do a fast-fix here, but for now we mark generation failed to force a new attempt
                            generation_failed = True
                            grid.mark_unhealthy(coder_model, "LINT_FAIL")
                            break
                    except: pass
                
                project_state["files_created"].append(filepath)
                if "blueprint" not in project_state:
                    project_state["blueprint"] = []
                project_state["blueprint"].append(extract_signatures(filepath, content))
                with open(project_state_file, "w", encoding="utf-8") as f: 
                    json.dump(project_state, f, indent=4)
                log_event(f"Saved {filepath} ({len(content)} bytes).")
                
            if generation_failed:
                log_event(f"Generation interrupted. Model {coder_model} swapped. Progress saved.")
                continue 
                
            # Stage 2b: Dependency Check
            if not check_dependencies(project_state["files_created"], project_dir):
                log_event("Hallucinated dependencies found. Swapping model.")
                grid.mark_unhealthy(coder_model, "HALLUCINATED_DEPS")
                continue
                
            # STAGE 3: TESTS & FIX LOOP
            files_created = project_state["files_created"]
            test_script = generate_tests(coder_model, project_name, files_created)
            if test_script == "QUOTA_EXHAUSTED": exit(1)
            if test_script == "SERVER_ERROR" or not test_script:
                grid.mark_unhealthy(coder_model, "TEST_GEN_FAIL")
                continue
                
            script_path = os.path.join(project_dir, "setup_and_test.bat")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(test_script.strip())
                
            fix_attempts = 0
            while fix_attempts < 3:
                log_event(f"Validating {project_name} (Attempt {fix_attempts+1}/3)...")
                try:
                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                             cwd=project_dir, capture_output=True, text=True, timeout=120)
                    
                    # Point 12: Real evidence
                    output_combined = result.stdout + result.stderr
                    has_evidence = "passed" in output_combined.lower() or "ok" in output_combined.lower() or "success" in output_combined.lower()
                    
                    if result.returncode == 0 and has_evidence:
                        success = True
                        break 
                    else:
                        log_event(f"FAILURE. Syntax/Test error. Asking SAME model to fix...")
                        error_log = f"STDOUT:\n{result.stdout[-1500:]}\nSTDERR:\n{result.stderr[-1500:]}"
                        if result.returncode == 0 and not has_evidence:
                            error_log += "\nScript exited 0 but no 'passed' or 'ok' evidence was found in the output. Did the tests actually run?"
                        
                        fix_plan = fix_error(coder_model, project_dir, files_created, error_log)
                        if fix_plan == "QUOTA_EXHAUSTED": exit(1)
                        if fix_plan == "SERVER_ERROR" or not fix_plan or "files_to_update" not in fix_plan:
                            log_event("Model failed to provide a fix plan. Aborting fix attempt.")
                            break
                            
                        blueprint_context = "\n".join(project_state.get("blueprint", []))
                        for f_info in fix_plan["files_to_update"]:
                            filepath = f_info.get("filepath")
                            instructions = f_info.get("instructions", "")
                            if not filepath: continue
                            
                            log_event(f"Applying fix to {filepath}...")
                            content = generate_file_chunked(coder_model, project_name, "Fixing errors", filepath, instructions, blueprint_context)
                            if content and content not in ["SERVER_ERROR", "ERROR_TRUNCATED", "QUOTA_EXHAUSTED"]:
                                full_path = os.path.abspath(os.path.join(project_dir, filepath))
                                if not full_path.startswith(os.path.abspath(project_dir)): continue
                                if os.path.isdir(full_path): continue
                                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write(content.strip())
                        fix_attempts += 1
                except subprocess.TimeoutExpired:
                    log_event("Test script timed out. Likely a hanging process.")
                    break
                    
            if success:
                grid.mark_healthy(coder_model)
                log_event(f"VICTORY ACHIEVED! Code is fully working.")
                memory["score"] += 1
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": coder_model})
                
                # Point 14: Fix memory loop
                if plan.get("lessons_learned"):
                    memory["lessons_learned"].append(plan.get("lessons_learned"))
                    memory["lessons_learned"] = memory["lessons_learned"][-20:] # cap size
                memory["past_projects"].append(project_name)
                memory["past_projects"] = memory["past_projects"][-20:]
                
                save_memory(memory)
                
                # Push
                try:
                    # Point 10: confirm .env in gitignore
                    gitignore_path = os.path.join(REPO_ROOT, ".gitignore")
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n.venv/\nvenv/\n__pycache__/\nnode_modules/\n*.log\n.env\n")
                        
                    subprocess.run(["git", "rm", "-r", "--cached", ".venv"], check=False, cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "rm", "-r", "--cached", "venv"], check=False, cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "rm", "--cached", ".env"], check=False, cwd=REPO_ROOT, capture_output=True)
                    
                    subprocess.run(["git", "add", "."], check=True, cwd=REPO_ROOT)
                    
                    action_desc = plan.get("commit_message", "autonomous module update")
                    commit_msg = f"feat({project_name}): {action_desc}"
                    
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=REPO_ROOT)
                    
                    # Point 11: Git Pull Rebase dynamic branch
                    branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=True, cwd=REPO_ROOT, capture_output=True, text=True)
                    branch_name = branch_res.stdout.strip() or "main"
                    subprocess.run(["git", "pull", "origin", branch_name, "--rebase"], check=True, cwd=REPO_ROOT)
                    
                    subprocess.run(["git", "push", "origin", branch_name], check=True, cwd=REPO_ROOT)
                    log_event(f"Code successfully pushed to GitHub '{branch_name}' with message: '{commit_msg}'")
                except Exception as e:
                    log_event(f"Git push failed: {e}")
                    
                if os.path.exists(project_state_file):
                    os.remove(project_state_file)
                    
                log_event("Project successfully completed. Exiting script as requested.")
                return 
                
            else:
                log_event(f"Model {coder_model} failed to fix the project after 3 attempts. Rotating model...")
                grid.mark_unhealthy(coder_model, "FIX_LOOP_FAIL")
                time.sleep(2)

        if not success:
            log_event("ENTIRE NEURAL GRID CONGESTED. Exiting.")
            return

if __name__ == "__main__":
    run_beast_cycle()
