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
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

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
- On Windows, always close file descriptors returned by tempfile.mkstemp() (e.g. os.close(fd)) immediately to prevent [WinError 32] PermissionError on deletion.
"""

os.makedirs(PROJECTS_DIR, exist_ok=True)

def log_event(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

# ==========================================
# QUOTA & LIMITS
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
    if quota["count"] >= 50: # Free tier limit
        log_event("DAILY QUOTA EXHAUSTED (50 requests). Exiting.")
        exit(1)

# ==========================================
# DYNAMIC NEURAL GRID
# ==========================================
def fetch_live_free_models():
    def inject_qwen(models):
        qwen_models = ["qwen-max", "qwen-plus", "qwen3-coder-plus", "qwen3-coder-flash"]
        for qm in reversed(qwen_models):
            if qm not in models:
                models.insert(0, qm)
        return models

    if os.path.exists(MODELS_CACHE_FILE):
        if time.time() - os.path.getmtime(MODELS_CACHE_FILE) < 3600: 
            try:
                with open(MODELS_CACHE_FILE, "r") as f:
                    return inject_qwen(json.load(f))
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
            return inject_qwen([])
        log_event(f"Discovery complete. Found {len(free_models)} free architects online.")
        
        with open(MODELS_CACHE_FILE, "w") as f:
            json.dump(free_models, f)
            
        return inject_qwen(free_models)
    except Exception as e:
        log_event(f"Failed to sync with grid: {e}")
        return inject_qwen([])

class NeuralGrid:
    def __init__(self, memory):
        self.memory = memory
        self.models = fetch_live_free_models()
        self.unhealthy_models = set()
        
    def _init_metrics(self, model, role):
        target_dict = f"{role}_ratings" if role else "model_ratings"
        if target_dict not in self.memory: self.memory[target_dict] = {}
        if model not in self.memory[target_dict]:
            if role == "coder":
                self.memory[target_dict][model] = {"files_generated": 0, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
            else:
                self.memory[target_dict][model] = {"plans_created": 0, "critique_survivals": 0, "test_stages_reached": 0}

    def get_planner_model(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        def score(m):
            if m.startswith("qwen"): return 1000.0
            metrics = self.memory.get("planner_ratings", {}).get(m, {"plans_created": 0, "critique_survivals": 0, "test_stages_reached": 0})
            if isinstance(metrics, int): metrics = {"plans_created": metrics, "critique_survivals": 0, "test_stages_reached": 0}
            plans = max(metrics.get("plans_created", 1), 1)
            return (metrics.get("critique_survivals", 0) / plans) + (metrics.get("test_stages_reached", 0) / plans) + random.uniform(0, 0.2)
        available.sort(key=score, reverse=True)
        return available[0]
        
    def get_coder_model(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        def score(m):
            if m.startswith("qwen"): return 1000.0
            metrics = self.memory.get("coder_ratings", {}).get(m, {"files_generated": 0, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0})
            if isinstance(metrics, int): metrics = {"files_generated": metrics, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
            files = max(metrics.get("files_generated", 1), 1)
            fixes = max(metrics.get("fix_attempts", 1), 1)
            lint_rate = metrics.get("lint_passes", 0) / files
            fix_rate = metrics.get("fix_successes", 0) / fixes
            return (lint_rate * 0.4) + (fix_rate * 0.6) + random.uniform(0, 0.2)
        available.sort(key=score, reverse=True)
        return available[0]
        
    def get_fallback_models(self, role="coder"):
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return []
        def score(m):
            if role == "planner":
                metrics = self.memory.get("planner_ratings", {}).get(m, {"plans_created": 0, "critique_survivals": 0, "test_stages_reached": 0})
                if isinstance(metrics, int): metrics = {"plans_created": metrics, "critique_survivals": 0, "test_stages_reached": 0}
                plans = max(metrics.get("plans_created", 1), 1)
                return (metrics.get("critique_survivals", 0) / plans) + (metrics.get("test_stages_reached", 0) / plans) + random.uniform(0, 0.2)
            else:
                metrics = self.memory.get("coder_ratings", {}).get(m, {"files_generated": 0, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0})
                if isinstance(metrics, int): metrics = {"files_generated": metrics, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
                files = max(metrics.get("files_generated", 1), 1)
                fixes = max(metrics.get("fix_attempts", 1), 1)
                lint_rate = metrics.get("lint_passes", 0) / files
                fix_rate = metrics.get("fix_successes", 0) / fixes
                return (lint_rate * 0.4) + (fix_rate * 0.6) + random.uniform(0, 0.2)
        available.sort(key=score, reverse=True)
        return available[1:3] if len(available) > 1 else []

    def record_metric(self, model, role, metric, value=1):
        self._init_metrics(model, role)
        target_dict = f"{role}_ratings" if role else "model_ratings"
        if isinstance(self.memory[target_dict][model], int):
            if role == "coder":
                self.memory[target_dict][model] = {"files_generated": self.memory[target_dict][model], "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
            else:
                self.memory[target_dict][model] = {"plans_created": self.memory[target_dict][model], "critique_survivals": 0, "test_stages_reached": 0}
        self.memory[target_dict][model][metric] = self.memory[target_dict][model].get(metric, 0) + value
        save_memory(self.memory)

    def mark_unhealthy(self, model, reason="error", role=None):
        if reason == "QUOTA_EXHAUSTED":
            log_event("Account Quota reached. Halting.")
            exit(1)
        log_event(f"Marking {model} as UNHEALTHY ({reason}). Rotating to next model...")
        self.unhealthy_models.add(model)

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
                if "planner_ratings" not in data: data["planner_ratings"] = {}
                if "coder_ratings" not in data: data["coder_ratings"] = {}
                
                # Migrate old integers to dicts
                for k, v in data["planner_ratings"].items():
                    if isinstance(v, int): data["planner_ratings"][k] = {"plans_created": v, "critique_survivals": 0, "test_stages_reached": 0}
                for k, v in data["coder_ratings"].items():
                    if isinstance(v, int): data["coder_ratings"][k] = {"files_generated": v, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}

                if "past_projects" not in data: data["past_projects"] = []
                if "lessons_learned" not in data: data["lessons_learned"] = []
                return data
        except Exception: pass
    return {"score": 0, "history": [], "model_ratings": {}, "planner_ratings": {}, "coder_ratings": {}, "past_projects": [], "lessons_learned": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def fetch_hn_story(sid):
    try:
        return requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
    except Exception:
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
    except Exception: return "Focus: AI-driven autonomous systems."

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

def call_openrouter(models_list, sys_prompt, user_prompt, temperature=0.4, max_tokens=8000):
    """
    Leverages OpenRouter's native `models` array for fallback failover, 
    and plugins for response-healing and context-compression.
    """
    for attempt in range(2):
        enforce_rate_limit()
        if attempt == 0: increment_quota() 
        
        target_model = models_list[0]
        is_qwen = target_model.startswith("qwen")
        
        if is_qwen and QWEN_API_KEY:
            url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
            headers = {"Authorization": f"Bearer {QWEN_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": target_model,
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        else:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "models": models_list,
                "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "plugins": [{"id": "response-healing"}, {"id": "context-compression"}]
            }
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            res_data = response.json()
            
            actual_model = res_data.get("model", target_model)
            
            usage = res_data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            log_event(f"API Call ({actual_model}) used {total_tokens} tokens.")
            
            if "error" in res_data:
                err_msg = res_data['error'].get('message', 'Unknown')
                err_code = res_data['error'].get('code', response.status_code)
                log_event(f"API Error: {err_msg} (Code: {err_code})")
                
                if response.status_code == 429:
                    if is_qwen:
                        log_event("Qwen Rate Limit. Marking model UNHEALTHY to fallback to OpenRouter.")
                        return "SERVER_ERROR", actual_model
                    elif "limit reached" in err_msg.lower() or "credits" in err_msg.lower() or "free-models-per-day" in err_msg.lower():
                        return "QUOTA_EXHAUSTED", actual_model
                
                if attempt == 0:
                    log_event("Transient error across all models. Retrying array once in 5s...")
                    time.sleep(5)
                    continue
                return "SERVER_ERROR", actual_model
            
            return res_data["choices"][0]["message"]["content"], actual_model
        except Exception as e:
            log_event(f"API Request Failed: {e}")
            if attempt == 0:
                log_event("Network error. Retrying array once in 5s...")
                time.sleep(5)
                continue
            return "SERVER_ERROR", models_list[0]

def extract_json(content, required_keys=None):
    if not content: return None
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
        except Exception: pass
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
    except Exception:
        return f"File: {filepath} (Syntax error or unparseable)"
        
def apply_search_replace(file_content, search_block, replace_block):
    """Fuzzy Line-Window Matcher for robust string replacement"""
    import difflib
    search_block = strip_markdown(search_block).replace('\r\n', '\n')
    replace_block = strip_markdown(replace_block).replace('\r\n', '\n')
    file_content_norm = file_content.replace('\r\n', '\n')
    
    # Exact Match
    if search_block in file_content_norm:
        return file_content_norm.replace(search_block, replace_block)
        
    # Fuzzy Line Window Match
    search_lines = [line.strip() for line in search_block.split('\n') if line.strip()]
    if not search_lines:
        return "ERROR_SEARCH_NOT_FOUND"
        
    file_lines = file_content_norm.split('\n')
    file_lines_stripped = [line.strip() for line in file_lines]
    
    search_len = len(search_lines)
    file_len = len(file_lines_stripped)
    
    for i in range(file_len - search_len + 1):
        match = True
        for j in range(search_len):
            if file_lines_stripped[i+j] != search_lines[j]:
                match = False
                break
        if match:
            new_lines = file_lines[:i] + replace_block.split('\n') + file_lines[i+search_len:]
            return '\n'.join(new_lines)
            
    # difflib fallback
    best_ratio = 0
    best_idx = -1
    for i in range(file_len - search_len + 1):
        block = file_lines_stripped[i:i+search_len]
        ratio = difflib.SequenceMatcher(None, block, search_lines).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i
            
    if best_ratio > 0.8:
        new_lines = file_lines[:best_idx] + replace_block.split('\n') + file_lines[best_idx+search_len:]
        return '\n'.join(new_lines)
            
    return "ERROR_SEARCH_NOT_FOUND"

# ==========================================
# STAGES
# ==========================================
def plan_project(models, trends, memory, error_context=None):
    import sys
    log_event(f"Stage 1: Planning Project with Architect {models[0]}...")
    sys_prompt = "You are the Lead AGI Architect. Respond ONLY with valid JSON."
    retry_guidance = f"\nPREVIOUS RUN FAILED. FIX ERRORS:\n{error_context}" if error_context else ""
    past_projects = "\n".join(memory.get("past_projects", [])[-10:])
    lessons_learned = "\n".join(memory.get("lessons_learned", [])[-10:])
    
    user_prompt = f"""
    You are operating under the Get Shit Done (GSD) autonomous agent framework.
    Design a new, innovative, fully functional software application. 
    
    PROBLEM SELECTION (Agentic Gaps):
    Do not build generic CRUD apps. Build "Specialist Agents" or solve specific developer/agentic gaps.
    
    CRITICAL SCOPE LIMITS for Free LLMs:
    - You must keep the architecture extremely compact (maximum 8 files).
    - Avoid 'enterprise boilerplate'. Pack the complexity into dense, robust files.
    - Do NOT design things requiring paid external APIs or massive datasets.
    
    SPEC-DRIVEN DEVELOPMENT & DETERMINISTIC VALIDATION:
    1. Your plan must include explicit `interface_contracts` declaring function signatures for cross-file dependencies.
    2. Your plan must include a strict unit test suite (`test_main.py` or similar). The tests MUST import and use the actual generated modules. Do NOT create mock or stub classes for the core logic. The code MUST pass its own tests.
    3. Include a `.gitignore` to ignore venv, __pycache__, .env.
    4. Include a `README.md` explaining the architecture.
    5. CRITICAL: Only Python projects are supported. Do NOT create Node.js/JavaScript projects.
    6. CRITICAL: MUST be cross-platform. Target OS: {sys.platform}. Do NOT use `curses` or other OS-specific libraries not available on this platform.
    7. CRITICAL: Do NOT use heavy ML libraries like `tensorflow`, `torch`, `transformers`, or `numpy`. Stick to standard library or lightweight packages.
    8. CRITICAL TDD REQUIREMENT: Design Pure Functions and use Dependency Injection wherever possible. Decouple core logic from side-effects (e.g., file I/O, network requests, os.path.exists) so the code can be easily unit tested without complex mocks.
    
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
    content, actual_model = call_openrouter(models, sys_prompt, user_prompt, temperature=0.8) 
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return content, actual_model
    if not content: return None, actual_model
    return extract_json(content, required_keys=["project_name", "files_to_generate", "lessons_learned", "interface_contracts"]), actual_model

def validate_plan(plan):
    if not plan: return False
    files = plan.get("files_to_generate", [])
    if not files or len(files) > 8: 
        log_event("Plan Validation Failed: File count must be between 1 and 8.")
        return False
    has_test = any("test" in f.get("filepath", "").lower() for f in files)
    if not has_test:
        log_event("Plan Validation Failed: No test file detected.")
        return False
    contracts = plan.get("interface_contracts", "")
    if not contracts or len(str(contracts)) < 10:
        log_event("Plan Validation Failed: Missing or empty interface_contracts.")
        return False
    return True

def critique_plan(models, plan):
    log_event("Stage 1b: Critiquing Plan...")
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
    content, actual_model = call_openrouter(models, sys_prompt, user_prompt, temperature=0.2)
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return plan, actual_model 
    critique = extract_json(content, required_keys=["files_to_generate"])
    return (critique if critique else plan), actual_model

def check_dependencies(file_list, project_dir):
    log_event("Sanity checking dependencies...")
    req_path = os.path.join(project_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            pkgs = [line.split("==")[0].strip() for line in f if line.strip() and not line.startswith("#")]
        for pkg in pkgs:
            if not pkg: continue
            try:
                res = requests.get(f"https://pypi.org/pypi/{pkg}/json", timeout=3)
                if res.status_code == 404:
                    log_event(f"WARNING: Hallucinated package detected: {pkg}")
                    return False
            except: pass
    return True

def generate_file_chunked(models, project_name, vision, filepath, instructions, project_blueprint=""):
    log_event(f"Stage 2: Generating File -> {filepath} (Chunked)...")
    
    # Keep blueprint at a reasonable size but DON'T destroy memory context
    # The memory injection adds full file contents — we need those for cross-file consistency
    if len(project_blueprint) > 12000:
        project_blueprint = project_blueprint[-12000:]  # Keep last 12k chars
    
    sys_prompt = "You are an Expert Software Engineer operating under the GSD framework. You write clean, robust code."
    if "gitignore" in filepath.lower():
        sys_prompt += "\nYou are writing a .gitignore file. Output ONLY a short, standard Python .gitignore (max 20 lines)."
        instructions = "Write a minimal Python .gitignore: .venv/, venv/, __pycache__/, *.pyc, .env, node_modules/, *.egg-info/, dist/, build/. Nothing else. Max 20 lines."
    elif "readme" in filepath.lower():
        instructions += "\nCRITICAL: Include a 'How it Works' section."
    elif "test" in filepath.lower():
        instructions += "\nCRITICAL: Your tests MUST import the actual classes and functions from the generated modules. Use the EXACT same parameter names and class signatures as shown in the previously generated files. Do NOT declare stub classes or mocks for the code you are testing. Do NOT write assertions that expect specific serialized output from functions that were generated as empty placeholders or stubs. Double-check method signatures across files: do not call an instance method as a class method, and respect type hints for file paths vs file-like objects."
        
    blueprint_section = f"\n    ROLLING BLUEPRINT:\n    {project_blueprint}\n" if project_blueprint else ""
    
    top_directive = f"""
CRITICAL DIRECTIVE: 
Task: Write ONLY the exact contents for the file: `{filepath}`.
CRITICAL RULE: When you are COMPLETELY FINISHED writing the entire file, append the exact token `[EOF]` at the very end. Do NOT use `[EOF]` until the entire file is complete.
"""

    base_prompt = f"""{top_directive}
Project: {project_name}
Vision: {vision}
{blueprint_section}
Instructions: {instructions}

STYLE GUIDE:
{STYLE_GUIDE}

RULES:
1. Write proper, lengthy production code. Ensure it integrates correctly with the Rolling Blueprint.
2. Return ONLY raw file contents. No explanations.
3. Do NOT wrap your output in markdown code blocks. Just plain text.

{top_directive}
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
            
        content, actual_model = call_openrouter(models, sys_prompt, user_prompt, temperature=0.1) 
        if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]:
            return content, actual_model
        if not content:
            break
            
        content = strip_markdown(content)
        
        if "[EOF]" in content:
            full_content += content.replace("[EOF]", "")
            return strip_markdown(full_content), actual_model
        else:
            full_content += content
            chunks_completed += 1
            
    log_event(f"Failed to generate full file {filepath} within {max_chunks} chunks.")
    return "ERROR_TRUNCATED", models[0]

def generate_tests(models, project_name, file_list, project_dir):
    log_event(f"Stage 3: Generating Integration Script for {project_name}...")
    
    # Check if requirements.txt exists and read it
    req_path = os.path.join(project_dir, "requirements.txt")
    req_content = ""
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            req_content = f.read().strip()
    
    req_install = ""
    if req_content:
        req_install = "pip install -r requirements.txt"
    
    # Instead of asking the AI to generate a bat script (which wastes tokens and
    # often produces broken scripts), use a hardcoded reliable template.
    bat_script = f"""@echo off
setlocal

cd /d "%~dp0"

if exist .venv (
    echo Activating existing venv...
    call .venv\\Scripts\\activate.bat
) else (
    echo Creating venv...
    python -m venv .venv
    call .venv\\Scripts\\activate.bat
)

python -m pip install --quiet --upgrade pip
if "%req_install%" NEQ "" (
    %req_install%
    if %ERRORLEVEL% NEQ 0 (
        echo PIP INSTALL FAILED
        exit /b %ERRORLEVEL%
    )
)
python -m pip install --quiet pytest pytest-json-report
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo Running tests...
python -m pytest --json-report --json-report-file=report.json -v
set EXITCODE=%ERRORLEVEL%

exit /b %EXITCODE%
"""
    log_event("Using hardcoded reliable test script template (0 tokens used).")
    return bat_script.strip(), "hardcoded-template"

def fix_error(models, project_dir, files_to_check, error_log):
    log_event("Stage 4: Identifying Fixes (Agentless Localization)...")
    
    file_contents = {}
    for fname in files_to_check:
        full_path = os.path.join(project_dir, fname)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
                file_contents[fname] = "\n".join(numbered_lines)[:15000] # Cap size per file
                
    files_str = "\n".join([f"--- {k} ---\n{v}\n" for k, v in file_contents.items()])
                
    sys_prompt = "You are a Debugger operating under the GSD framework. You fix code and respond ONLY with valid JSON."
    user_prompt = f"""
    The test script failed.
    Error Log:
    {error_log}
    
    CURRENT SOURCE CODE OF SUSPECTED FILES:
    {files_str}
    
    Perform a Root Cause Analysis. 
    CRITICAL: Do NOT blindly trust the test suite. If the test asserts something factually incorrect, specify that the TEST FILE needs fixing instead of breaking the implementation logic to match a bad test.
    
    Then, specify EXACTLY which lines to replace to fix the code. Use line numbers corresponding to the source code provided above. You MUST provide the complete drop-in replacement lines. Do NOT rewrite the entire file.
    
    Respond ONLY with this JSON schema:
    {{
        "root_cause_analysis": "Write a 2-sentence explanation of EXACTLY why the code failed.",
        "files_to_update": [
            {{
                "filepath": "path/to/file.ext",
                "start_line": 40,
                "end_line": 45,
                "replacement_code": "    exact replacement code here\\n    matching indentation\\n"
            }}
        ]
    }}
    """
    content, actual_model = call_openrouter(models, sys_prompt, user_prompt, temperature=0.2)
    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return content, actual_model
    if not content: return None, actual_model
    return extract_json(content, required_keys=["root_cause_analysis", "files_to_update"]), actual_model

# ==========================================
# THE RELENTLESS EXECUTION LOOP
# ==========================================
def run_beast_cycle():
    log_event("========================================")
    log_event(" AGENT BEAST V6.5: SOTA SCAFFOLD")
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
            planner_model = grid.get_planner_model()
            coder_model = grid.get_coder_model()
            if not planner_model or not coder_model: break
            
            planner_fallback = [planner_model] + grid.get_fallback_models("planner")
            coder_fallback = [coder_model] + grid.get_fallback_models("coder")
            
            actual_coder = coder_model
            actual_planner = planner_model
            # STAGE 1: PLAN
            if not project_state.get("plan"):
                log_event(f"--- Assigning Planner Model: {planner_model} ---")
                trends = fetch_trends()
                plan, actual_planner = plan_project(planner_fallback, trends, memory)
                
                if plan == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during planning.")
                    exit(1)
                if plan == "SERVER_ERROR":
                    grid.mark_unhealthy(actual_planner, "SERVER_ERROR", "planner")
                    continue
                if not plan or "files_to_generate" not in plan:
                    log_event(f"Architect {actual_planner} failed planning phase.")
                    grid.mark_unhealthy(actual_planner, "BAD_PLAN", "planner") 
                    continue
                    
                # Plan Critique
                if not validate_plan(plan):
                    log_event("Architecture rejected by programmatic validation.")
                    grid.mark_unhealthy(actual_planner, "INVALID_PLAN", "planner")
                    project_state["plan"] = None
                    continue

                grid.record_metric(actual_planner, "planner", "plans_created")
                
                # Plan Critique
                plan_copy = json.dumps(plan)
                plan, actual_critic = critique_plan(planner_fallback, plan)
                if json.dumps(plan) == plan_copy:
                    grid.record_metric(actual_planner, "planner", "critique_survivals")
                    
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
                # Short-Term Memory Injection
                is_test_file = "test" in filepath.lower()
                memory_blocks = []
                total_context_len = 0
                fallback_to_blueprint = False
                
                for created_file in project_state.get("files_created", []):
                    created_path = os.path.join(project_dir, created_file)
                    if os.path.exists(created_path):
                        with open(created_path, "r", encoding="utf-8") as f:
                            c = f.read()
                            if is_test_file:
                                total_context_len += len(c)
                                if total_context_len > 12000:
                                    fallback_to_blueprint = True
                                    break
                                memory_blocks.append(f"--- {created_file} ---\n{c}\n")
                            else:
                                if len(c) > 2000: c = c[:2000] + "\n...[truncated to save tokens]"
                                memory_blocks.append(f"--- {created_file} ---\n{c}\n")
                
                if is_test_file and fallback_to_blueprint:
                    log_event("Full source exceeded 12k chars. Falling back to interface blueprint for test context.")
                    context_memory_str = "" # Fallback to blueprint only
                else:
                    context_memory_str = "PREVIOUSLY GENERATED FILES IN THIS PROJECT:\n" + "\n".join(memory_blocks) if memory_blocks else ""
                
                blueprint_context = "\n".join(project_state.get("blueprint", []))
                if context_memory_str:
                    blueprint_context += "\n\n" + context_memory_str
                    
                content, actual_coder = generate_file_chunked(coder_fallback, project_name, plan.get("vision", ""), filepath, instructions, blueprint_context)
                if content == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during coding.")
                    exit(1)
                if content in ["SERVER_ERROR", "ERROR_TRUNCATED"] or not content:
                    generation_failed = True
                    grid.mark_unhealthy(actual_coder, "GENERATION_FAIL", "coder")
                    break
                
                full_path = os.path.abspath(os.path.join(project_dir, filepath))
                if os.path.commonpath([full_path, os.path.abspath(project_dir)]) != os.path.abspath(project_dir):
                    log_event(f"Security: skipping path outside project dir: {full_path}")
                    continue
                if os.path.isdir(full_path):
                    log_event(f"Skipping invalid directory filepath: {full_path}")
                    continue
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                    
                # Local Linting
                if filepath.endswith(".py"):
                    try:
                        lint_res = subprocess.run(["python", "-m", "py_compile", full_path], capture_output=True, text=True)
                        if lint_res.returncode == 0:
                            grid.record_metric(actual_coder, "coder", "lint_passes")
                        else:
                            log_event(f"Local Lint Failed for {filepath}. Attempting inline retry...")
                            error_msg = lint_res.stderr if lint_res.stderr else lint_res.stdout
                            retry_instructions = instructions + f"\n\nCRITICAL FIX REQUIRED: Your previous attempt had a syntax error. Fix it and output the entire file again.\nError:\n{error_msg}"
                            content, actual_coder = generate_file_chunked(coder_fallback, project_name, plan.get("vision", ""), filepath, retry_instructions, blueprint_context)
                            
                            if content and content not in ["SERVER_ERROR", "ERROR_TRUNCATED", "QUOTA_EXHAUSTED"]:
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write(content.strip())
                                lint_res_2 = subprocess.run(["python", "-m", "py_compile", full_path], capture_output=True, text=True)
                                if lint_res_2.returncode == 0:
                                    log_event(f"Inline retry successful for {filepath}.")
                                    grid.record_metric(actual_coder, "coder", "lint_passes")
                                else:
                                    log_event(f"Inline retry failed. Marking coder unhealthy and rotating...")
                                    generation_failed = True
                                    grid.mark_unhealthy(actual_coder, "LINT_FAIL", "coder")
                                    break
                            else:
                                log_event(f"Inline retry generation failed. Marking coder unhealthy and rotating...")
                                generation_failed = True
                                grid.mark_unhealthy(actual_coder, "LINT_FAIL", "coder")
                                break
                    except Exception: pass
                
                grid.record_metric(actual_coder, "coder", "files_generated")
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
                grid.mark_unhealthy(actual_coder, "HALLUCINATED_DEPS", "coder")
                continue
                
            # STAGE 3: TESTS & FIX LOOP
            grid.record_metric(actual_planner, "planner", "test_stages_reached")
            
            files_created = project_state["files_created"]
            test_script, actual_tester = generate_tests(coder_fallback, project_name, files_created, project_dir)
            if test_script == "QUOTA_EXHAUSTED": exit(1)
            if test_script == "SERVER_ERROR" or not test_script:
                grid.mark_unhealthy(actual_tester, "TEST_GEN_FAIL", "coder")
                continue
            
            # Sanity check: bat script must look real (not an error string)
            if len(test_script.strip()) < 30 or "echo" not in test_script.lower():
                log_event(f"WARNING: Generated test script looks invalid ({len(test_script)} bytes). Skipping.")
                grid.mark_unhealthy(actual_tester, "BAD_TEST_SCRIPT", "coder")
                continue
                
            script_path = os.path.join(project_dir, "setup_and_test.bat")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(test_script.strip())
                
            fix_attempts = 0
            while fix_attempts < 8:
                log_event(f"Validating {project_name} (Attempt {fix_attempts+1}/8)...")
                try:
                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                             cwd=project_dir, capture_output=True, text=True, timeout=120)
                    
                    output_combined = result.stdout + result.stderr
                    
                    report_path = os.path.join(project_dir, "report.json")
                    if os.path.exists(report_path):
                        try:
                            import json as pyjson
                            with open(report_path, "r", encoding="utf-8") as f:
                                report_data = pyjson.load(f)
                                summary = report_data.get("summary", {})
                                passed = summary.get("passed", 0)
                                failed = summary.get("failed", 0)
                                errors = summary.get("error", 0)
                                if passed > 0 and failed == 0 and errors == 0:
                                    success = True
                        except Exception: pass
                    
                    if success:
                        break 
                    else:
                        if fix_attempts >= 7:
                            log_event("FAILURE. Maximum fix attempts reached. Proceeding to Sunk Cost Protocol...")
                            fix_attempts += 1
                            break
                            
                        log_event("FAILURE. Syntax/Test error. Asking SAME model to patch...")
                        error_log = f"STDOUT:\n{result.stdout[-1500:]}\nSTDERR:\n{result.stderr[-1500:]}"
                        if not os.path.exists(report_path):
                            error_log += "\nCRITICAL: `report.json` was NOT generated. Did pytest actually run?"
                        
                        # Agentless Localization
                        crashing_files = set()
                        for fname in files_created:
                            if fname in error_log:
                                crashing_files.add(fname)
                        if not crashing_files:
                            crashing_files = set(files_created)
                            
                        fix_plan, actual_fixer = fix_error(coder_fallback, project_dir, list(crashing_files), error_log)
                        if fix_plan == "QUOTA_EXHAUSTED": exit(1)
                        if fix_plan == "SERVER_ERROR" or not fix_plan or "files_to_update" not in fix_plan:
                            log_event("Model failed to provide a valid fix plan.")
                            fix_attempts += 1
                            grid.mark_unhealthy(actual_fixer, "BAD_FIX_PLAN", "coder")
                            continue
                            
                        for f_info in fix_plan.get("files_to_update", []):
                            filepath = f_info.get("filepath")
                            start_line = f_info.get("start_line")
                            end_line = f_info.get("end_line")
                            replacement_code = f_info.get("replacement_code")
                            if not filepath or not start_line or not end_line or replacement_code is None: continue
                            
                            full_path = os.path.abspath(os.path.join(project_dir, filepath))
                            if os.path.commonpath([full_path, os.path.abspath(project_dir)]) != os.path.abspath(project_dir): continue
                            if not os.path.exists(full_path): continue
                            
                            log_event(f"Applying LINE NUMBER patch to {filepath} ({start_line} to {end_line})...")
                            
                            with open(full_path, "r", encoding="utf-8") as f:
                                lines = f.read().splitlines()
                                
                            try:
                                s_idx = int(start_line) - 1
                                e_idx = int(end_line)
                                if s_idx < 0: s_idx = 0
                                
                                new_lines = replacement_code.splitlines()
                                patched_lines = lines[:s_idx] + new_lines + lines[e_idx:]
                                
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write("\n".join(patched_lines) + "\n")
                                log_event(f"Successfully patched {filepath}.")
                            except Exception as e:
                                log_event(f"Failed to apply patch to {filepath}: {e}")
                                    
                        fix_attempts += 1
                        grid.record_metric(actual_fixer, "coder", "fix_attempts")
                except subprocess.TimeoutExpired:
                    log_event("Test script timed out. Likely a hanging process.")
                    break
                    
            if not success and fix_attempts >= 8:
                # Sunk Cost Protocol
                log_event("Sunk Cost Protocol Disabled. Keeping files and rotating model for further patching...")
                """
                for failing_file in crashing_files:
                    failing_instructions = ""
                    for fi in plan.get("files_to_generate", []):
                        if fi.get("filepath") == failing_file:
                            failing_instructions = fi.get("instructions", "")
                            break
                            
                    if failing_instructions:
                        blueprint_context = "\n".join(project_state.get("blueprint", [])[-5:])
                        log_event(f"Regenerating {failing_file} entirely...")
                        new_content, actual_sunk_coder = generate_file_chunked(coder_fallback, project_name, "Fixing errors by full rewrite", failing_file, failing_instructions + " THE PREVIOUS IMPLEMENTATION FAILED ENTIRELY. REWRITE IT DIFFERENTLY.", blueprint_context)
                        if new_content and new_content not in ["SERVER_ERROR", "ERROR_TRUNCATED", "QUOTA_EXHAUSTED"]:
                            full_path = os.path.abspath(os.path.join(project_dir, failing_file))
                            if os.path.commonpath([full_path, os.path.abspath(project_dir)]) == os.path.abspath(project_dir):
                                with open(full_path, "w", encoding="utf-8") as f:
                                    f.write(new_content.strip())
                """
                
                # Final check
                try:
                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], cwd=project_dir, capture_output=True, text=True, timeout=120)
                    report_path = os.path.join(project_dir, "report.json")
                    if os.path.exists(report_path):
                        import json as pyjson
                        with open(report_path, "r", encoding="utf-8") as f:
                            report_data = pyjson.load(f)
                            summary = report_data.get("summary", {})
                            if summary.get("passed", 0) > 0 and summary.get("failed", 0) == 0 and summary.get("error", 0) == 0:
                                success = True
                                log_event("Sunk Cost Protocol SUCCEEDED.")
                except Exception: pass
                
            if success:
                grid.record_metric(actual_coder, "coder", "fix_successes")
                    
                log_event("VICTORY ACHIEVED! Code is fully working.")
                memory["score"] += 1
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": actual_coder})
                
                if plan.get("lessons_learned"):
                    memory["lessons_learned"].append(plan.get("lessons_learned"))
                    memory["lessons_learned"] = memory["lessons_learned"][-20:]
                memory["past_projects"].append(project_name)
                memory["past_projects"] = memory["past_projects"][-20:]
                
                save_memory(memory)
                
                try:
                    gitignore_path = os.path.join(REPO_ROOT, ".gitignore")
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n.venv/\nvenv/\n__pycache__/\nnode_modules/\n*.log\n.env\n")
                        
                    subprocess.run(["git", "rm", "-r", "--cached", ".venv"], check=False, cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "rm", "-r", "--cached", "venv"], check=False, cwd=REPO_ROOT, capture_output=True)
                    subprocess.run(["git", "rm", "--cached", ".env"], check=False, cwd=REPO_ROOT, capture_output=True)
                    
                    subprocess.run(["git", "add", "."], check=True, cwd=REPO_ROOT)
                    
                    action_desc = plan.get("commit_message", "autonomous module update")
                    commit_msg = f"feat({project_name}): {action_desc}"
                    commit_msg = commit_msg.encode('ascii', 'ignore').decode('ascii')
                    
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=REPO_ROOT)
                    
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
                log_event(f"Model {actual_coder} failed to fix the project after Sunk Cost. Rotating model...")
                grid.mark_unhealthy(actual_coder, "FIX_LOOP_FAIL", "coder")
                time.sleep(2)

        if not success:
            log_event("ENTIRE NEURAL GRID CONGESTED. Exiting.")
            return

if __name__ == "__main__":
    run_beast_cycle()
