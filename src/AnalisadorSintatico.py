from src.SintaticoLib import *
import src.TabelaSimbolos as TS
from src.Erro import Erro

def AnalisadorSintatico(fila_tokens,fila_erros):
    print("[Sintatico] Iniciado, aguardando tokens...")
    
    # Reseta a tabela de símbolos
    TS.resetar_tabela()

    token = fila_tokens.get()  # pega o primeiro token

    while token is not None:
        # print("[Sintatico] Recebeu:", token)

        if token.simbolo == "sprograma":

            token = fila_tokens.get()  # consome 'programa'

            if token.simbolo == "sidentificador":

                # Insere o nome do programa na tabela de símbolos
                TS.insere_tabela(token.lexema, "nomedeprograma", tipo=None, nivel=None, end=None)
                gera("","START","","")

                # Inicio o escopo do programa
                TS.enter_scope() # nível 0
                
                token = fila_tokens.get()  # consome identificador

                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()  # consome ';'

                    # Analisa o bloco do programa
                    token = Analisa_bloco(token, fila_tokens, fila_erros)

                    if token is not None and token.simbolo == "sponto":
                        token = fila_tokens.get()  # consome '.'

                        if token is None:
                            print("[Sintatico] Fim dos tokens. Encerrando.")
                            break
                        else:
                            erro = Erro("ERRO:tokens extras após '.'","ERRO SINTATICO")
                            fila_erros.put(erro)
                    else:
                        erro = Erro("ERRO:esperado '.' ao final do programa","ERRO SINTATICO")
                        fila_erros.put(erro)
                else:
                    erro = Erro("ERRO:esperado ';' após nome do programa","ERRO SINTATICO")
                    fila_erros.put(erro)
                    break
            else:
                erro = Erro("ERRO:esperado identificador após 'programa'","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador  'programa'","ERRO SINTATICO")
            fila_erros.put(erro)
            break