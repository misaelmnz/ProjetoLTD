import os
import winreg
import time
import shutil
import subprocess

# ---------------------------
# Funções de utilidade
# ---------------------------

def listar_registro(chave_base, sub_chave):
    """Lista valores de uma chave de registro"""
    programas = {}
    try:
        with winreg.OpenKey(chave_base, sub_chave, 0, winreg.KEY_READ) as chave:
            i = 0
            while True:
                try:
                    nome, valor, _ = winreg.EnumValue(chave, i)
                    programas[nome] = valor
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return programas


def listar_inicializacao():
    """Lista todos os programas configurados para iniciar com o Windows"""
    programas = {}

    # Registro - Usuário atual
    programas.update(listar_registro(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run"))

    # Registro - Todos os usuários
    programas.update(listar_registro(winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run"))

    # Registro 32 bits
    programas.update(listar_registro(winreg.HKEY_LOCAL_MACHINE,
        r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"))

    # Pastas de inicialização
    pastas = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
    ]

    for pasta in pastas:
        if os.path.exists(pasta):
            for arquivo in os.listdir(pasta):
                if arquivo.lower().endswith(".lnk"):
                    programas[arquivo] = os.path.join(pasta, arquivo)

    return programas


def desabilitar_programa(nome):
    """Remove programa das chaves de inicialização"""
    caminhos = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]
    for base, sub in caminhos:
        try:
            with winreg.OpenKey(base, sub, 0, winreg.KEY_ALL_ACCESS) as chave:
                winreg.DeleteValue(chave, nome)
                print(f"[OK] {nome} removido da inicialização ({sub})")
        except FileNotFoundError:
            pass
        except PermissionError:
            print(f"[ERRO] Sem permissão para remover {nome} em {sub}")


def atrasar_programa(nome, caminho, segundos=30):
    """Cria uma tarefa agendada que inicia o programa com atraso"""
    comando = f'schtasks /create /tn "Atraso_{nome}" /tr "{caminho}" /sc once /st 00:00:30 /delay 0000:{segundos:02d}'
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"[OK] {nome} agendado com atraso de {segundos}s")
    except subprocess.CalledProcessError:
        print(f"[ERRO] Falha ao criar tarefa agendada para {nome}")


# ---------------------------
# Execução principal
# ---------------------------

if __name__ == "__main__":
    print("=== GERENCIADOR DE PROGRAMAS NA INICIALIZAÇÃO ===")

    programas = listar_inicializacao()

    if not programas:
        print("[INFO] Nenhum programa encontrado na inicialização.")
    else:
        print("\n[INFO] Programas configurados para iniciar com o Windows:\n")
        for i, (nome, caminho) in enumerate(programas.items(), 1):
            print(f"{i}. {nome} -> {caminho}")

        print("\nAções disponíveis:")
        print(" [1] Desabilitar programa")
        print(" [2] Atrasar inicialização")
        print(" [3] Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            alvo = input("Digite o nome exato do programa a desabilitar: ")
            desabilitar_programa(alvo)

        elif opcao == "2":
            alvo = input("Digite o nome exato do programa para atrasar: ")
            segundos = int(input("Quantos segundos de atraso? "))
            if alvo in programas:
                atrasar_programa(alvo, programas[alvo], segundos)
            else:
                print("[ERRO] Programa não encontrado na lista.")

        else:
            print("Saindo...")