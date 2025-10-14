import psutil

class PcInfo:
    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        return instance

    def __init__(self):
        self.cpu_info = None
        self.memory_info = None
        self.disk_info = None
        self.internet_info = None

    def collector(self):

        self.cpu_info = {
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_cores": psutil.cpu_count(logical=True),
            "cpu_frequency": psutil.cpu_freq()._asdict(),
            "cpu_core_usage": psutil.cpu_percent(percpu=True),
            "cpu_total_usage": psutil.cpu_percent(),
        }

        system_virtual_mem = psutil.virtual_memory()

        self.memory_info = {
            "ram_total": system_virtual_mem.total,
            "ram_used": system_virtual_mem.used,
            "ram_free": system_virtual_mem.free,
            "ram_percent": system_virtual_mem.percent,
        }

        self.disk_info = {
            "disk_total": psutil.disk_usage("/").total,
            "disk_used": psutil.disk_usage("/").used,
            "disk_free": psutil.disk_usage("/").free,
            "disk_percent": psutil.disk_usage("/").percent,
        }

        self.internet_info = {
            "internet_bytes_sent": psutil.net_io_counters().bytes_sent,
            "internet_bytes_received": psutil.net_io_counters().bytes_recv,
        }
