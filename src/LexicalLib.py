from src.Token import Token

def acabou(posicao_atual,conteudo): # EOF (end of conteudo)
    return posicao_atual[0] >= len(conteudo)

def ver_caractere(posicao_atual,conteudo):
    if acabou(posicao_atual,conteudo):
        return None
    return conteudo[posicao_atual[0]]

def ler_caractere(posicao_atual,conteudo):

    if acabou(posicao_atual,conteudo):
            return None
    ch = conteudo[posicao_atual[0]]
    posicao_atual[0]+=1
    return ch


def trata_digito(posicao_atual,conteudo):
        lex = []
        # pelo menos um dígito existe (dispatch garantiu)
        while True:
            c = ver_caractere(posicao_atual,conteudo)
            if c is not None and c.isdigit():
                lex.append(ler_caractere(posicao_atual,conteudo))
            else:
                break
        return Token("".join(lex), "NUMERO_INTEIRO")

def trata_ident_ou_reservada(posicao_atual,conteudo,reservadas):
        lex = []
        # primeiro caractere é letra ou '_'
        while True:
            c = ver_caractere(posicao_atual,conteudo)
            if c is not None and (c.isalnum() or c == "_"):
                lex.append(ler_caractere(posicao_atual,conteudo))
            else:
                break
        lexema = "".join(lex)

        simbolo = reservadas.get(lexema, "IDENTIFICADOR")
        return Token(lexema, simbolo)

def trata_atribuicao(posicao_atual,conteudo):
        # estamos sobre ':'
        primeiro = ler_caractere(posicao_atual,conteudo)  # consome ':'
        prox = ver_caractere(posicao_atual,conteudo)
        if prox == "=":
            ler_caractere(posicao_atual,conteudo)  # consome '='
            return Token(":=", "ATRIBUICAO")
        
        # apenas ':'
        return Token(primeiro, "DOIS_PONTOS")

def trata_op_aritmetico(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        mapa = {
            "+": "OP_SOMA",
            "-": "OP_SUB",
            "*": "OP_MULT",
        }
        return Token(c, mapa.get(c, "OPERADOR_ARITMETICO"))

def trata_op_relacional(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        prox = ver_caractere(posicao_atual,conteudo)

        if c == "!":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token("!=", "OP_DIF")
            
            # '!' sozinho não é válido na gramática
            return Token("!", "ERRO")

        if c == "<":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token("<=", "OP_MENOR_IGUAL")
            return Token("<", "OP_MENOR")

        if c == ">":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token(">=", "OP_MAIOR_IGUAL")
            return Token(">", "OP_MAIOR")

        if c == "=":
            # igualdade
            return Token("=", "OP_IGUAL")

        # fallback (não deve chegar aqui)
        return Token(c, "ERRO")

def trata_pontuacao(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        mapa = {
            ";": "PONTO_E_VIRGULA",
            ",": "VIRGULA",
            "(": "ABRE_PARENTESE",
            ")": "FECHA_PARENTESE",
            ".": "PONTO",
        }
        return Token(c, mapa.get(c, "PONTUACAO"))