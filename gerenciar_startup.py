import os
import json
import shutil
import winreg
import subprocess
from pathlib import Path

BACKUP_FILE = Path.home() / "startup_backup.json"
BACKUP_DIR = Path.home() / "startup_backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ---------------------------
# Funções de utilidade
# ---------------------------

def listar_registro(chave_base, sub_chave):
    programas = {}
    try:
        with winreg.OpenKey(chave_base, sub_chave, 0, winreg.KEY_READ) as chave:
            i = 0
            while True:
                try:
                    nome, valor, _ = winreg.EnumValue(chave, i)
                    programas[nome] = {"value": valor, "location": f"REG::{sub_chave}"}
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return programas


def listar_pastas_startup():
    programas = {}
    pastas = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
    ]
    for pasta in pastas:
        if os.path.exists(pasta):
            for arquivo in os.listdir(pasta):
                if arquivo.lower().endswith(".lnk"):
                    programas[arquivo] = {"value": os.path.join(pasta, arquivo), "location": f"FS::{pasta}"}
    return programas


def listar_tudo():
    programas = {}
    programas.update(listar_registro(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"))
    programas.update(listar_registro(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"))
    programas.update(listar_registro(winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"))
    programas.update(listar_pastas_startup())
    return programas


# ---------------------------
# Backup e remoção
# ---------------------------

def salvar_backup(nome, meta):
    if BACKUP_FILE.exists():
        data = json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
    else:
        data = []
    data.append({"nome": nome, "meta": meta})
    BACKUP_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def desabilitar_programa(programas, indice):
    items = list(programas.items())
    if indice < 1 or indice > len(items):
        print("Índice inválido.")
        return
    nome, meta = items[indice-1]
    salvar_backup(nome, meta)
    loc = meta["location"]

    if loc.startswith("REG::"):
        chave = loc.split("REG::",1)[1]
        for base in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                with winreg.OpenKey(base, chave, 0, winreg.KEY_ALL_ACCESS) as k:
                    try:
                        winreg.DeleteValue(k, nome)
                        print(f"[OK] {nome} removido da inicialização ({chave})")
                        return
                    except FileNotFoundError:
                        pass
            except FileNotFoundError:
                continue
            except PermissionError:
                print(f"[ERRO] Permissão negada para {nome}. Execute como administrador.")
    elif loc.startswith("FS::"):
        caminho = meta["value"]
        try:
            shutil.move(caminho, BACKUP_DIR / Path(caminho).name)
            print(f"[OK] {nome} movido para backup: {BACKUP_DIR}")
        except Exception as e:
            print(f"[ERRO] Falha ao mover {nome}: {e}")


# ---------------------------
# Habilitar programas
# ---------------------------

def habilitar_programa():
    """Restaura backups OU adiciona novo programa à inicialização"""
    print("\n=== HABILITAR PROGRAMA NA INICIALIZAÇÃO ===")
    print("1. Restaurar de backup existente")
    print("2. Adicionar novo programa instalado")
    print("3. Cancelar")

    escolha = input("\nEscolha uma opção: ").strip()

    # Restaurar backup existente
    if escolha == "1":
        if not BACKUP_FILE.exists():
            print("[INFO] Nenhum backup encontrado.")
            return

        data = json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
        if not data:
            print("[INFO] Nenhuma entrada para restaurar.")
            return

        print("\nEntradas disponíveis para restauração:")
        for i, item in enumerate(data, start=1):
            print(f"{i}. {item['nome']} -> {item['meta']['value']} ({item['meta']['location']})")

        escolha_idx = input("\nDigite o número do programa para restaurar (ou 0 para sair): ").strip()
        if not escolha_idx.isdigit() or int(escolha_idx) == 0:
            return

        indice = int(escolha_idx)
        if indice < 1 or indice > len(data):
            print("Índice inválido.")
            return

        alvo = data.pop(indice - 1)
        nome, meta = alvo["nome"], alvo["meta"]
        loc = meta["location"]

        if loc.startswith("REG::"):
            chave = loc.split("REG::",1)[1]
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave, 0, winreg.KEY_SET_VALUE) as k:
                    winreg.SetValueEx(k, nome, 0, winreg.REG_SZ, meta["value"])
                    print(f"[OK] {nome} restaurado em {chave}")
            except PermissionError:
                print(f"[ERRO] Sem permissão. Execute como administrador.")
        elif loc.startswith("FS::"):
            try:
                shutil.move(BACKUP_DIR / Path(meta["value"]).name, meta["value"])
                print(f"[OK] Arquivo restaurado em {meta['value']}")
            except Exception as e:
                print(f"[ERRO] Falha ao restaurar arquivo: {e}")

        BACKUP_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Adicionar novo programa instalado
    elif escolha == "2":
        caminho_programa = ""
        nome_programa = ""

        print("\nEscolha como deseja adicionar o programa:")
        print("1. Selecionar executável manualmente")
        print("2. Procurar em Program Files")
        modo = input("\nDigite a opção desejada: ").strip()

        if modo == "1":
            caminho_programa = input("Digite o caminho completo do executável (.exe): ").strip('"')
            if not os.path.exists(caminho_programa):
                print("[ERRO] Caminho inválido.")
                return
            nome_programa = Path(caminho_programa).stem

        elif modo == "2":
            print("\n[INFO] Buscando programas em Program Files...")
            program_files = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")]
            encontrados = []
            for base in program_files:
                if base and os.path.exists(base):
                    for root, dirs, files in os.walk(base):
                        for f in files:
                            if f.lower().endswith(".exe"):
                                encontrados.append(os.path.join(root, f))
            if not encontrados:
                print("[INFO] Nenhum programa encontrado.")
                return

            # Paginação
            tamanho_pagina = 20
            total = len(encontrados)
            pagina = 0

            while True:
                inicio = pagina * tamanho_pagina
                fim = inicio + tamanho_pagina
                subset = encontrados[inicio:fim]

                print(f"\nExibindo {inicio+1} a {min(fim, total)} de {total} executáveis:")
                for i, caminho in enumerate(subset, start=inicio + 1):
                    print(f"{i}. {caminho}")

                print("\n[N] Próxima | [P] Anterior | [S] Selecionar | [Q] Sair")
                cmd = input("Escolha: ").strip().lower()

                if cmd == "n":
                    pagina += 1
                elif cmd == "p" and pagina > 0:
                    pagina -= 1
                elif cmd == "s":
                    idx = int(input("Digite o número do programa: "))
                    if idx < 1 or idx > total:
                        print("Índice inválido.")
                        continue
                    caminho_programa = encontrados[idx - 1]
                    nome_programa = Path(caminho_programa).stem
                    break
                elif cmd == "q":
                    return
                else:
                    print("Opção inválida.")

        else:
            return

        print("\nAdicionar para:")
        print("1. Somente este usuário")
        print("2. Todos os usuários (requer administrador)")
        nivel = input("Escolha: ").strip()

        chave_destino = r"Software\Microsoft\Windows\CurrentVersion\Run"
        base = winreg.HKEY_CURRENT_USER if nivel == "1" else winreg.HKEY_LOCAL_MACHINE

        try:
            with winreg.OpenKey(base, chave_destino, 0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, nome_programa, 0, winreg.REG_SZ, caminho_programa)
                print(f"[OK] {nome_programa} adicionado à inicialização.")
        except PermissionError:
            print("[ERRO] Execute como administrador.")

# ---------------------------
# Atrasar inicialização
# ---------------------------

def atrasar_programa(programas, indice, segundos=30):
    """Cria uma tarefa agendada para iniciar o programa com atraso"""
    items = list(programas.items())
    if indice < 1 or indice > len(items):
        print("Índice inválido.")
        return

    nome, meta = items[indice - 1]
    caminho = meta["value"]

    comando = (
        f'schtasks /create /tn "Atraso_{nome}" /tr "{caminho}" '
        f'/sc onlogon /delay 0000:{segundos:02d}'
    )

    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"[OK] {nome} será executado com atraso de {segundos}s após o login.")
    except subprocess.CalledProcessError:
        print(f"[ERRO] Falha ao criar tarefa agendada para {nome}. Requer modo administrador.")

if __name__ == "__main__":
    print("=== GERENCIADOR DE PROGRAMAS NA INICIALIZAÇÃO ===")

    while True:
        programas = listar_tudo()
        print("\nProgramas configurados para iniciar com o Windows:")
        if not programas:
            print("  [Nenhum programa encontrado]")
        else:
            for i, (nome, meta) in enumerate(programas.items(), start=1):
                print(f"{i}. {nome} -> {meta['value']} ({meta['location']})")

        print("\nAções disponíveis:")
        print(" [1] Desabilitar programa")
        print(" [2] Habilitar programa (restaurar ou adicionar novo)")
        print(" [3] Atrasar inicialização (segundos reais)")
        print(" [4] Atualizar lista")
        print(" [0] Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            if not programas:
                print("[INFO] Nenhum programa disponível para desabilitar.")
                continue
            idx = int(input("Digite o número do programa a desabilitar: "))
            desabilitar_programa(programas, idx)

        elif opcao == "2":
            habilitar_programa()

        elif opcao == "3":
            if not programas:
                print("[INFO] Nenhum programa disponível para atrasar.")
                continue
            idx = int(input("Digite o número do programa a atrasar: "))
            segundos = int(input("Quantos segundos de atraso? "))
            atrasar_programa(programas, idx, segundos)

        elif opcao == "4":
            print("\n[INFO] Lista atualizada.")
            continue

        elif opcao == "0":
            print("\nEncerrando o gerenciador...")
            break

        else:
            print("Opção inválida. Tente novamente.")

        input("\nPressione ENTER para continuar...")