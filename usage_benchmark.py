import os
import psutil

def cpu_usage():
    process = psutil.cpu_percent(interval=1)
    return process

def memory_usage():
    ram = psutil.virtual_memory()
    ram_used = round(ram.used / 1e9, 2)
    return ram, ram_used

print(cpu_usage())
print(memory_usage())