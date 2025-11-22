from src.AnalisadorLexical import AnalisadorLexical
from src.AnalisadorSintatico import AnalisadorSintatico
from multiprocessing import Process, Queue

if __name__ == "__main__":
    arquivo_input = "gera1.txt"
    arquivo_output = "outputs/tokens.txt"

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