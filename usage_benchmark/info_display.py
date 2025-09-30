import psutil

from pc_info import PcInfo
import time
import os


class InfoDisplay:
    def __init__(self):
        self.info = PcInfo()

    def display_bar(self, percent, length=30):
        bar_progress = int(length * percent / 100)
        return "█" * bar_progress + "-" * (length - bar_progress)

    def display(self, interval=1):
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.info.collector()
                display_values = self.info

                ## 1. Isso ainda será devidamente separado em uma classes e defs dedicadas*, com cada valor convertido em string
                ## CPU

                print("// === CPU ===// ")

                current_cpu_frequency = display_values.cpu_info['cpu_frequency']['current']
                max_cpu_frequency = display_values.cpu_info['cpu_frequency']['max']
                percent_cpu_frequency = (current_cpu_frequency / max_cpu_frequency) * 100 if max_cpu_frequency > 0 else 0

                print(f"\nUtilização Total da CPU: "
                      f"\n {display_values.cpu_info['cpu_total_usage']:.2f} %"
                      f" | {self.display_bar(display_values.cpu_info['cpu_total_usage'])} |\n")

                print(f"\nNúcleos: {display_values.cpu_info['cpu_physical_cores']}"
                      f"\nProcessadores Lógicos: {display_values.cpu_info['cpu_cores']}"
                      f"\nFrequência do Procesador: {display_values.cpu_info['cpu_frequency']['current']:.2f} Ghz | "
                      f"{percent_cpu_frequency:5.1f} % {self.display_bar(percent_cpu_frequency)} |"
                      f"\n"
                      )

                for i, core in enumerate(display_values.cpu_info['cpu_core_usage']):
                    print(f"...Core {i+1:02}: {core:05} % | {self.display_bar(core)}  |")


                ## Memória
                ## Converter corretamente o tamanho da memória*, atribuindo apenas ao tamanho útil

                memory_size_div = 1000000 ## Diminuir por 6 '0's.

                print("\n// === Memória Ram ===// ")

                print(f"\nUtilização Total da Memória Ram: \n{display_values.memory_info['ram_percent']:.2f} %"
                        f" | {self.display_bar(display_values.memory_info['ram_percent'])} |\n"
                        f"\nMemória Ram: {display_values.memory_info['ram_total']/memory_size_div:.2f} MB"
                        f"\nMemória Usada: {display_values.memory_info['ram_used']/memory_size_div:.2f} MB"
                        f"\nMemória Livre: {display_values.memory_info['ram_free']/memory_size_div:.2f} MB"
                        )

                ## Disco Rígido

                disk_size_div = 1000000000 # Diminuir por 9 '0's.

                print(f"\n// === Disco Rígido ===//")

                print(f"\nUtilização Total do Disco: \n{display_values.memory_info['ram_percent']:.2f} %"
                      f" | {self.display_bar(display_values.disk_info['disk_percent'])} |\n"
                      f"\nEspaço Total: {display_values.disk_info['disk_total'] / disk_size_div:.2f} GB"
                      f"\nEspaço Usado: {display_values.disk_info['disk_used'] / disk_size_div:.2f} GB"
                      f"\nEspaço Livre: {display_values.disk_info['disk_free'] / disk_size_div:.2f} GB")

                time.sleep(interval)

        except KeyboardInterrupt:
            print('\nExit')


if __name__ == '__main__':
    info_display = InfoDisplay()
    info_display.display()
