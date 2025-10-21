import time
from enum import nonmember

import psutil

class PcInfo:

    def __init__(self):
        self.cpu_info = None
        self.memory_info = None
        self.disk_info = None
        self.internet_info = None

    def collect_cpu_info(self):

        self.cpu_info = {
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_cores": psutil.cpu_count(logical=True),
            "cpu_frequency": psutil.cpu_freq()._asdict(),
            "cpu_core_usage": psutil.cpu_percent(percpu=True),
            "cpu_total_usage": psutil.cpu_percent(),
        }
        return self.cpu_info

    def collect_memory_info(self):
        system_virtual_mem = psutil.virtual_memory()
        self.memory_info = {
            "ram_total": system_virtual_mem.total,
            "ram_used": system_virtual_mem.used,
            "ram_free": system_virtual_mem.free,
            "ram_percent": system_virtual_mem.percent,
        }
        return self.memory_info

    def collect_disk_info(self):
        self.disk_info = {
            "disk_total": psutil.disk_usage("/").total,
            "disk_used": psutil.disk_usage("/").used,
            "disk_free": psutil.disk_usage("/").free,
            "disk_percent": psutil.disk_usage("/").percent,
        }
        return self.disk_info

    def collect_internet_info(self):

        if not self.internet_info:
            self.internet_info = {
                "last_byte_sent": None,
                "last_byte_received": None,
                "last_time": None,
                "internet_rate": {
                    "upload_rate": 0,
                    "download_rate": 0
                }
            }

        net = psutil.net_io_counters()
        now = time.time()
        bytes_sent = net.bytes_sent
        bytes_recv = net.bytes_recv

        if self.internet_info["last_byte_sent"] is not None and self.internet_info["last_byte_received"] is not None:
            interval = now - self.internet_info["last_time"]
            if interval > 0:
                upload_rate = (bytes_sent - self.internet_info["last_byte_sent"]) / interval
                download_rate = (bytes_recv - self.internet_info["last_byte_received"]) / interval
                self.internet_info["internet_rate"]["upload_rate"] = upload_rate
                self.internet_info["internet_rate"]["download_rate"] = download_rate
        else:
            self.internet_info["internet_rate"]["upload_rate"] = 0
            self.internet_info["internet_rate"]["download_rate"] = 0

        self.internet_info["last_byte_sent"] = bytes_sent
        self.internet_info["last_byte_received"] = bytes_recv
        self.internet_info["last_time"] = now

        return self.internet_info["internet_rate"]


    def collector(self):
        self.collect_cpu_info()
        self.collect_memory_info()
        self.collect_disk_info()
        self.collect_internet_info()
