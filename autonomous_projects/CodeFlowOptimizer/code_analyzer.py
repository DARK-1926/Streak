import cProfile
import pstats
import tempfile
import os
from typing import Dict, Any

def analyze_code(code: str) -> Dict[str, Any]:
    """
    Analyzes the given Python code and returns a dictionary of profiling information.
    
    :param code: A string containing the Python code to be analyzed.
    :return: A dictionary containing the profiling information.
    """
    try:
        # Create a temporary file to write the code
        fd, path = tempfile.mkstemp(suffix='.py')
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(code)
        
        # Profile the code
        profiler = cProfile.Profile()
        profiler.run(f'exec(open(r"{path}").read())')
        
        # Get the stats
        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        # Convert stats to dictionary
        # Convert stats to dictionary
        profile_data = {}
        for key, value in stats.stats.items():
            if isinstance(key, tuple):
                func_name = f'{key[0]}:{key[1]}({key[2]}'
                profile_data[func_name] = {
                    'ncalls': value[0],
                    'tottime': value[2],
                    'cumtime': value[3]
                }
        
        # Convert stats to dictionary
        profile_data = {}
        for key, value in stats.stats.items():
            if isinstance(key, tuple):
                func_name = f'{key[0]}:{key[1]}({key[2]}'
                profile_data[func_name] = {
                    'ncalls': value[0],
                    'tottime': value[2],
                    'cumtime': value[3]
                }
        
        return profile_data
    except Exception as e:
        raise RuntimeError(f"Failed to analyze code: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(path):
            os.remove(path)

def get_profiling_data(profiling_info: Dict[str, Any]) -> str:
    """
    Takes the profiling information and returns a formatted report.
    
    :param profiling_info: A dictionary containing the profiling information.
    :return: A formatted string report of the profiling data.
    """
    report = "Profiling Report:\n"
    for func, info in profiling_info.items():
        report += (f"Function: {func}\n"
                   f"  - Number of calls: {info['ncalls']}\n"
                   f"  - Total time: {info['tottime']} s\n"
                   f"  - Cumulative time: {info['cumtime']} s\n")
    return report
