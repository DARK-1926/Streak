import json
from secure_code_wrapper import execute_code

def parse_request(request_body: str) -> dict:
    """
    Parse the incoming request body into a dictionary.
    """
    try:
        return json.loads(request_body)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in request body")

def format_response(result: dict) -> str:
    """
    Format the result of the code execution into a JSON response.
    """
    return json.dumps(result)

def handle_request(request: dict) -> dict:
    """
    Handle an incoming request by executing the provided code.
    """
    if 'code' not in request:
        return {'error': 'No code provided in request'}
    
    code = request['code']
    input_data = request.get('input_data', {})
    
    try:
        return execute_code(code, input_data)
    except Exception as e:
        return {'error': str(e)}
        response = json.dumps(result)
        return response
    except (TypeError, ValueError) as e:
        # Handle JSON encoding errors
        return json.dumps({'error': f'Failed to encode result: {str(e)}'})
