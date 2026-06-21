import sys
content = open('ai_brain.py', encoding='utf-8').read()

# 1. call_openrouter
content = content.replace('''    enforce_rate_limit()
    increment_quota() 
    
    try:
        response = requests.post(url, headers=headers, json={
            "models": models_list,''',
'''    for attempt in range(2):
        enforce_rate_limit()
        if attempt == 0: increment_quota() 
        
        try:
            response = requests.post(url, headers=headers, json={
                "models": models_list,''')

content = content.replace('''                if "limit reached" in err_msg.lower() or "credits" in err_msg.lower():
                    return "QUOTA_EXHAUSTED", actual_model
            return "SERVER_ERROR", actual_model
            
        return res_data["choices"][0]["message"]["content"], actual_model
    except Exception as e:
        log_event(f"API Request Failed: {e}")
        return "SERVER_ERROR", models_list[0]''',
'''                if "limit reached" in err_msg.lower() or "credits" in err_msg.lower():
                    return "QUOTA_EXHAUSTED", actual_model
                
                if attempt == 0:
                    log_event("Transient error across all models. Retrying array once in 5s...")
                    import time
                    time.sleep(5)
                    continue
                return "SERVER_ERROR", actual_model
            
            return res_data["choices"][0]["message"]["content"], actual_model
        except Exception as e:
            log_event(f"API Request Failed: {e}")
            if attempt == 0:
                log_event("Network error. Retrying array once in 5s...")
                import time
                time.sleep(5)
                continue
            return "SERVER_ERROR", models_list[0]''')

# 2. plan_project
content = content.replace('''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return content
    if not content: return None
    return extract_json(content, required_keys=["project_name", "files_to_generate", "lessons_learned", "interface_contracts"])''',
'''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return content, actual_model
    if not content: return None, actual_model
    return extract_json(content, required_keys=["project_name", "files_to_generate", "lessons_learned", "interface_contracts"]), actual_model''')

# 3. critique_plan
content = content.replace('''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return plan 
    critique = extract_json(content, required_keys=["files_to_generate"])
    return critique if critique else plan''',
'''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return plan, actual_model 
    critique = extract_json(content, required_keys=["files_to_generate"])
    return (critique if critique else plan), actual_model''')

# 4. generate_file_chunked
content = content.replace('''        if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]:
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
            
    log_event(f"Failed to generate full file {filepath} within {max_chunks} chunks.")
    return "ERROR_TRUNCATED"''',
'''        if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]:
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
    return "ERROR_TRUNCATED", models[0]''')

# 5. generate_tests
content = content.replace('''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR"
    if not content: return None
    return strip_markdown(content)''',
'''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR", actual_model
    if not content: return None, actual_model
    return strip_markdown(content), actual_model''')

# 6. fix_error
content = content.replace('''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR"
    if not content: return None
    return extract_json(content, required_keys=["root_cause_analysis", "files_to_update"])''',
'''    if content in ["SERVER_ERROR", "QUOTA_EXHAUSTED"]: return "ERROR", actual_model
    if not content: return None, actual_model
    return extract_json(content, required_keys=["root_cause_analysis", "files_to_update"]), actual_model''')

# 7. run_beast_cycle P1
content = content.replace('''            # STAGE 1: PLAN
            if not project_state.get("plan"):
                log_event(f"--- Assigning Planner Model: {planner_model} ---")
                trends = fetch_trends()
                plan = plan_project(planner_fallback, trends, memory)
                
                if plan == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during planning.")
                    exit(1)
                if plan == "SERVER_ERROR":
                    grid.mark_unhealthy(planner_model, "SERVER_ERROR", "planner")
                    continue
                if not plan or "files_to_generate" not in plan:
                    log_event(f"Architect {planner_model} failed planning phase.")
                    grid.mark_unhealthy(planner_model, "BAD_PLAN", "planner") 
                    continue
                    
                # Plan Critique
                plan_copy = json.dumps(plan)
                plan = critique_plan(planner_fallback, plan)
                if json.dumps(plan) == plan_copy:
                    # +1 Informed scoring: Planner survived critique untouched
                    grid.mark_healthy(planner_model, "planner")''',
'''            actual_coder = coder_model
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
                plan_copy = json.dumps(plan)
                plan, actual_critic = critique_plan(planner_fallback, plan)
                if json.dumps(plan) == plan_copy:
                    # +1 Informed scoring: Planner survived critique untouched
                    grid.mark_healthy(actual_planner, "planner")''')

# 8. run_beast_cycle P2
content = content.replace('''                blueprint_context = "\\n".join(project_state.get("blueprint", []))
                content = generate_file_chunked(coder_fallback, project_name, plan.get("vision", ""), filepath, instructions, blueprint_context)
                
                if content == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during coding.")
                    exit(1)
                if content in ["SERVER_ERROR", "ERROR_TRUNCATED"] or not content:
                    generation_failed = True
                    grid.mark_unhealthy(coder_model, "GENERATION_FAIL", "coder")
                    break''',
'''                blueprint_context = "\\n".join(project_state.get("blueprint", []))
                content, actual_coder = generate_file_chunked(coder_fallback, project_name, plan.get("vision", ""), filepath, instructions, blueprint_context)
                
                if content == "QUOTA_EXHAUSTED":
                    log_event("Quota exhausted during coding.")
                    exit(1)
                if content in ["SERVER_ERROR", "ERROR_TRUNCATED"] or not content:
                    generation_failed = True
                    grid.mark_unhealthy(actual_coder, "GENERATION_FAIL", "coder")
                    break''')

# 9. run_beast_cycle P3
content = content.replace('''                        if lint_res.returncode == 0:
                            grid.mark_healthy(coder_model, "coder") # +1 for lint pass
                        else:
                            log_event(f"Local Lint Failed for {filepath}. Triggering internal fast-fix.")
                            generation_failed = True
                            grid.mark_unhealthy(coder_model, "LINT_FAIL", "coder")
                            break''',
'''                        if lint_res.returncode == 0:
                            grid.mark_healthy(actual_coder, "coder") # +1 for lint pass
                        else:
                            log_event(f"Local Lint Failed for {filepath}. Triggering internal fast-fix.")
                            generation_failed = True
                            grid.mark_unhealthy(actual_coder, "LINT_FAIL", "coder")
                            break''')

content = content.replace('''            if not check_dependencies(project_state["files_created"], project_dir):
                log_event("Hallucinated dependencies found. Swapping model.")
                grid.mark_unhealthy(coder_model, "HALLUCINATED_DEPS", "coder")
                continue''',
'''            if not check_dependencies(project_state["files_created"], project_dir):
                log_event("Hallucinated dependencies found. Swapping model.")
                grid.mark_unhealthy(actual_coder, "HALLUCINATED_DEPS", "coder")
                continue''')

# 10. run_beast_cycle P4
content = content.replace('''            files_created = project_state["files_created"]
            test_script = generate_tests(coder_fallback, project_name, files_created)
            if test_script == "QUOTA_EXHAUSTED": exit(1)
            if test_script == "SERVER_ERROR" or not test_script:
                grid.mark_unhealthy(coder_model, "TEST_GEN_FAIL", "coder")
                continue''',
'''            files_created = project_state["files_created"]
            test_script, actual_tester = generate_tests(coder_fallback, project_name, files_created)
            if test_script == "QUOTA_EXHAUSTED": exit(1)
            if test_script == "SERVER_ERROR" or not test_script:
                grid.mark_unhealthy(actual_tester, "TEST_GEN_FAIL", "coder")
                continue''')

content = content.replace('''                        fix_plan = fix_error(coder_fallback, project_dir, list(crashing_files), error_log)
                        if fix_plan == "QUOTA_EXHAUSTED": exit(1)
                        if fix_plan == "SERVER_ERROR" or not fix_plan or "files_to_update" not in fix_plan:
                            log_event("Model failed to provide a valid fix plan.")
                            fix_attempts += 1
                            continue''',
'''                        fix_plan, actual_fixer = fix_error(coder_fallback, project_dir, list(crashing_files), error_log)
                        if fix_plan == "QUOTA_EXHAUSTED": exit(1)
                        if fix_plan == "SERVER_ERROR" or not fix_plan or "files_to_update" not in fix_plan:
                            log_event("Model failed to provide a valid fix plan.")
                            fix_attempts += 1
                            grid.mark_unhealthy(actual_fixer, "BAD_FIX_PLAN", "coder")
                            continue''')

content = content.replace('''                        fix_attempts += 1
                        grid.mark_unhealthy(coder_model, "FIX_LOOP", "coder") # small penalty for needing a fix loop''',
'''                        fix_attempts += 1
                        grid.mark_unhealthy(actual_fixer, "FIX_LOOP", "coder") # small penalty for needing a fix loop''')

# 11. run_beast_cycle P5
content = content.replace('''            if not success and fix_attempts >= 3:
                # Sunk Cost Protocol (Best-of-N Scaling)
                log_event("Sunk Cost Protocol Engaged: 3 attempts failed. Best-of-2 parallel generation on crashing files.")''',
'''            if not success and fix_attempts >= 3:
                # Sunk Cost Protocol
                log_event("Sunk Cost Protocol Engaged: 3 attempts failed. Sequential full rewrite on crashing files.")''')

content = content.replace('''                        log_event(f"Regenerating {failing_file} entirely...")
                        new_content = generate_file_chunked(coder_fallback, project_name, "Fixing errors by full rewrite", failing_file, failing_instructions + " THE PREVIOUS IMPLEMENTATION FAILED ENTIRELY. REWRITE IT DIFFERENTLY.", blueprint_context)
                        if new_content and new_content not in ["SERVER_ERROR", "ERROR_TRUNCATED", "QUOTA_EXHAUSTED"]:''',
'''                        log_event(f"Regenerating {failing_file} entirely...")
                        new_content, actual_sunk_coder = generate_file_chunked(coder_fallback, project_name, "Fixing errors by full rewrite", failing_file, failing_instructions + " THE PREVIOUS IMPLEMENTATION FAILED ENTIRELY. REWRITE IT DIFFERENTLY.", blueprint_context)
                        if new_content and new_content not in ["SERVER_ERROR", "ERROR_TRUNCATED", "QUOTA_EXHAUSTED"]:''')

# 12. run_beast_cycle P6
content = content.replace('''            if success:
                if fix_attempts == 0:
                    # +3 Informed scoring: Coder wrote perfect code on first try
                    grid.mark_healthy(coder_model, "coder")
                    grid.mark_healthy(coder_model, "coder")
                    grid.mark_healthy(coder_model, "coder")
                    
                log_event(f"VICTORY ACHIEVED! Code is fully working.")
                memory["score"] += 1
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": coder_model})''',
'''            if success:
                if fix_attempts == 0:
                    # +3 Informed scoring: Coder wrote perfect code on first try
                    grid.mark_healthy(actual_coder, "coder")
                    grid.mark_healthy(actual_coder, "coder")
                    grid.mark_healthy(actual_coder, "coder")
                    
                log_event(f"VICTORY ACHIEVED! Code is fully working.")
                memory["score"] += 1
                memory["history"].append({"date": datetime.now().isoformat(), "project": project_name, "model": actual_coder})''')

open('ai_brain.py', 'w', encoding='utf-8').write(content)
