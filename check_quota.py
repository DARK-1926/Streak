import os, subprocess, json, ai_brain
key = getattr(ai_brain, 'OPENROUTER_API_KEY')
r = subprocess.run(['curl.exe', '-s', '-H', f'Authorization: Bearer {key}', '-H', 'Content-Type: application/json', '-d', '{"models": ["cohere/north-mini-code:free"], "messages": [{"role": "user", "content": "test"}]}', 'https://openrouter.ai/api/v1/chat/completions'], capture_output=True, text=True)
print(r.stdout)
