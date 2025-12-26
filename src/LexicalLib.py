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
        return Token("".join(lex), "snumero")

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

        simbolo = reservadas.get(lexema, "sidentificador")
        return Token(lexema, simbolo)

def trata_atribuicao(posicao_atual,conteudo):
        # estamos sobre ':'
        primeiro = ler_caractere(posicao_atual,conteudo)  # consome ':'
        prox = ver_caractere(posicao_atual,conteudo)
        if prox == "=":
            ler_caractere(posicao_atual,conteudo)  # consome '='
            return Token(":=", "satribuicao")
        
        # apenas ':'
        return Token(primeiro, "sdoispontos")

def trata_op_aritmetico(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        mapa = {
            "+": "smais",
            "-": "smenos",
            "*": "smult",
        }
        return Token(c, mapa.get(c, "OPERADOR_ARITMETICO"))

def trata_op_relacional(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        prox = ver_caractere(posicao_atual,conteudo)

        if c == "!":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token("!=", "sdif")
            
            # '!' sozinho não é válido na gramática
            return Token("!", "ERRO")

        if c == "<":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token("<=", "smenorig")
            return Token("<", "smenor")

        if c == ">":
            if prox == "=":
                ler_caractere(posicao_atual,conteudo)
                return Token(">=", "smaiorig")
            return Token(">", "smaior")

        if c == "=":
            # igualdade
            return Token("=", "sig")

        return Token(c, "ERRO")

def trata_pontuacao(posicao_atual,conteudo):
        c = ler_caractere(posicao_atual,conteudo)
        mapa = {
            ";": "spontovirgula",
            ",": "svirgula",
            "(": "sabre_parenteses",
            ")": "sfecha_parenteses",
            ".": "sponto",
        }
        return Token(c, mapa.get(c, "PONTUACAO"))

def pular_comentarios_e_espacos(posicao_atual, conteudo):
    while posicao_atual[0] < len(conteudo):
        c = conteudo[posicao_atual[0]]

        if c.isspace():
            posicao_atual[0] += 1
            continue

        if c == "{":
            posicao_atual[0] += 1  # consome '{'
            while posicao_atual[0] < len(conteudo) and conteudo[posicao_atual[0]] != "}":
                posicao_atual[0] += 1
            if posicao_atual[0] < len(conteudo):
                posicao_atual[0] += 1  # consome '}'
            continue

        # se não é espaço nem comentário, para
        break
