from src.AnalisadorLexical import AnalisadorLexical
from src.AnalisadorSintatico import AnalisadorSintatico
from multiprocessing import Process, Queue

if __name__ == "__main__":
    arquivo_input = "exemplos/programa2.txt"
    arquivo_output = "outputs/tokens.txt"

    #analisador = AnalisadorLexico(arquivo_input)
    #analisador.analisar()
    #analisador.salvar_tokens(arquivo_output)
       # Cria fila de tokens compartilhada
    fila_tokens = Queue()

    # Cria processos
    p_lex = Process(target=AnalisadorLexical, args=(arquivo_input, fila_tokens,))
    p_syn = Process(target=AnalisadorSintatico, args=(fila_tokens,))

    # Inicia processos
    p_lex.start()
    p_syn.start()

    # Aguarda finalização
    p_lex.join()
    p_syn.join()