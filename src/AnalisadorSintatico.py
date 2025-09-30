from src.SintaticoLib import *
from src.Erro import Erro
tabela_simbolos = {}

def AnalisadorSintatico(fila_tokens,fila_erros):
    print("[Sintático] Iniciado, aguardando tokens...")

    token = fila_tokens.get()  # pega o primeiro token

    while token is not None:
        print("[Sintático] Recebeu:", token)

        if token.simbolo == "sprograma":
            token = fila_tokens.get()  # consome 'programa'

            if token.simbolo == "sidentificador":
                # insere nome do programa na tabela de símbolos
                #tabela_simbolos[token.lexema] = {"categoria": "programa", "tipo": None}

                token = fila_tokens.get()  # consome identificador

                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()  # consome ';'

                    # Analisa o bloco do programa
                    token = Analisa_bloco(token, fila_tokens, tabela_simbolos,fila_erros)

                    if token is not None and token.simbolo == "sponto":
                        token = fila_tokens.get()  # consome '.'

                        if token is None:
                            print("[Sintático] Fim dos tokens. Encerrando.")
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

    print(">>> Tabela de Símbolos final:", tabela_simbolos)

            
                


        
        