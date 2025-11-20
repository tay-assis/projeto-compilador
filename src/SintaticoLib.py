from src.Erro import Erro
import src.TabelaSimbolos as TS

def Analisa_bloco(token, fila_tokens,fila_erros):
    token = Analisa_et_variaveis(token, fila_tokens,fila_erros)
    token = Analisa_subrotinas(token, fila_tokens,fila_erros)
    token = Analisa_comandos(token, fila_tokens,fila_erros)
    return token


def Analisa_et_variaveis(token, fila_tokens,fila_erros):
    if token.simbolo == "svar":
        token = fila_tokens.get()
        # print("[Sintatico] Recebeu:", token)
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token = Analisa_Variaveis(token, fila_tokens,fila_erros)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                    # print("[Sintatico] Recebeu:", token)
                else:
                    erro = Erro("ERRO:etapa de variaveis","ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador","ERRO SINTATICO")
            fila_erros.put(erro)
    return token


def Analisa_Variaveis(token, fila_tokens, fila_erros):
    # lista temporária para armazenar variáveis do mesmo tipo
    lista_var = []
    
    while True:
        if token.simbolo == "sidentificador":
            
            if not TS.pesquisa_declvar_tabela(token.lexema) or not TS.pesquisa_var_func_tabela_inteira(token.lexema):
                lista_var.append(token.lexema)
                
                TS.insere_tabela(token.lexema, "variavel", tipo=None, nivel=None, end=None)
            
                token = fila_tokens.get()  # consome identificador
                # print("[Sintatico] Recebeu:", token)

                if token.simbolo == "svirgula" or token.simbolo == "sdoispontos":
                    if token.simbolo == "svirgula":
                        token = fila_tokens.get()  # consome próximo
                        # print("[Sintatico] Recebeu:", token)
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
                erro = Erro(f"ERRO: variável '{token.lexema}' já declarada neste bloco", "ERRO SEMANTICO")
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
        # print("[Sintatico] Recebeu:", token)
        
        # print("\n",lista_var, "\n")
        
        token = Analisa_Tipo(token, fila_tokens, fila_erros, lista_var)

        TS.imprimir_tabela()

    else:
        erro = Erro("ERRO: ':' esperado", "ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Analisa_Tipo(token, fila_tokens,fila_erros, lista_var):
    if token.simbolo != "sinteiro" and token.simbolo != "sbooleano":
        erro = Erro("ERRO: tipo da variavel não reconhecido","ERRO SINTATICO")
        fila_erros.put(erro)
    
    # print("[Semantico] Atribuindo tipo", token.lexema, "as variaveis:", lista_var)

    # Atribuindo o tipo para as variáveis declaradas
    TS.atribuir_tipo_variaveis(lista_var, token.lexema)
    
    token = fila_tokens.get()
    # print("[Sintatico] Recebeu:", token)
    return token
    
def Analisa_comandos(token,fila_tokens,fila_erros):
    if token.simbolo == "sinicio":
        token = fila_tokens.get()
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_comando_simples(token,fila_tokens,fila_erros)
        while(token.simbolo != "sfim"):
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                # print("[Sintatico] Recebeu:", token)
                if(token.simbolo != "sfim"):
                    token = Analisa_comando_simples(token,fila_tokens,fila_erros)
            else:
                erro = Erro("ERRO: ';' ausente","ERRO SINTATICO")
                fila_erros.put(erro)
        token = fila_tokens.get()
        # print("[Sintatico] Recebeu:", token)
    else:
        erro = Erro("ERRO: em declarações apos programa,procedimento ou funcao","ERRO SINTATICO")
        fila_erros.put(erro)
    return token
    

def Analisa_comando_simples(token,fila_tokens,fila_erros):
    if token.simbolo == "sidentificador": # pode ser atribuição de variável, função (retorno da função) ou chamada de procedimento
        print("\n\n comando simples com identificador:", token.lexema, token.simbolo +"\n\n")
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
                        # erro = Erro("ERRO:comando simples invalido","ERRO SINTATICO")
                        # fila_erros.put(erro)
                        token = Analisa_comandos(token,fila_tokens,fila_erros)
    return token

def Analisa_atrib_chprocedimento(token,fila_tokens,fila_erros):
    if token.simbolo == "sidentificador":
        if TS.get_categoria(token.lexema) == "variavel":
            tipo_var = TS.get_tipo(token.lexema) # Obtém o tipo da variável
            token = fila_tokens.get()
            if token.simbolo == "satribuicao":
                token = Analisa_atribuicao(token,fila_tokens,fila_erros, tipo_var)
            else:
                erro = Erro("ERRO:esperado ':=' apos identificador em atribuicao","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            # Se for função verificar se existe retorno (obrigatório atribuir o retorno da função)
            if TS.get_categoria(token.lexema) == "funcao":
                tipo_func = TS.get_tipo(token.lexema) # Obtém o tipo da função
                token = fila_tokens.get()
                if token.simbolo == "satribuicao":
                    token = Analisa_atribuicao(token,fila_tokens,fila_erros, tipo_func)
                else:
                    # Erro de função sem atribuição do retorno
                    erro = Erro("ERRO:esperado atribuir o retorno da funcao","ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                # É chamada de procedimento
                token = Chamada_procedimento(token,fila_tokens,fila_erros)
    return token

def Analisa_leia(token, fila_tokens,fila_erros):
    # consome o "leia"
    token = fila_tokens.get()
    # print("[Sintatico] Recebeu:", token)
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        # print("[Sintatico] Recebeu:", token)
        if token.simbolo == "sidentificador":
            # Verifica se a variável foi declarada até o marcador
            if TS.pesquisa_var_func_tabela_inteira(token.lexema):
                # Verifica se a variável é do tipo inteiro
                if not TS.verifica_tipo(token.lexema, "inteiro"):
                    erro = Erro(f"ERRO: variavel '{token.lexema}' nao é do tipo inteiro em 'leia'","ERRO SEMANTICO")
                    fila_erros.put(erro)
                else:
                    token = fila_tokens.get()
                    # print("[Sintatico] Recebeu:", token)
                    if token.simbolo == "sfecha_parenteses":
                            token = fila_tokens.get()  # consome o ')'
                            # print("[Sintatico] Recebeu :", token)
                    else:
                            erro = Erro("ERRO:esperado ')' após identificador","ERRO SINTATICO")
                            fila_erros.put(erro)
            else:
                erro = Erro(f"ERRO: variavel '{token.lexema}' não declarada","ERRO SEMANTICO")
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
    # print("[Sintatico] Recebeu:", token)

    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        # print("[Sintatico] Recebeu:", token)

        if token.simbolo == "sidentificador":
            if TS.pesquisa_var_func_tabela_inteira(token.lexema):    
                token = fila_tokens.get()
                # print("[Sintatico] Recebeu:", token)
                if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()  # consome o ')'
                    # print("[Sintatico] Recebeu:", token)
                else:
                    erro = Erro("ERRO:Erro: esperado ')' após identificador em 'escreva'","ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                erro = Erro(f"ERRO: variavel '{token.lexema}' nao declarada","ERRO SEMANTICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador apos '(' em 'escreva'","ERRO SINTATICO")
            fila_erros.put(erro) 
    else:
        erro = Erro("ERRO: esperado '(' após 'escreva'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_enquanto(token, fila_tokens,fila_erros):
    # consome o "enquanto"
    token = fila_tokens.get()
  
    # print("[Sintatico] Recebeu:", token)
    
    token = Analisa_expressao(token, fila_tokens,fila_erros)
    if token.simbolo == "sfaca":
        token = fila_tokens.get()  # consome o "faça"
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_comando_simples(token, fila_tokens,fila_erros)
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_se(token, fila_tokens,fila_erros):
    # consome o "se"
    token = fila_tokens.get()
    # print("[Sintatico] Recebeu:", token)

    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens,fila_erros)

    if token.simbolo == "sentao":
        token = fila_tokens.get()  # consome o "então"
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_comando_simples(token, fila_tokens,fila_erros)

        if token.simbolo == "ssenão":
            token = fila_tokens.get()  # consome o "senão"
            # print("[Sintatico] Recebeu:", token)
            token = Analisa_comando_simples(token, fila_tokens,fila_erros)
    else:
        erro = Erro("ERRO:esperado 'entao' após expressão no 'se'","ERRO SINTATICO")
        fila_erros.put(erro)

    return token

def Analisa_declaracao_procedimento(token, fila_tokens,fila_erros):
    # consome a palavra-chave "procedimento"
    token = fila_tokens.get()
    # print("[Sintatico] Recebeu:", token)

    if token.simbolo == "sidentificador":
        if not TS.pesquisa_declproc_tabela(token.lexema):

            # Insere o procedimento na tabela de símbolos
            TS.insere_tabela(token.lexema, "procedimento", tipo=None, nivel=None, end=None)

            # Gera um novo rótulo (USADO PARA A GERAÇÃO DE CÓDIGO)
            rotulo = TS.novo_rotulo()

            # Entra em um novo escopo (gera a marca e incrementa o escopo)
            TS.enter_scope()
            
            # consome o identificador
            token = fila_tokens.get()
            # print("[Sintatico] Recebeu:", token)
            if token.simbolo == "spontovirgula":
                # consome o ponto e vírgula
                token = fila_tokens.get()
                # print("[Sintatico] Recebeu:", token)
                # analisa o bloco do procedimento
                token = Analisa_bloco(token, fila_tokens,fila_erros)
            else:
                erro = Erro("ERRO:esperado ';' após nome do procedimento","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: procedimento '{token.lexema}' ja declarado","ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO:esperado identificador após 'procedimento'","ERRO SINTATICO")
        fila_erros.put(erro)

    # Fim do procedimento: sai do escopo
    TS.exit_scope()
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
            # print("[Sintatico] Recebeu:", token)
        else:
            erro = Erro("ERRO:esperado ';' após declaração de sub-rotina","ERRO SINTATICO")
            fila_erros.put(erro)

    return token

def Analisa_declaracao_funcao(token, fila_tokens,fila_erros):
    # Consome a palavra-chave 'funcao'
    token = fila_tokens.get()
    # print("[Sintatico] Recebeu:", token)

    if token.simbolo == "sidentificador":
        # Armazena o nome da função
        iden = token.lexema

        if not TS.pesquisa_declfunc_tabela(token.lexema):
            # Insere a função na tabela de símbolos
            TS.insere_tabela(token.lexema, "funcao", tipo=None, nivel=None, end=None)
            
            # Gera um novo rótulo (USADO PARA A GERAÇÃO DE CÓDIGO)
            rotulo = TS.novo_rotulo()

            # Entra em um novo escopo (gera a marca e incrementa o escopo)
            TS.enter_scope()

            token = fila_tokens.get()
            # print("[Sintatico] Recebeu:", token)

            # Espera ':' 
            if token.simbolo == "sdoispontos":
                token = fila_tokens.get()
                # print("[Sintatico] Recebeu:", token)

                if token.simbolo == "sinteiro" or token.simbolo == "sbooleano":
                    # Atribui o tipo de retorno da função na tabela de símbolos
                    if token.simbolo == "sinteiro":
                        # Tipo inteiro
                        TS.insere_tipo(iden, token.lexema)
                    else:
                        # Tipo booleano
                        TS.insere_tipo(iden, token.lexema)
                    
                    token = fila_tokens.get()
                    # Espera ';'
                    if token.simbolo == "spontovirgula":
                        token = fila_tokens.get()
                        # print("[Sintatico] Recebeu:", token)
                        # Chama o bloco da função
                        token = Analisa_bloco(token, fila_tokens,fila_erros)
                    else:
                        erro = Erro("ERRO:esperado ';' após declaração de função","ERRO SINTATICO")
                        fila_erros.put(erro)
                else:
                    erro = Erro("ERRO:tipo de retorno da funcao nao reconhecido","ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                erro = Erro("ERRO:esperado ':' após identificador da função","ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: funcao '{token.lexema}' ja declarada","ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO: esperado identificador após 'funcao'","ERRO SINTATICO")
        fila_erros.put(erro)

    # Fim da função: sai do escopo
    TS.exit_scope()
    return token

def Analisa_expressao(token, fila_tokens,fila_erros, var_tipo=None):
    # Primeiro analisa uma expressão simples
    token = Analisa_expressao_simples(token, fila_tokens,fila_erros, var_tipo)

    # Se encontrar operador relacional
    if token.simbolo in ["smaior", "smaiorig", "sig", "smenor", "smenorig", "sdif"]:
        print("\n\n operador relacional encontrado:", token.lexema, token.simbolo,"\n\n")
        token = fila_tokens.get()  # consome o operador
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_expressao_simples(token, fila_tokens,fila_erros, var_tipo)

    return token

def Analisa_expressao_simples(token, fila_tokens,fila_erros, var_tipo=None):
    # Consome + ou - iniciais, se houver
    if token.simbolo in ["smais", "smenos"]:
        token = fila_tokens.get()
        if not TS.verifica_tipo(token.lexema, "inteiro") and not var_tipo == "inteiro":
            erro = Erro("ERRO: operador '+' ou '-' aplicado a tipo nao inteiro","ERRO SEMANTICO")
            fila_erros.put(erro)

    # Analisa o primeiro termo
    token = Analisa_termo(token, fila_tokens,fila_erros, var_tipo)

    # Enquanto aparecer +, - ou "ou"
    while token.simbolo in ["smais", "smenos", "sou"]:
        token = fila_tokens.get()  # consome o operador
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_termo(token, fila_tokens,fila_erros, var_tipo)

    return token

def Analisa_termo(token, fila_tokens,fila_erros, var_tipo=None):
    # Analisa o primeiro fator
    token = Analisa_fator(token, fila_tokens,fila_erros, var_tipo)

    # Enquanto houver * , div ou "e"
    while token.simbolo in ["smult", "sdiv", "se"]:
        print("\n\n operador de termo encontrado:", token.lexema, token.simbolo,"\n\n")
        token = fila_tokens.get()  # consome o operador
        print("\n",token.lexema, token.simbolo,"\n")
        # print("[Sintatico] Recebeu:", token)
        token = Analisa_fator(token, fila_tokens,fila_erros, var_tipo)

    return token

def Analisa_fator(token, fila_tokens,fila_erros, var_tipo=None):
    # Variável ou funcao
    if token.simbolo == "sidentificador": # (Variável ou função)
        print("\n\n pesquisa no fator:"+ token.lexema, token.simbolo +"\n\n")
        # Verifica se é uma função ou variável
        if TS.pesquisa_tabela(token.lexema):
            if TS.get_categoria(token.lexema) == "funcao": # Verifica se é função
                if TS.verifica_tipo(token.lexema, var_tipo): # Verifica se o tipo da função corresponde ao esperado
                    # token = Analisa_chamada_funcao(token, fila_tokens,fila_erros)
                    token = fila_tokens.get()
                else:
                    erro = Erro(f"ERRO: tipo de retorno da funcao '{token.lexema}' nao corresponde ao esperado ('{var_tipo}')","ERRO SEMANTICO")
                    fila_erros.put(erro)
            else:
                # É variável
                if TS.verifica_tipo(token.lexema, var_tipo): # Verifica se o tipo da variável corresponde ao esperado
                    token = fila_tokens.get()
                    # print("[Sintatico] Recebeu:", token)
                else:
                    erro = Erro(f"ERRO: tipo da variavel '{token.lexema}' nao corresponde ao esperado ('{var_tipo}')","ERRO SEMANTICO")
                    fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: identificador '{token.lexema}' nao declarado","ERRO SEMANTICO")
            fila_erros.put(erro)
    else: 
        # É numero
        if token.simbolo == "snumero":
            token = fila_tokens.get()
            # print("[Sintatico] Recebeu:", token)
        else:
            # Verifica se o operador lógico é o nao
            if token.simbolo == "snao": 
                token = fila_tokens.get()
                # print("[Sintatico] Recebeu:", token)
                token = Analisa_fator(token, fila_tokens,fila_erros, var_tipo="booleano")
            else:
                # É expressão entre parênteses
                if token.simbolo == "sabre_parenteses":
                    print("\n",token.lexema, token.simbolo,"\n")
                    token = fila_tokens.get()
                    print("\n",token.lexema, token.simbolo,"\n")
                    # print("[Sintatico] Recebeu:", token)
                    token = Analisa_expressao(token, fila_tokens,fila_erros, var_tipo)
                    print("\n",token.lexema, token.simbolo,"\n")
                    if token.simbolo == "sfecha_parenteses":
                        token = fila_tokens.get()  # consome o ')'
                        # print("[Sintatico] Recebeu:", token)
                    else:
                        erro = Erro("ERRO: esperado ')'","ERRO SINTATICO")
                        fila_erros.put(erro)
                else:
                    if token.simbolo == "sverdadeiro" or token.simbolo == "sfalso":
                        # Verificação de tipo: o fator booleano só é permitido quando var_tipo for booleano ou None
                        if var_tipo != "booleano":
                            erro = Erro(f"ERRO: valor booleano '{token.lexema}' nao corresponde ao tipo esperado '{var_tipo}'","ERRO SEMANTICO")
                            fila_erros.put(erro)
                        
                        token = fila_tokens.get()
                    else:
                        erro = Erro("ERRO: fator invalido","ERRO SINTATICO")
                        fila_erros.put(erro)    

    return token

def Analisa_atribuicao(token, fila_tokens,fila_erros, var_tipo=None):
    token = fila_tokens.get() # consome o ':='
    # print("[Sintatico] Recebeu:", token)
    
    # Espera uma expressão do lado direito
    token = Analisa_expressao(token, fila_tokens,fila_erros, var_tipo)
    return token

# def Analisa_chamada_funcao(token, fila_tokens, fila_erros):
#     # Aqui o token recebido já deve ser um identificador
#     if token.simbolo == "sidentificador":
#         # print("[Sintatico] Chamada de funcao:", token.lexema)
#         token = fila_tokens.get()  # consome o identificador
#     else:
#         erro = Erro("ERRO: identificador esperado em chamada de função", "ERRO SINTATICO")
#         fila_erros.put(erro)

#     return token


def Chamada_procedimento(token, fila_tokens,fila_erros):
    # Aqui o token recebido já deve ser um identificador
    print("\n\n Chamada de procedimento:", token.lexema, token.simbolo +"\n\n")
    if TS.pesquisa_tabela(token.lexema) is not None:  
        print("\n\n pesquisa no procedimento:"+ token.lexema, token.simbolo +"\n\n")  
        if TS.get_categoria(token.lexema) == "procedimento":
            token = fila_tokens.get()  # consome o identificador
        else:
            erro = Erro(f"ERRO: identificador '{token.lexema}' nao é um procedimento", "ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        TS.imprimir_tabela()
        erro = Erro(f"ERRO: identificador '{token.lexema}' nao encontrado na tabela de simbolos", "ERRO SEMANTICO")
        fila_erros.put(erro)

    return token
