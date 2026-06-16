import psutil
import platform
import json

class HardwareProfiler:
    def cpu_info(self):
        return {
            "cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "freq": psutil.cpu_freq().current
        }

    def memory_info(self):
        mem = psutil.virtual_memory()
        return {"total_gb": mem.total / (1024 ** 3)}

    def disk_info(self):
        disk = psutil.disk_partitions()[0]
        usage = psutil.disk_usage(disk.mountpoint)
        return {"total_gb": usage.total / (1024 ** 3)}

class ModelSelector:
    def __init__(self, profiler):
        self.profiler = profiler

    def recommend(self):
        cpu = self.profiler.cpu_info()
        if cpu["cores"] >= 8:
            return "llama-70b"
        return "llama-7b"

if __name__ == "__main__":
    profiler = HardwareProfiler()
    selector = ModelSelector(profiler)
    print(json.dumps({"recommendation": selector.recommend()}, indent=2))
