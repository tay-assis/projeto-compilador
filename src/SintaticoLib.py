from src.Erro import Erro

def Analisa_bloco(token, fila_tokens,fila_erros):
    token = Analisa_et_variaveis(token, fila_tokens,fila_erros)
    token = Analisa_subrotinas(token, fila_tokens,fila_erros)
    token = Analisa_comandos(token, fila_tokens,fila_erros)
    return token


def Analisa_et_variaveis(token, fila_tokens,fila_erros):
    if token.simbolo == "svar":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token = Analisa_Variaveis(token, fila_tokens,fila_erros)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                    print("[Sintático] Recebeu:", token)
                else:
                    erro = Erro("ERRO:etapa de variaveis","ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador","ERRO SINTATICO")
            fila_erros.put(erro)
    return token


def Analisa_Variaveis(token, fila_tokens, fila_erros):
    while True:
        if token.simbolo == "sidentificador":
            token = fila_tokens.get()  # consome identificador
            print("[Sintático] Recebeu:", token)

            if token.simbolo == "svirgula" or token.simbolo == "sdoispontos":
                if token.simbolo == "svirgula":
                    token = fila_tokens.get()  # consome próximo
                    print("[Sintático] Recebeu:", token)
                    if token.simbolo == "sdoispontos":
                        erro = Erro("ERRO: ':' inesperado após ','", "ERRO SINTATICO")
                        fila_erros.put(erro)
                        break
                    # senão, continua o loop, esperando próximo identificador
                else:
                    # encontrou dois pontos → sai do loop
                    break
            else:
                erro = Erro("ERRO: ',' ou ':' esperado", "ERRO SINTATICO")
                fila_erros.put(erro)
                break
        else:
            erro = Erro("ERRO: identificador esperado", "ERRO SINTATICO")
            fila_erros.put(erro)
            break

        # condição de parada: achou dois pontos
        if token.simbolo == "sdoispontos":
            break

    # se chegou aqui, precisa analisar o tipo
    if token.simbolo == "sdoispontos":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        token = Analisa_Tipo(token, fila_tokens, fila_erros)
    else:
        erro = Erro("ERRO: ':' esperado", "ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Analisa_Tipo(token, fila_tokens,fila_erros):
    if token.simbolo != "sinteiro" and token.simbolo != "sbooleano":
        erro = Erro("ERRO: tipo da variavel não reconhecido","ERRO SINTATICO")
        fila_erros.put(erro)
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)
    return token
    
def Analisa_comandos(token,fila_tokens,fila_erros):
    if token.simbolo == "sinicio":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        token = Analisa_comando_simples(token,fila_tokens,fila_erros)
        while(token.simbolo != "sfim"):
            #if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                print("[Sintático] Recebeu:", token)
                if(token.simbolo != "sfim"):
                    token = Analisa_comando_simples(token,fila_tokens,fila_erros)
            #else:
                #erro = Erro("ERRO: ';' ausente","ERRO SINTATICO")
                #fila_erros.put(erro)
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
    else:
        erro = Erro("ERRO: em declarações apos programa,procedimento ou funcao","ERRO SINTATICO")
        fila_erros.put(erro)
    return token
    

def Analisa_comando_simples(token,fila_tokens,fila_erros):
    if token.simbolo == "sidentificador":
        token = Analisa_atrib_chprocedimento(token,fila_tokens,fila_erros)
    else:
        if token.simbolo == "sse":
          token = Analisa_se(token,fila_tokens,fila_erros)
        else:
            if token.simbolo == "senquanto":
                token = Analisa_enquanto(token,fila_tokens,fila_erros)
            else:
                if token.simbolo == "sleia":
                    token = Analisa_leia(token,fila_tokens,fila_erros)
                else:
                    if token.simbolo == "sescreva":
                        token = Analisa_escreva(token,fila_tokens,fila_erros)
                    else:
                        token = Analisa_comandos(token,fila_tokens,fila_erros)
    return token

def Analisa_atrib_chprocedimento(token,fila_tokens,fila_erros):
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)
    if token.simbolo == "satribuicao":
        token = Analisa_atribuicao(token,fila_tokens,fila_erros)
    else:
        return token
        #token = Chamada_procedimento(token,fila_tokens,fila_erros)
    return token

def Analisa_leia(token, fila_tokens,fila_erros):
    # consome o "leia"
    print(token.lexema)
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        if token.simbolo == "sidentificador":
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)
            if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()  # consome o ')'
                    print("[Sintático] Recebeu :", token)
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
    print("[Sintático] Recebeu:", token)

    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)

        if token.simbolo == "sidentificador":
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)
            if token.simbolo == "sfecha_parenteses":
                token = fila_tokens.get()  # consome o ')'
                print("[Sintático] Recebeu:", token)
            else:
                erro = Erro("ERRO:Erro: esperado ')' após identificador em 'escreva'","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador após '(' em 'escreva'","ERRO SINTATICO")
            fila_erros.put(erro) 
    else:
        erro = Erro("ERRO: esperado '(' após 'escreva'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_enquanto(token, fila_tokens,fila_erros):
    # consome o "enquanto"
    token = fila_tokens.get()
  
    print("[Sintático] Recebeu:", token)
    


    token = Analisa_expressao(token, fila_tokens,fila_erros)
    if token.simbolo == "sfaca":
        token = fila_tokens.get()  # consome o "faça"
        print("[Sintático] Recebeu:", token)
        token = Analisa_comando_simples(token, fila_tokens,fila_erros)
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_se(token, fila_tokens,fila_erros):
    # consome o "se"
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)

    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens,fila_erros)

    if token.simbolo == "sentao":
        token = fila_tokens.get()  # consome o "então"
        print("[Sintático] Recebeu:", token)
        token = Analisa_comando_simples(token, fila_tokens,fila_erros)

        if token.simbolo == "ssenão":
            token = fila_tokens.get()  # consome o "senão"
            print("[Sintático] Recebeu:", token)
            token = Analisa_comando_simples(token, fila_tokens,fila_erros)
    else:
        erro = Erro("ERRO:esperado 'entao' após expressão no 'se'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_declaracao_procedimento(token, fila_tokens,fila_erros):
    # consome a palavra-chave "procedimento"
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)

    if token.simbolo == "sidentificador":
        # consome o identificador
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        if token.simbolo == "spontovirgula":
            # consome o ponto e vírgula
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)
            # analisa o bloco do procedimento
            token = Analisa_bloco(token, fila_tokens,fila_erros)
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
            token = Analisa_declaracao_procedimento(token, fila_tokens,fila_erros)
        else:  # caso seja "sfuncao"
            token = Analisa_declaracao_funcao(token, fila_tokens,fila_erros)

        # após a declaração, deve vir ponto e vírgula
        if token.simbolo == "spontovirgula":
            token = fila_tokens.get()  # consome o ";"
            print("[Sintático] Recebeu:", token)
        else:
            erro = Erro("ERRO:esperado ';' após declaração de sub-rotina","ERRO SINTATICO")
            fila_erros.put(erro)

    return token

def Analisa_declaracao_funcao(token, fila_tokens,fila_erros):
    # Consome a palavra-chave 'funcao'
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)

    if token.simbolo == "sidentificador":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)

        # Espera ':'
        if token.simbolo == "sdoispontos":
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)
            # Próximo token
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)

            # Espera ';'
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                print("[Sintático] Recebeu:", token)
                # Chama o bloco da função
                token = Analisa_bloco(token, fila_tokens,fila_erros)
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
        print("[Sintático] Recebeu:", token)
        token = Analisa_expressao_simples(token, fila_tokens,fila_erros)

    return token

def Analisa_expressao_simples(token, fila_tokens,fila_erros):
    # Consome + ou - iniciais, se houver
    if token.simbolo in ["smais", "smenos"]:
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)

    # Analisa o primeiro termo
    token = Analisa_termo(token, fila_tokens,fila_erros)

    # Enquanto aparecer +, - ou "ou"
    while token.simbolo in ["smais", "smenos", "sou"]:
        token = fila_tokens.get()  # consome o operador
        print("[Sintático] Recebeu:", token)
        token = Analisa_termo(token, fila_tokens,fila_erros)

    return token

def Analisa_termo(token, fila_tokens,fila_erros):
    # Analisa o primeiro fator
    token = Analisa_fator(token, fila_tokens,fila_erros)

    # Enquanto houver * , div ou "e"
    while token.simbolo in ["smult", "sdiv", "se"]:
        token = fila_tokens.get()  # consome o operador
        print("[Sintático] Recebeu:", token)
        token = Analisa_fator(token, fila_tokens,fila_erros)

    return token

def Analisa_fator(token, fila_tokens,fila_erros):
    # Variável
    if token.simbolo == "sidentificador":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
    # Número
    elif token.simbolo == "sinteiro":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
    # Não
    elif token.simbolo == "snao":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        token = Analisa_fator(token, fila_tokens,fila_erros)

    # Parênteses
    elif token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)
        token = Analisa_expressao(token, fila_tokens,fila_erros)
        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()
            print("[Sintático] Recebeu:", token)
        else:
            erro = Erro("ERRO:esperado ')'","ERRO SINTATICO")
            fila_erros.put(erro)

    # Verdadeiro ou falso
    elif token.lexema in ["verdadeiro", "falso"]:
        token = fila_tokens.get()
        print("[Sintático] Recebeu:", token)

    else:
        erro = Erro("ERRO:fator invalido","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_atribuicao(token, fila_tokens,fila_erros):
    # Consome o ':=' (atribuição)
    token = fila_tokens.get()
    print("[Sintático] Recebeu:", token)

    # Espera uma expressão do lado direito
    token = Analisa_expressao(token, fila_tokens,fila_erros)
    return token

def Analisa_chamada_funcao(token, fila_tokens, fila_erros):
    # Aqui o token recebido já deve ser um identificador
    if token.simbolo == "sidentificador":
        print("[Sintático] Chamada de função:", token.lexema)
        token = fila_tokens.get()  # consome o identificador
    else:
        erro = Erro("ERRO: identificador esperado em chamada de função", "ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Chamada_procedimento(token, fila_tokens,fila_erros):
    # Aqui o token recebido já deve ser um identificador
    print(token.lexema)
    if token.simbolo == "sidentificador":
        print("[Sintático] Chamada Procedimento:", token.lexema)
        token = fila_tokens.get()  # consome o identificador
    else:
        erro = Erro("ERRO: identificador esperado em chamada de Procedimento", "ERRO SINTATICO")
        fila_erros.put(erro)

    return token
