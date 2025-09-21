from src.Erro import Erro

def Analisa_bloco(token, fila_tokens,tabela_simbolos,fila_erros):
    token = Analisa_et_variaveis(token, fila_tokens,tabela_simbolos,fila_erros)
    token = Analisa_subrotinas(token, fila_tokens,tabela_simbolos,fila_erros)
    token = Analisa_comandos(token, fila_tokens,tabela_simbolos,fila_erros)
    return token


def Analisa_et_variaveis(token, fila_tokens,tabela_simbolos,fila_erros):
    if token.simbolo == "svar":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token = Analisa_Variaveis(token, fila_tokens,tabela_simbolos,fila_erros)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                else:
                    erro = Erro("ERRO:etapa de variaveis","ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador","ERRO SINTATICO")
            fila_erros.put(erro)
    return token


def Analisa_Variaveis(token, fila_tokens, tabela_simbolos,fila_erros):
    while token.simbolo == "sidentificador":
        if token.lexema not in tabela_simbolos:
            ultima_variavel = token.lexema
            tabela_simbolos[ultima_variavel] = {"categoria": "variavel", "tipo": "", "valor": ""}
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
        else:
            erro = Erro("ERRO:variável"+{token.lexema}+" já declarada","ERRO SINTATICO")
            fila_erros.put(erro)

    if token.simbolo == "sdoispontos":
        token = fila_tokens.get()
        token = Analisa_Tipo(token, fila_tokens, tabela_simbolos,ultima_variavel)
    else:
        erro = Erro("ERRO: ':' esperado","ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Analisa_Tipo(token, fila_tokens,tabela_simbolos,ultima_variavel):
    if token.simbolo != "sinteiro" and token.simbolo != "sbooleano":
        print("erro tipo nao reconhecido")
    else:
        tabela_simbolos[ultima_variavel]["tipo"] = token.simbolo
        print(f"[Sintatico]TS atualizada: >>> Tipo '{token.simbolo}' adicionado na variável '{ultima_variavel}'")
        

    token = fila_tokens.get()
    return token
    
def Analisa_comandos(token,fila_tokens,tabela_simbolos,fila_erros):
    if token.simbolo == "sinicio":
        token = fila_tokens.get()
        Analisa_comando_simples(token,fila_tokens,tabela_simbolos,fila_erros)
        while(token.simbolo != "sfim"):
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                if token.simbolo != "sfim":
                    Analisa_comando_simples(token,fila_tokens,tabela_simbolos)
            else:
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)
        token = fila_tokens.get()
    else:
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)
    return token
    

def Analisa_comando_simples(token,fila_tokens,tabela_simbolos,fila_erros):
    if token.simbolo == "sidentificador":
        Analisa_atrib_chprocedimento(token,fila_tokens,tabela_simbolos)
    else:
        if token.simbolo == "sse":
            Analisa_se(token,fila_tokens,tabela_simbolos)
        else:
            if token.simbolo == "senquanto":
                Analisa_enquanto(token,fila_tokens,tabela_simbolos,fila_erros)
            else:
                if token.simbolo == "sleia":
                    Analisa_leia(token,fila_tokens,tabela_simbolos,fila_erros)
                else:
                    if token.simbolo == "sescreva":
                        Analisa_escreva(token,fila_tokens,tabela_simbolos,fila_erros)
                    else:
                        Analisa_comandos(token,fila_tokens,tabela_simbolos,fila_erros)

def Analisa_atrib_chprocedimento(token,fila_tokens,tabela_simbolos):
    token = fila_tokens.get()
    if token.simbolo == "satribuicao":
        Analisa_atribuicao(token,fila_tokens,tabela_simbolos)
    else:
        Chamada_procedimento(token,fila_tokens,tabela_simbolos)
    return token

def Analisa_leia(token, fila_tokens, tabela_simbolos,fila_erros):
    # consome o "leia"
    token = fila_tokens.get()
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()

        if token.simbolo == "sidentificador":
            # verifica se identificador existe na tabela
            if token.lexema in tabela_simbolos:
                token = fila_tokens.get()

                if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()  # consome o ')'
                else:
                    print("Erro: esperado ')' após identificador")
                    erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                print(f"Erro: variável '{token.lexema}' não declarada")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            print("Erro: esperado identificador após '('")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print("Erro: esperado '(' após 'leia'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_escreva(token, fila_tokens, tabela_simbolos,fila_erros):
    # consome o "escreva"
    token = fila_tokens.get()

    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()

        if token.simbolo == "sidentificador":
            # verifica se identificador existe (variável ou função)
            if token.lexema in tabela_simbolos:
                token = fila_tokens.get()

                if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()  # consome o ')'
                else:
                    print("Erro: esperado ')' após identificador em 'escreva'")
                    erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                print(f"Erro: identificador '{token.lexema}' não declarado")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
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

def Analisa_enquanto(token, fila_tokens, tabela_simbolos,fila_erros):
    # consome o "enquanto"
    token = fila_tokens.get()

    # aqui deveria entrar a chamada para o analisador de expressão
    token = Analisa_expressao(token, fila_tokens, tabela_simbolos,fila_erros)

    if token.simbolo == "sfaca":
        token = fila_tokens.get()  # consome o "faça"
        token = Analisa_comando_simples(token, fila_tokens, tabela_simbolos)
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_se(token, fila_tokens, tabela_simbolos,fila_erros):
    # consome o "se"
    token = fila_tokens.get()

    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens, tabela_simbolos,fila_erros)

    if token.simbolo == "sentao":
        token = fila_tokens.get()  # consome o "então"
        token = Analisa_comando_simples(token, fila_tokens, tabela_simbolos,fila_erros)

        if token.simbolo == "ssenão":
            token = fila_tokens.get()  # consome o "senão"
            token = Analisa_comando_simples(token, fila_tokens, tabela_simbolos,fila_erros)
    else:
        print("Erro: esperado 'entao' após expressão no 'se'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_declaracao_procedimento(token, fila_tokens, tabela_simbolos,fila_erros):
    # consome a palavra-chave "procedimento"
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        # verifica duplicidade na tabela
        if token.lexema not in tabela_simbolos:
            # insere na tabela de símbolos
            tabela_simbolos[token.lexema] = {
                "categoria": "procedimento",
                "tipo": None
            }
            print(f">>> Procedimento '{token.lexema}' adicionado na tabela de símbolos")
        else:
            print(f"Erro: procedimento '{token.lexema}' já declarado")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
         

        # consome o identificador
        token = fila_tokens.get()

        if token.simbolo == "spontovirgula":
            # consome o ponto e vírgula
            token = fila_tokens.get()
            # analisa o bloco do procedimento
            token = Analisa_bloco(token, fila_tokens, tabela_simbolos)
        else:
            print("Erro: esperado ';' após nome do procedimento")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print("Erro: esperado identificador após 'procedimento'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_subrotinas(token, fila_tokens, tabela_simbolos,fila_erros):
    # Enquanto o token atual for "procedimento" ou "função"
    while token.simbolo == "sprocedimento" or token.simbolo == "sfuncao":
        if token.simbolo == "sprocedimento":
            token = Analisa_declaracao_procedimento(token, fila_tokens, tabela_simbolos)
        else:  # caso seja "sfuncao"
            token = Analisa_declaracao_funcao(token, fila_tokens, tabela_simbolos,fila_erros)

        # após a declaração, deve vir ponto e vírgula
        if token.simbolo == "spontovirgula":
            token = fila_tokens.get()  # consome o ";"
        else:
            print("Erro: esperado ';' após declaração de sub-rotina")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)

    return token

def Analisa_declaracao_funcao(token, fila_tokens, tabela_simbolos,fila_erros):
    # Consome a palavra-chave 'funcao'
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        lexema_funcao = token.lexema

        # Verifica duplicidade
        if lexema_funcao in tabela_simbolos:
            print(f"Erro: função '{lexema_funcao}' já declarada.")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
        else:
            # Insere na tabela com tipo indefinido por enquanto
            tabela_simbolos[lexema_funcao] = {"categoria": "funcao", "tipo": ""}

        # Pega próximo token
        token = fila_tokens.get()

        # Espera ':'
        if token.simbolo == "sdoispontos":
            token = fila_tokens.get()

            # Verifica se é inteiro ou booleano
            if token.simbolo == "sinteiro":
                tabela_simbolos[lexema_funcao]["tipo"] = "funcao inteiro"
            elif token.simbolo == "sbooleano":
                tabela_simbolos[lexema_funcao]["tipo"] = "funcao booleana"
            else:
                print("Erro: tipo de retorno inválido em função.")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)

            # Próximo token
            token = fila_tokens.get()

            # Espera ';'
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                # Chama o bloco da função
                token = Analisa_bloco(token, fila_tokens, tabela_simbolos)
            else:
                print("Erro: esperado ';' após declaração de função")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            print("Erro: esperado ':' após identificador da função")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print("Erro: esperado identificador após 'funcao'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_expressao(token, fila_tokens, tabela_simbolos,fila_erros):
    # Primeiro analisa uma expressão simples
    token = Analisa_expressao_simples(token, fila_tokens, tabela_simbolos,fila_erros)

    # Se encontrar operador relacional
    if token.simbolo in ["smaior", "smaiorig", "sig", "smenor", "smenorig", "sdif"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_expressao_simples(token, fila_tokens, tabela_simbolos,fila_erros)

    return token

def Analisa_expressao_simples(token, fila_tokens, tabela_simbolos,fila_erros):
    # Consome + ou - iniciais, se houver
    if token.simbolo in ["smais", "smenos"]:
        token = fila_tokens.get()

    # Analisa o primeiro termo
    token = Analisa_termo(token, fila_tokens, tabela_simbolos,fila_erros)

    # Enquanto aparecer +, - ou "ou"
    while token.simbolo in ["smais", "smenos", "sou"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_termo(token, fila_tokens, tabela_simbolos)

    return token

def Analisa_termo(token, fila_tokens, tabela_simbolos,fila_erros):
    # Analisa o primeiro fator
    token = Analisa_fator(token, fila_tokens, tabela_simbolos,fila_erros)

    # Enquanto houver * , div ou "e"
    while token.simbolo in ["smult", "sdiv", "se"]:
        token = fila_tokens.get()  # consome o operador
        token = Analisa_fator(token, fila_tokens, tabela_simbolos)

    return token

def Analisa_fator(token, fila_tokens, tabela_simbolos,fila_erros):
    # Variável ou função
    if token.simbolo == "sidentificador":
        if token.lexema in tabela_simbolos:
            tipo = tabela_simbolos[token.lexema]["tipo"]
            if tipo in ["funcao inteiro", "funcao booleana"]:
                # Chama análise de chamada de função
                token = Analisa_chamada_funcao(token, fila_tokens, tabela_simbolos,fila_erros)
            else:
                token = fila_tokens.get()  # consome a variável
        else:
            print(f"Erro: identificador '{token.lexema}' não declarado")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)

    # Número
    elif token.simbolo == "snumero":
        token = fila_tokens.get()

    # Não
    elif token.simbolo == "snao":
        token = fila_tokens.get()
        token = Analisa_fator(token, fila_tokens, tabela_simbolos)

    # Parênteses
    elif token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        token = Analisa_expressao(token, fila_tokens, tabela_simbolos)
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

def Analisa_atribuicao(token, fila_tokens, tabela_simbolos):
    # Consome o '=' (atribuição)
    token = fila_tokens.get()

    # Espera uma expressão do lado direito
    token = Analisa_expressao(token, fila_tokens, tabela_simbolos)

    # Aqui você poderia adicionar verificação semântica de tipo
    # por exemplo:
    # tipo_var = tabela_simbolos[variavel]["tipo"]
    # tipo_expr = resultado_expressao
    # if tipo_var != tipo_expr: print("Erro de tipo")

    return token

def Analisa_chamada_funcao(token, fila_tokens, tabela_simbolos,fila_erros):
    lexema_funcao = token.lexema

    # consome o identificador da função
    token = fila_tokens.get()

    # Espera '(' para chamada
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()  # consome '('

        # Aqui você poderia analisar os parâmetros, se houver
        # Por enquanto, vamos assumir sem parâmetros ou já tratados
        # Exemplo: Analisa_expressao(token, fila_tokens, tabela_simbolos) para cada parâmetro
        # Enquanto não fechar ')'
        while token.simbolo != "sfecha_parenteses":
            token = Analisa_expressao(token, fila_tokens, tabela_simbolos,fila_erros)
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

def Chamada_procedimento(token, fila_tokens, tabela_simbolos,fila_erros):
    lexema_proc = token.lexema

    # Verifica se o procedimento foi declarado
    if lexema_proc not in tabela_simbolos:
        print(f"Erro: procedimento '{lexema_proc}' não declarado")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    # consome o identificador do procedimento
    token = fila_tokens.get()

    # Espera '(' para chamada de procedimento (mesmo que a função)
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()  # consome '('

        # Se houver parâmetros, analisa-os como expressões
        while token.simbolo != "sfecha_parenteses":
            token = Analisa_expressao(token, fila_tokens, tabela_simbolos,fila_erros)
            if token.simbolo == "svirgula":
                token = fila_tokens.get()  # consome ',' e continua
            elif token.simbolo != "sfecha_parenteses":
                print("Erro: esperado ',' ou ')' em chamada de procedimento")
                erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
                fila_erros.put(erro)

        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()  # consome ')'
        else:
            print(f"Erro: esperado ')' no final da chamada do procedimento '{lexema_proc}'")
            erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        print(f"Erro: esperado '(' após procedimento '{lexema_proc}'")
        erro = Erro("ERRO:generico para teste","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

