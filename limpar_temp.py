import os
import shutil
import stat
import tempfile

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def limpar_pasta(caminho):
    if not os.path.exists(caminho):
        print(f"[AVISO] Pasta não encontrada: {caminho}")
        return

    print(f"\n[INFO] Limpando: {caminho}")
    removidos = 0
    falhas = 0

    for root, dirs, files in os.walk(caminho):
        for nome in files:
            caminho_arquivo = os.path.join(root, nome)
            try:
                os.remove(caminho_arquivo)
                removidos += 1
            except PermissionError:
                try:
                    os.chmod(caminho_arquivo, stat.S_IWRITE)
                    os.remove(caminho_arquivo)
                    removidos += 1
                except Exception:
                    falhas += 1
            except Exception:
                falhas += 1

        for nome in dirs:
            caminho_dir = os.path.join(root, nome)
            try:
                shutil.rmtree(caminho_dir, onerror=remove_readonly)
                removidos += 1
            except Exception:
                falhas += 1

    print(f"[OK] Removidos: {removidos}, Falhas: {falhas}")


def main():
    temp_usuario = tempfile.gettempdir()

    temp_sistema = r"C:\Windows\Temp"

    prefetch = r"C:\Windows\Prefetch"

    limpar_pasta(temp_usuario)
    limpar_pasta(temp_sistema)
    limpar_pasta(prefetch)

    print("\n[LIMPEZA CONCLUÍDA]")


if __name__ == "__main__":
    main()