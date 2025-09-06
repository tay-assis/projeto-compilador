from src.Token import Token
from src.LexicalLib import *

reservadas = {
    "programa": "PROGRAMA",
    "var": "VAR",
    "inteiro": "INTEIRO",
    "booleano": "BOOLEANO",
    "procedimento": "PROCEDIMENTO",
    "funcao": "FUNCAO",
    "se": "SE",
    "entao": "ENTAO",
    "senao": "SENAO",
    "enquanto": "ENQUANTO",
    "faca": "FACA",
    "inicio": "INICIO",
    "fim": "FIM",
    "escreva": "ESCREVA",
    "leia": "LEIA",
    "div": "DIV",
    "e": "E",
    "ou": "OU",
    "nao": "NAO",
    "verdadeiro": "VERDADEIRO",
    "falso": "FALSO",
}


def AnalisadorLexical(caminho_arquivo, fila_tokens):
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
        posicao_atual = [0]
        
        while True:
            #ignora espaços e comentarios 
            while posicao_atual[0] < len(conteudo):
                c = conteudo[posicao_atual[0]]

                # pula espaços (\n, \t, espaço, etc.)
                if c.isspace():
                    posicao_atual[0] += 1
                    continue

                # comentário { ... }
                if c == "{":
                      # consome '{'
                    while posicao_atual[0] < len(conteudo) and conteudo[posicao_atual[0]] != "}":
                        posicao_atual[0]+=1
                      # consome '}'
                        continue

                # não é espaço nem comentário -> sai
                break
            print("saiu pular comentario")

            if acabou(posicao_atual, conteudo):
                # EOF -> sinaliza fim e encerra
                fila_tokens.put(None)
                print("[Léxico] Todos os tokens enviados. Fim do processo.")
                break

            c = ver_caractere(posicao_atual, conteudo)
            tok = None

            if c.isdigit():
                tok = trata_digito(posicao_atual, conteudo)
                

            elif c.isalpha() or c == "_":
                tok = trata_ident_ou_reservada(posicao_atual, conteudo, reservadas)
                

            elif c == ":":
                tok = trata_atribuicao(posicao_atual, conteudo)
                

            elif c in "+-*":
                tok = trata_op_aritmetico(posicao_atual, conteudo)
                

            elif c in "!<=>":
                tok = trata_op_relacional(posicao_atual, conteudo)
                

            elif c in ";,().":
                tok = trata_pontuacao(posicao_atual, conteudo)
                

            else:
                # caractere desconhecido
                ch = ler_caractere(posicao_atual, conteudo)
                tok = Token(ch, "ERRO")
                

            # adiciona token válido ou de erro
            if tok:
                print("[Léxico] Token gerado:", tok.lexema, "->", tok.simbolo)
                fila_tokens.put(tok)
            


    #def salvar_tokens(self, nome_arquivo):
           # with open(nome_arquivo, "w", encoding="utf-8") as f:
              #  for t in tokens:
               #     f.write(f"{t.lexema:<15} -> {t.simbolo}\n")

           # print(f"Tokens salvos no arquivo {nome_arquivo}")
