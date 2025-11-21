from src.Erro import Erro
from src.LexicalLib import *

reservadas = {
    "programa": "sprograma",
    "var": "svar",
    "inteiro": "sinteiro",
    "booleano": "sbooleano",
    "procedimento": "sprocedimento",
    "funcao": "sfuncao",
    "se": "sse",
    "entao": "sentao",
    "senao": "ssenao",
    "enquanto": "senquanto",
    "faca": "sfaca",
    "inicio": "sinicio",
    "fim": "sfim",
    "escreva": "sescreva",
    "leia": "sleia",
    "div": "sdiv",
    "e": "se",
    "ou": "sou",
    "nao": "snao",
    "verdadeiro": "sverdadeiro",
    "falso": "sfalso",
    "numero": "snumero",
}

def AnalisadorLexical(caminho_arquivo, fila_tokens,fila_erros):
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
        posicao_atual = [0]
        
        while True:
            #ignora espaços e comentarios 
            pular_comentarios_e_espacos(posicao_atual,conteudo)

            if acabou(posicao_atual, conteudo):
                # EOF -> sinaliza fim e encerra
                fila_tokens.put(None)
                print("[Lexico] Todos os tokens enviados. Fim do processo.")
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
                erro = Erro("ERRO:Caracter desconhecido '"+ch+"'","ERRO LEXICAL")
                fila_erros.put(erro)

            # adiciona token válido
            if tok:
                # print("[Lexico] Token gerado:", tok.lexema, "->", tok.simbolo)
                fila_tokens.put(tok)
