from src.Erro import Erro

def Analisa_bloco(token, fila_tokens,fila_erros):
    token = Analisa_et_variaveis(token, fila_tokens,fila_erros)
    token = Analisa_subrotinas(token, fila_tokens,fila_erros)
    token = Analisa_comandos(token, fila_tokens,fila_erros)
    return token


def Analisa_et_variaveis(token, fila_tokens,fila_erros):
    if token.simbolo == "svar":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token = Analisa_Variaveis(token, fila_tokens,fila_erros)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                else:
                    erro = Erro("ERRO:etapa de variaveis","ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador","ERRO SINTATICO")
            fila_erros.put(erro)
    return token


def Analisa_Variaveis(token, fila_tokens,fila_erros):
    while token.simbolo == "sidentificador":
        token = fila_tokens.get()  # consome o token do identificador
        if token.simbolo == "svirgula" or token.simbolo == "sdoispontos":
            if token.simbolo == "svirgula":
                token = fila_tokens.get()  # consome próximo identificador
                if token.simbolo == "sdoispontos":
                    erro = Erro("ERRO: ':' inesperado após ','","ERRO SINTATICO")
                    fila_erros.put(erro)
                else:
                    # encontrou ':' → sai do while
                    break
            else:
                erro = Erro("ERRO:',' ou ':' esperado","ERRO SINTATICO")
                fila_erros.put(erro)
    if token.simbolo == "sdoispontos":
        token = fila_tokens.get()
        token = Analisa_Tipo(token, fila_tokens,fila_erros)
    else:
        erro = Erro("ERRO: ':' esperado","ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Analisa_Tipo(token, fila_tokens,ultima_variavel,fila_erros):
    if token.simbolo != "sinteiro" and token.simbolo != "sbooleano":
        erro = Erro("ERRO: tipo da variavel não reconhecido","ERRO SINTATICO")
        fila_erros.put(erro)
    token = fila_tokens.get()
    return token
    
def Analisa_comandos(token,fila_tokens,fila_erros):
    if token.simbolo == "sinicio":
        token = fila_tokens.get()
        Analisa_comando_simples(token,fila_tokens,fila_erros)
        while(token.simbolo != "sfim"):
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                if token.simbolo != "sfim":
                    Analisa_comando_simples(token,fila_tokens)
            else:
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)
        token = fila_tokens.get()
    else:
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)
    return token
    

def Analisa_comando_simples(token,fila_tokens,fila_erros):
    if token.simbolo == "sidentificador":
        Analisa_atrib_chprocedimento(token,fila_tokens)
    else:
        if token.simbolo == "sse":
            Analisa_se(token,fila_tokens)
        else:
            if token.simbolo == "senquanto":
                Analisa_enquanto(token,fila_tokens,fila_erros)
            else:
                if token.simbolo == "sleia":
                    Analisa_leia(token,fila_tokens,fila_erros)
                else:
                    if token.simbolo == "sescreva":
                        Analisa_escreva(token,fila_tokens,fila_erros)
                    else:
                        Analisa_comandos(token,fila_tokens,fila_erros)

def Analisa_atrib_chprocedimento(token,fila_tokens):
    token = fila_tokens.get()
    if token.simbolo == "satribuicao":
        Analisa_atribuicao(token,fila_tokens)
    else:
        Chamada_procedimento(token,fila_tokens)
    return token

def Analisa_leia(token, fila_tokens,fila_erros):
    # consome o "leia"
    token = fila_tokens.get()
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()

        if token.simbolo == "sidentificador":
            token = fila_tokens.get()
            if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()  # consome o ')'
            else:
                    erro = Erro("ERRO:esperado ')' após identificador","ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador após '('","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO:esperado '(' após 'leia'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_escreva(token, fila_tokens,fila_erros):
    # consome o "escreva"
    token = fila_tokens.get()

    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()

        if token.simbolo == "sidentificador":
            token = fila_tokens.get()
            if token.simbolo == "sfecha_parenteses":
                token = fila_tokens.get()  # consome o ')'
            else:
                erro = Erro("ERRO:Erro: esperado ')' após identificador em 'escreva'","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            print("Erro: esperado identificador após '(' em 'escreva'")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro) 
    else:
        print("Erro: esperado '(' após 'escreva'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_enquanto(token, fila_tokens,fila_erros):
    # consome o "enquanto"
    token = fila_tokens.get()

    # aqui deveria entrar a chamada para o analisador de expressão
    token = Analisa_expressao(token, fila_tokens,fila_erros)

    if token.simbolo == "sfaca":
        token = fila_tokens.get()  # consome o "faça"
        token = Analisa_comando_simples(token, fila_tokens)
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_se(token, fila_tokens,fila_erros):
    # consome o "se"
    token = fila_tokens.get()

    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens,fila_erros)

    if token.simbolo == "sentao":
        token = fila_tokens.get()  # consome o "então"
        token = Analisa_comando_simples(token, fila_tokens,fila_erros)

        if token.simbolo == "ssenão":
            token = fila_tokens.get()  # consome o "senão"
            token = Analisa_comando_simples(token, fila_tokens,fila_erros)
    else:
        print("Erro: esperado 'entao' após expressão no 'se'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_declaracao_procedimento(token, fila_tokens,fila_erros):
    # consome a palavra-chave "procedimento"
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        # consome o identificador
        token = fila_tokens.get()
        if token.simbolo == "spontovirgula":
            # consome o ponto e vírgula
            token = fila_tokens.get()
            # analisa o bloco do procedimento
            token = Analisa_bloco(token, fila_tokens)
        else:
            erro = Erro("ERRO:esperado ';' após nome do procedimento","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO:esperado identificador após 'procedimento'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_subrotinas(token, fila_tokens,fila_erros):
    # Enquanto o token atual for "procedimento" ou "função"
    while token.simbolo == "sprocedimento" or token.simbolo == "sfuncao":
        if token.simbolo == "sprocedimento":
            token = Analisa_declaracao_procedimento(token, fila_tokens)
        else:  # caso seja "sfuncao"
            token = Analisa_declaracao_funcao(token, fila_tokens,fila_erros)

        # após a declaração, deve vir ponto e vírgula
        if token.simbolo == "spontovirgula":
            token = fila_tokens.get()  # consome o ";"
        else:
            print("Erro: esperado ';' após declaração de sub-rotina")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)

    return token

def Analisa_declaracao_funcao(token, fila_tokens,fila_erros):
    # Consome a palavra-chave 'funcao'
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        token = fila_tokens.get()

        # Espera ':'
        if token.simbolo == "sdoispontos":
            token = fila_tokens.get()
            # Próximo token
            token = fila_tokens.get()

            # Espera ';'
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                # Chama o bloco da função
                token = Analisa_bloco(token, fila_tokens)
            else:
                erro = Erro("ERRO:esperado ';' após declaração de função","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado ':' após identificador da função","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO: esperado identificador após 'funcao'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_expressao(token, fila_tokens,fila_erros):
    # Primeiro analisa uma expressão simples
    token = Analisa_expressao_simples(token, fila_tokens,fila_erros)

    # Se encontrar operador relacional
    if token.simbolo in ["smaior", "smaiorig", "sig", "smenor", "smenorig", "sdif"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_expressao_simples(token, fila_tokens,fila_erros)

    return token

def Analisa_expressao_simples(token, fila_tokens,fila_erros):
    # Consome + ou - iniciais, se houver
    if token.simbolo in ["smais", "smenos"]:
        token = fila_tokens.get()

    # Analisa o primeiro termo
    token = Analisa_termo(token, fila_tokens,fila_erros)

    # Enquanto aparecer +, - ou "ou"
    while token.simbolo in ["smais", "smenos", "sou"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_termo(token, fila_tokens)

    return token

def Analisa_termo(token, fila_tokens,fila_erros):
    # Analisa o primeiro fator
    token = Analisa_fator(token, fila_tokens,fila_erros)

    # Enquanto houver * , div ou "e"
    while token.simbolo in ["smult", "sdiv", "se"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_fator(token, fila_tokens)

    return token

def Analisa_fator(token, fila_tokens,fila_erros):
    # Variável ou função
    if token.simbolo == "sidentificador":
        token = Analisa_chamada_funcao(token, fila_tokens,fila_erros)
    # Número
    elif token.simbolo == "snumero":
        token = fila_tokens.get()

    # Não
    elif token.simbolo == "snao":
        token = fila_tokens.get()
        token = Analisa_fator(token, fila_tokens)

    # Parênteses
    elif token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        token = Analisa_expressao(token, fila_tokens)
        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()
        else:
            print("Erro: esperado ')'")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)

    # Verdadeiro ou falso
    elif token.lexema in ["verdadeiro", "falso"]:
        token = fila_tokens.get()

    else:
        erro = Erro("ERRO:fator invalido","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_atribuicao(token, fila_tokens):
    # Consome o '=' (atribuição)
    token = fila_tokens.get()

    # Espera uma expressão do lado direito
    token = Analisa_expressao(token, fila_tokens)
    return token

def Analisa_chamada_funcao(token, fila_tokens,fila_erros):
    lexema_funcao = token.lexema

    # consome o identificador da função
    token = fila_tokens.get()

    # Espera '(' para chamada
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()  # consome '('

        # Aqui você poderia analisar os parâmetros, se houver
        # Por enquanto, vamos assumir sem parâmetros ou já tratados
        # Exemplo: Analisa_expressao(token, fila_tokens) para cada parâmetro
        # Enquanto não fechar ')'
        while token.simbolo != "sfecha_parenteses":
            token = Analisa_expressao(token, fila_tokens,fila_erros)
            if token.simbolo == "svirgula":
                token = fila_tokens.get()  # consome ',' e continua o próximo argumento
            elif token.simbolo != "sfecha_parenteses":
                print("Erro: esperado ',' ou ')' em chamada de função")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)

        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()  # consome ')'
        else:
            print("Erro: esperado ')' no final da chamada da função")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print(f"Erro: esperado '(' após função '{lexema_funcao}'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Chamada_procedimento(token, fila_tokens,fila_erros):
    lexema_proc = token.lexema
    # consome o identificador do procedimento
    token = fila_tokens.get()
    # Espera '(' para chamada de procedimento (mesmo que a função)
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()  # consome '('
        # Se houver parâmetros, analisa-os como expressões
        while token.simbolo != "sfecha_parenteses":
            token = Analisa_expressao(token, fila_tokens,fila_erros)
            if token.simbolo == "svirgula":
                token = fila_tokens.get()  # consome ',' e continua
            elif token.simbolo != "sfecha_parenteses":
                erro = Erro("ERRO:esperado ',' ou ')' em chamada de procedimento","ERRO SINTATICO")
                fila_erros.put(erro)

        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()  # consome ')'
        else:
            erro = Erro("ERRO:esperado ')' no final da chamada do procedimento","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print(f"Erro: esperado '(' após procedimento '{lexema_proc}'")
        erro = Erro("ERRO:esperado '(' após procedimento","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

