import sys

content = open('ai_brain.py', encoding='utf-8').read()

# 1. Update load_memory
content = content.replace('''                if "planner_ratings" not in data: data["planner_ratings"] = {}
                if "coder_ratings" not in data: data["coder_ratings"] = {}''',
'''                if "planner_ratings" not in data: data["planner_ratings"] = {}
                if "coder_ratings" not in data: data["coder_ratings"] = {}
                
                # Migrate old integers to dicts
                for k, v in data["planner_ratings"].items():
                    if isinstance(v, int): data["planner_ratings"][k] = {"plans_created": v, "critique_survivals": 0, "test_stages_reached": 0}
                for k, v in data["coder_ratings"].items():
                    if isinstance(v, int): data["coder_ratings"][k] = {"files_generated": v, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
''')

# 2. Rewrite NeuralGrid
content = content.replace('''    def get_planner_model(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        available.sort(key=lambda m: self.memory.get("planner_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)
        return available[0]
        
    def get_coder_model(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        if not available: return None
        available.sort(key=lambda m: self.memory.get("coder_ratings", {}).get(m, 0) + random.uniform(0, 0.5), reverse=True)
        return available[0]
        
    def get_fallback_models(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        return available[1:3] if len(available) > 1 else []

    def mark_unhealthy(self, model, reason="error", role=None):
        if reason == "QUOTA_EXHAUSTED":
            log_event(f"Account Quota reached. Halting.")
            exit(1)
            
        log_event(f"Marking {model} as UNHEALTHY ({reason}). Rotating to next model...")
        self.unhealthy_models.add(model)
        
        target_dict = f"{role}_ratings" if role else "model_ratings"
        if target_dict not in self.memory: self.memory[target_dict] = {}
        self.memory[target_dict][model] = self.memory[target_dict].get(model, 0) - 1
        save_memory(self.memory)

    def mark_healthy(self, model, role=None):
        target_dict = f"{role}_ratings" if role else "model_ratings"
        if target_dict not in self.memory: self.memory[target_dict] = {}
        self.memory[target_dict][model] = self.memory[target_dict].get(model, 0) + 1
        save_memory(self.memory)''',
'''    def _init_metrics(self, model, role):
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
            metrics = self.memory.get("coder_ratings", {}).get(m, {"files_generated": 0, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0})
            if isinstance(metrics, int): metrics = {"files_generated": metrics, "lint_passes": 0, "fix_attempts": 0, "fix_successes": 0}
            files = max(metrics.get("files_generated", 1), 1)
            fixes = max(metrics.get("fix_attempts", 1), 1)
            lint_rate = metrics.get("lint_passes", 0) / files
            fix_rate = metrics.get("fix_successes", 0) / fixes
            return (lint_rate * 0.4) + (fix_rate * 0.6) + random.uniform(0, 0.2)
        available.sort(key=score, reverse=True)
        return available[0]
        
    def get_fallback_models(self):
        available = [m for m in self.models if m not in self.unhealthy_models]
        return available[1:3] if len(available) > 1 else []

    def record_metric(self, model, role, metric, value=1):
        self._init_metrics(model, role)
        target_dict = f"{role}_ratings" if role else "model_ratings"
        if isinstance(self.memory[target_dict][model], int):
            self._init_metrics(model, role) # Ensure it's a dict
        self.memory[target_dict][model][metric] = self.memory[target_dict][model].get(metric, 0) + value
        save_memory(self.memory)

    def mark_unhealthy(self, model, reason="error", role=None):
        if reason == "QUOTA_EXHAUSTED":
            log_event(f"Account Quota reached. Halting.")
            exit(1)
        log_event(f"Marking {model} as UNHEALTHY ({reason}). Rotating to next model...")
        self.unhealthy_models.add(model)''')


# 3. Fuzzy search match
content = content.replace('''def apply_search_replace(file_content, search_block, replace_block):
    """SWE-Agent style exact string replacement"""
    search_block = search_block.replace('\\r\\n', '\\n')
    replace_block = replace_block.replace('\\r\\n', '\\n')
    file_content_norm = file_content.replace('\\r\\n', '\\n')
    
    if search_block in file_content_norm:
        return file_content_norm.replace(search_block, replace_block)
        
    if search_block.strip() in file_content_norm:
        return file_content_norm.replace(search_block.strip(), replace_block.strip())
        
    return "ERROR_SEARCH_NOT_FOUND"''',
'''def apply_search_replace(file_content, search_block, replace_block):
    """Fuzzy Line-Window Matcher for robust string replacement"""
    search_block = search_block.replace('\\r\\n', '\\n')
    replace_block = replace_block.replace('\\r\\n', '\\n')
    file_content_norm = file_content.replace('\\r\\n', '\\n')
    
    # Exact Match
    if search_block in file_content_norm:
        return file_content_norm.replace(search_block, replace_block)
        
    # Fuzzy Line Window Match
    search_lines = [line.strip() for line in search_block.split('\\n') if line.strip()]
    if not search_lines:
        return "ERROR_SEARCH_NOT_FOUND"
        
    file_lines = file_content_norm.split('\\n')
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
            new_lines = file_lines[:i] + replace_block.split('\\n') + file_lines[i+search_len:]
            return '\\n'.join(new_lines)
            
    return "ERROR_SEARCH_NOT_FOUND"''')


# 4. test script prompt
content = content.replace('''    Write a Windows .bat script named 'setup_and_test.bat'.
    1. Setup venv (Python) or npm install (Node).
    2. Install dependencies.
    3. Run rigorous unit tests (pytest for Python) to verify REAL coverage.
    4. MUST Exit with code 0 if success, 1 if fail.
    Output ONLY raw script. Do NOT wrap in markdown code blocks. No explanations.''',
'''    Write a Windows .bat script named 'setup_and_test.bat'.
    1. Setup venv (Python) or npm install (Node).
    2. Install dependencies. MUST `pip install pytest pytest-json-report`.
    3. Run rigorous unit tests. MUST run with `pytest --json-report --json-report-file=report.json`.
    4. MUST Exit with code 0 if success, 1 if fail.
    Output ONLY raw script. Do NOT wrap in markdown code blocks. No explanations.''')

# 5. validate_plan
content = content.replace('''def critique_plan(models, plan):''',
'''def validate_plan(plan):
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

def critique_plan(models, plan):''')

# 6. run_beast_cycle metric recording
content = content.replace('''                plan_copy = json.dumps(plan)
                plan, actual_critic = critique_plan(planner_fallback, plan)
                if json.dumps(plan) == plan_copy:
                    # +1 Informed scoring: Planner survived critique untouched
                    grid.mark_healthy(actual_planner, "planner")''',
'''                if not validate_plan(plan):
                    log_event("Architecture rejected by programmatic validation.")
                    grid.mark_unhealthy(actual_planner, "INVALID_PLAN", "planner")
                    project_state["plan"] = None
                    continue

                grid.record_metric(actual_planner, "planner", "plans_created")
                
                # Plan Critique
                plan_copy = json.dumps(plan)
                plan, actual_critic = critique_plan(planner_fallback, plan)
                if json.dumps(plan) == plan_copy:
                    grid.record_metric(actual_planner, "planner", "critique_survivals")''')

content = content.replace('''                        if lint_res.returncode == 0:
                            grid.mark_healthy(actual_coder, "coder") # +1 for lint pass
                        else:''',
'''                        if lint_res.returncode == 0:
                            grid.record_metric(actual_coder, "coder", "lint_passes")
                        else:''')

content = content.replace('''                project_state["files_created"].append(filepath)''',
'''                grid.record_metric(actual_coder, "coder", "files_generated")
                project_state["files_created"].append(filepath)''')

content = content.replace('''            # STAGE 3: TESTS & FIX LOOP
            # +1 Informed scoring: Planner reached Test Stage
            grid.mark_healthy(actual_planner, "planner")''',
'''            # STAGE 3: TESTS & FIX LOOP
            grid.record_metric(actual_planner, "planner", "test_stages_reached")''')

content = content.replace('''                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
                                             cwd=project_dir, capture_output=True, text=True, timeout=120)
                    
                    output_combined = result.stdout + result.stderr
                    has_evidence = bool(re.search(r'\\b\\d+ passed\\b', output_combined.lower()))
                    has_failures = bool(re.search(r'\\b\\d+ failed\\b', output_combined.lower())) or bool(re.search(r'\\b\\d+ error', output_combined.lower()))
                    
                    if result.returncode == 0 and has_evidence and not has_failures:
                        success = True
                        break 
                    else:
                        log_event(f"FAILURE. Syntax/Test error. Asking SAME model to patch...")
                        error_log = f"STDOUT:\\n{result.stdout[-1500:]}\\nSTDERR:\\n{result.stderr[-1500:]}"
                        if result.returncode == 0 and not has_evidence:
                            error_log += "\\nScript exited 0 but no 'passed' evidence was found in the output. Did the tests actually run?"''',
'''                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], 
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
                        except: pass
                    
                    if success:
                        break 
                    else:
                        log_event(f"FAILURE. Syntax/Test error. Asking SAME model to patch...")
                        error_log = f"STDOUT:\\n{result.stdout[-1500:]}\\nSTDERR:\\n{result.stderr[-1500:]}"
                        if not os.path.exists(report_path):
                            error_log += "\\nCRITICAL: `report.json` was NOT generated. Did pytest actually run?"''')

content = content.replace('''                        fix_attempts += 1
                        grid.mark_unhealthy(actual_fixer, "FIX_LOOP", "coder") # small penalty for needing a fix loop''',
'''                        fix_attempts += 1
                        grid.record_metric(actual_fixer, "coder", "fix_attempts")''')

content = content.replace('''                # Final check
                try:
                    result = subprocess.run(["cmd.exe", "/c", "setup_and_test.bat"], cwd=project_dir, capture_output=True, text=True, timeout=120)
                    output_combined = result.stdout + result.stderr
                    has_evidence = bool(re.search(r'\\b\\d+ passed\\b', output_combined.lower()))
                    has_failures = bool(re.search(r'\\b\\d+ failed\\b', output_combined.lower())) or bool(re.search(r'\\b\\d+ error', output_combined.lower()))
                    if result.returncode == 0 and has_evidence and not has_failures:
                        success = True
                        log_event("Sunk Cost Protocol SUCCEEDED.")
                except: pass''',
'''                # Final check
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
                except: pass''')

content = content.replace('''            if success:
                if fix_attempts == 0:
                    # +3 Informed scoring: Coder wrote perfect code on first try
                    grid.mark_healthy(actual_coder, "coder")
                    grid.mark_healthy(actual_coder, "coder")
                    grid.mark_healthy(actual_coder, "coder")''',
'''            if success:
                grid.record_metric(actual_coder, "coder", "fix_successes")''')

open('ai_brain.py', 'w', encoding='utf-8').write(content)
