from src.Token import Token

class AnalisadorLexico:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.tokens = []
        self.conteudo = ""
        self.pos = 0

        # Tabela de palavras reservadas
        self.reservadas = {
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

            # operadores/lógicos e literais
            "div": "DIV",
            "e": "E",
            "ou": "OU",
            "nao": "NAO",
            "verdadeiro": "VERDADEIRO",
            "falso": "FALSO",
        }

    # ===== Helpers de cursor =====
    def acabou(self): # EOF (end of file)
        return self.pos >= len(self.conteudo)

    def ver_caractere(self):
        if self.acabou():
            return None
        return self.conteudo[self.pos]

    def ler_caractere(self):
        if self.acabou():
            return None
        ch = self.conteudo[self.pos]
        self.pos += 1
        return ch

    # ===== Pula comentários e espaços =====
    def pular_comentarios_e_espacos(self):
        while not self.acabou():
            c = self.ver_caractere()
            if c is None:
                break

            # espaços em branco (espaço, \n, \t, \r)
            if c.isspace():
                self.ler_caractere()
                continue

            # comentário { ... }
            if c == "{":
                self.ler_caractere()  # consome '{'
                # consome até '}'
                while not self.acabou():
                    d = self.ler_caractere()
                    if d == "}":
                        break
                # se acabou sem '}', apenas sai (comentário não fechado)
                continue

            # se não é espaço nem comentário, para
            break

    # ===== Dispatcher principal =====
    def pega_token(self):
        self.pular_comentarios_e_espacos()
        if self.acabou():
            return None  # EOF

        c = self.ver_caractere()

        if c.isdigit():
            return self.trata_digito()

        if c.isalpha() or c == "_":
            return self.trata_ident_ou_reservada()

        if c == ":":
            return self.trata_atribuicao()

        if c in "+-*":
            return self.trata_op_aritmetico()

        if c in "!<=>":
            return self.trata_op_relacional()

        if c in ";,().":
            return self.trata_pontuacao()

        # caractere desconhecido
        ch = self.ler_caractere()
        return Token(ch, "ERRO")

    # ===== Tratadores =====
    def trata_digito(self):
        lex = []
        # pelo menos um dígito existe (dispatch garantiu)
        while True:
            c = self.ver_caractere()
            if c is not None and c.isdigit():
                lex.append(self.ler_caractere())
            else:
                break
        return Token("".join(lex), "NUMERO_INTEIRO")

    def trata_ident_ou_reservada(self):
        lex = []
        # primeiro caractere é letra ou '_'
        while True:
            c = self.ver_caractere()
            if c is not None and (c.isalnum() or c == "_"):
                lex.append(self.ler_caractere())
            else:
                break
        lexema = "".join(lex)

        simbolo = self.reservadas.get(lexema, "IDENTIFICADOR")
        return Token(lexema, simbolo)

    def trata_atribuicao(self):
        # estamos sobre ':'
        primeiro = self.ler_caractere()  # consome ':'
        prox = self.ver_caractere()
        if prox == "=":
            self.ler_caractere()  # consome '='
            return Token(":=", "ATRIBUICAO")
        
        # apenas ':'
        return Token(primeiro, "DOIS_PONTOS")

    def trata_op_aritmetico(self):
        c = self.ler_caractere()
        mapa = {
            "+": "OP_SOMA",
            "-": "OP_SUB",
            "*": "OP_MULT",
        }
        return Token(c, mapa.get(c, "OPERADOR_ARITMETICO"))

    def trata_op_relacional(self):
        c = self.ler_caractere()
        prox = self.ver_caractere()

        if c == "!":
            if prox == "=":
                self.ler_caractere()
                return Token("!=", "OP_DIF")
            
            # '!' sozinho não é válido na gramática
            return Token("!", "ERRO")

        if c == "<":
            if prox == "=":
                self.ler_caractere()
                return Token("<=", "OP_MENOR_IGUAL")
            return Token("<", "OP_MENOR")

        if c == ">":
            if prox == "=":
                self.ler_caractere()
                return Token(">=", "OP_MAIOR_IGUAL")
            return Token(">", "OP_MAIOR")

        if c == "=":
            # igualdade
            return Token("=", "OP_IGUAL")

        # fallback (não deve chegar aqui)
        return Token(c, "ERRO")

    def trata_pontuacao(self):
        c = self.ler_caractere()
        mapa = {
            ";": "PONTO_E_VIRGULA",
            ",": "VIRGULA",
            "(": "ABRE_PARENTESE",
            ")": "FECHA_PARENTESE",
            ".": "PONTO",
        }
        return Token(c, mapa.get(c, "PONTUACAO"))

    # ===== Loop principal de análise =====
    def analisar(self):
        with open(self.caminho_arquivo, "r", encoding="utf-8") as arquivo:
            self.conteudo = arquivo.read()
            self.pos = 0

            while True:
                tok = self.pega_token()
                if tok is None:  # EOF
                    break
                self.tokens.append(tok)

        print("Analise finalizada. Total de tokens:\n", len(self.tokens))
        for t in self.tokens:
            print(f"{t.lexema:<15} -> {t.simbolo}")

    def salvar_tokens(self, nome_arquivo):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for t in self.tokens:
                f.write(f"{t.lexema:<15} -> {t.simbolo}\n")

        print(f"Tokens salvos no arquivo {nome_arquivo}")
