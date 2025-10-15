import os
import stat
import shutil
import tempfile
import subprocess
from datetime import datetime


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def limpar_pasta(caminho):
    if not os.path.exists(caminho):
        return

    removidos, falhas = 0, 0
    for root, dirs, files in os.walk(caminho, topdown=False):
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

    print(f"[OK] {caminho} → {removidos} itens removidos ({falhas} falhas).")


def limpar_temp():
    print("\nIniciando limpeza de arquivos temporários...\n")

    limpar_pasta(tempfile.gettempdir())               # Temp do usuário
    limpar_pasta(r"C:\Windows\Temp")                  # Temp do sistema
    limpar_pasta(r"C:\Windows\Prefetch")              # Prefetch

    print("\nLimpeza concluída em", datetime.now().strftime("%H:%M:%S"))


def criar_tarefa_agendada(nome_tarefa, caminho_script, frequencia="DAILY", horario="09:00"):

    frequencia = frequencia.upper()
    dias_param = ""

    if frequencia == "WEEKLY":
        print("\nEscolha o(s) dia(s) da semana para execução:")
        print("Opções válidas: MON, TUE, WED, THU, FRI, SAT, SUN")
        print("Exemplo: MON ou MON,WED,FRI")
        dias = input("Digite o(s) dia(s): ").strip().upper()
        if dias:
            dias_param = f"/d {dias}"

    elif frequencia == "MONTHLY":
        print("\nEscolha o(s) dia(s) do mês para execução:")
        print("Exemplo: 1 ou 1,15,30")
        dias = input("Digite o(s) dia(s): ").strip()
        if dias:
            dias_param = f"/d {dias}"

    comando = (
        f'schtasks /create /tn "{nome_tarefa}" /tr "python \\"{caminho_script}\\"" '
        f'/sc {frequencia} {dias_param} /st {horario} /rl highest /f'
    )

    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"[TAREFA CRIADA] '{nome_tarefa}' agendada como {frequencia} às {horario}")
        if dias_param:
            print(f"[INFO] Dias configurados: {dias}")
    except subprocess.CalledProcessError:
        print("[ERRO] Falha ao criar a tarefa. Execute o script como administrador.")


def remover_tarefa_agendada(nome_tarefa):
    comando = f'schtasks /delete /tn "{nome_tarefa}" /f'
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"[TAREFA REMOVIDA] '{nome_tarefa}' excluída do agendador.")
    except subprocess.CalledProcessError:
        print("[ERRO] Falha ao remover a tarefa (talvez ela não exista).")


if __name__ == "__main__":
    nome_tarefa = "Limpeza de arquivos temporários"
    caminho_script = os.path.abspath(__file__)

    while True:
        limpar_tela()
        print("\n=== GERENCIADOR DE LIMPEZA AUTOMÁTICA ===")
        print("1. Executar limpeza agora")
        print("2. Agendar limpeza automática")
        print("3. Remover agendamento")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            limpar_temp()

        elif opcao == "2":
            print("\nFrequências disponíveis:")
            print("DAILY - Executar diariamente")
            print("WEEKLY - Executar semanalmente")
            print("MONTHLY - Executar mensalmente")
            opcoes = {"1": "DAILY", "2": "WEEKLY", "3": "MONTHLY"}
            escolha = input("\nEscolha a frequência:\n1. DAILY\n2. WEEKLY\n3. MONTHLY\n> ").strip()
            freq = opcoes.get(escolha, "DAILY")
            hora = input("Horário da execução (formato HH:MM, ex: 09:00): ").strip() or "09:00"
            criar_tarefa_agendada(nome_tarefa, caminho_script, freq, hora)

        elif opcao == "3":
            remover_tarefa_agendada(nome_tarefa)

        elif opcao == "0":
            print("\nSaindo do gerenciador de limpeza automática...")
            break

        else:
            print("Opção inválida. Tente novamente.")

        input("\nPressione ENTER para voltar ao menu principal...")