import os
from src.Gera import configura_saida
from src.AnalisadorLexical import AnalisadorLexical
from src.AnalisadorSintatico import AnalisadorSintatico
from multiprocessing import Process, Queue
import sys

fonte = sys.argv[1]              # exemplo: "codigo.txt"
arquivo_fonte_absoluto = os.path.abspath(fonte)

nome_arquivo = os.path.basename(arquivo_fonte_absoluto)  # "codigo.txt"
base = nome_arquivo.rsplit(".", 1)[0]                    # "codigo"

OBJ_FILE = base + ".obj"         # "codigo.obj"

os.makedirs("outputs", exist_ok=True)
OBJ_FILE = os.path.join("outputs", OBJ_FILE)             # outputs/codigo.obj


configura_saida(OBJ_FILE)

    # limpar arquivo antes de iniciar
with open(OBJ_FILE, "w", encoding="utf-8") as f:
    pass


if __name__ == "__main__":
    arquivo_input= sys.argv[1]


    fila_tokens = Queue()
    fila_erros = Queue()

    # Cria processos
    p_lex = Process(target=AnalisadorLexical, args=(arquivo_input, fila_tokens,fila_erros,))
    p_syn = Process(target=AnalisadorSintatico, args=(fila_tokens,fila_erros))

    # Inicia processos
    p_lex.start()
    p_syn.start()

      # Monitor da fila de erros
    while True:
        try:
            erro = fila_erros.get_nowait()
            p_lex.terminate()
            p_syn.terminate()

            print("Erro encontrado:\n")
            print(erro.tipo + "\n")
            print(erro.mensagem)
            
            break  # sai do loop
        except:
            # Nenhum erro no momento
            if not p_lex.is_alive() and not p_syn.is_alive():
                # ambos os processos terminaram sem erros
                print("Processos concluidos sem erros.")
                break