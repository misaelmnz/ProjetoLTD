from pc_info import PcInfo
import time
import os


def display_bar(percent, length=30):
    bar_progress = int(length * percent / 100)
    return "█" * bar_progress + "-" * (length - bar_progress)

def bytes_to_num(n_byte):
    symbols = ("B", "KB", "GB", "TB")
    step = 1024
    i = 0
    while n_byte >= step and i < len(symbols):
        n_byte /= step
        i += 1
    return f"{n_byte:.2f} {symbols[i]}"

class InfoDisplay:
    def __init__(self):
        self.info = PcInfo()

    def display_bar(percent, length=30):
        bar_progress = int(length * percent / 100)
        return "█" * bar_progress + "-" * (length - bar_progress)

    def bytes_to_num(self, n_byte):
        symbols = ("B", "KB", "MB", "GB", "TB")
        step = 1024.0
        i = 0
        while n_byte >= step and i < len(symbols):
            n_byte /= step
            i += 1
        return f"{n_byte:.2f} {symbols[i]}"

    def cpu_display(self, cpu_info):
        print("// === CPU ===//")
        current_cpu_frequency = cpu_info['cpu_frequency']['current']
        max_cpu_frequency = cpu_info['cpu_frequency']['max']
        percent_cpu_frequency = (current_cpu_frequency / max_cpu_frequency) * 100 if max_cpu_frequency > 0 else 0

        print(f"\nUtilização Total da CPU: "
              f"\n {cpu_info['cpu_total_usage']:.2f} %"
              f" | {display_bar(cpu_info['cpu_total_usage'])} |\n")

        print(f"\nNúcleos: {cpu_info['cpu_physical_cores']}"
              f"\nProcessadores Lógicos: {cpu_info['cpu_cores']}"
              f"\nFrequência do Procesador: {cpu_info['cpu_frequency']['current']:.2f} Ghz | "
              f"{percent_cpu_frequency:5.1f} % {display_bar(percent_cpu_frequency)} |"
              f"\n"
              )

        for i, core in enumerate(cpu_info['cpu_core_usage']):
            print(f"...Core {i + 1:02}: {core:05} % | {display_bar(core)}  |")

    def memory_display(self, memory_info):
        print("\n// === Memória Ram ===// ")

        print(f"\nUtilização Total da Memória Ram: \n{memory_info['ram_percent']:.2f} %"
              f" | {display_bar(memory_info['ram_percent'])} |\n"
              f"\nMemória Ram: {self.bytes_to_num(memory_info['ram_total'])}"
              f"\nMemória Usada: {self.bytes_to_num(memory_info['ram_used'])}"
              f"\nMemória Livre: {self.bytes_to_num(memory_info['ram_free'])}"
              )

    def disk_display(self, disk_info):
        print(f"\n// === Disco Rígido ===//")

        print(f"\nUtilização Total do Disco: \n{disk_info['disk_percent']:.2f} %"
              f" | {display_bar(disk_info['disk_percent'])} |\n"
              f"\nEspaço Total: {self.bytes_to_num(disk_info['disk_total'])}"
              f"\nEspaço Usado: {self.bytes_to_num(disk_info['disk_used'])}"
              f"\nEspaço Livre: {self.bytes_to_num(disk_info['disk_free'])}")


    def internet_display(self, internet_info):
        print("\n// === Internet ===//")

        print(f"Bytes enviados: {self.bytes_to_num(internet_info["internet_rate"]["upload_rate"])}")
        print(f"Bytes recebidos: {self.bytes_to_num(internet_info["internet_rate"]["download_rate"])}")

    def display(self, interval=1):
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.info.collector()
                self.cpu_display(self.info.cpu_info)
                self.memory_display(self.info.memory_info)
                self.disk_display(self.info.disk_info)
                self.internet_display(self.info.internet_info)
                time.sleep(interval)
        except KeyboardInterrupt:
            print('\nExit')


if __name__ == '__main__':
    info_display = InfoDisplay()
    info_display.display()
