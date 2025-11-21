from src.Erro import Erro
import src.TabelaSimbolos as TS


def Analisa_bloco(token, fila_tokens, fila_erros):
    token = Analisa_et_variaveis(token, fila_tokens, fila_erros)
    token = Analisa_subrotinas(token, fila_tokens, fila_erros)
    token = Analisa_comandos(token, fila_tokens, fila_erros)
    return token


def Analisa_et_variaveis(token, fila_tokens, fila_erros):
    if token.simbolo == "svar":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token = Analisa_Variaveis(token, fila_tokens, fila_erros)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                else:
                    erro = Erro("ERRO:etapa de variaveis", "ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador", "ERRO SINTATICO")
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
                token = fila_tokens.get()

                if token.simbolo == "svirgula" or token.simbolo == "sdoispontos":
                    if token.simbolo == "svirgula":
                        token = fila_tokens.get()
                        if token.simbolo == "sdoispontos":
                            erro = Erro("ERRO: ':' inesperado após ','", "ERRO SINTATICO")
                            fila_erros.put(erro)
                            break
                    else:
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

        if token.simbolo == "sdoispontos":
            break

    # analisa o tipo das variáveis
    if token.simbolo == "sdoispontos":
        token = fila_tokens.get()
        token = Analisa_Tipo(token, fila_tokens, fila_erros, lista_var)
        TS.imprimir_tabela()
    else:
        erro = Erro("ERRO: ':' esperado", "ERRO SINTATICO")
        fila_erros.put(erro)

    return token


def Analisa_Tipo(token, fila_tokens, fila_erros, lista_var):
    if token.simbolo != "sinteiro" and token.simbolo != "sbooleano":
        erro = Erro("ERRO: tipo da variavel não reconhecido", "ERRO SINTATICO")
        fila_erros.put(erro)

    # atribui o tipo para as variáveis declaradas
    TS.atribuir_tipo_variaveis(lista_var, token.lexema)
    
    token = fila_tokens.get()
    return token

    
def Analisa_comandos(token, fila_tokens, fila_erros):
    if token.simbolo == "sinicio":
        token = fila_tokens.get()
        token = Analisa_comando_simples(token, fila_tokens, fila_erros)
        while token.simbolo != "sfim":
            token = fila_tokens.get()
            if token.simbolo != "sfim":
                token = Analisa_comando_simples(token, fila_tokens, fila_erros)
        token = fila_tokens.get()
    else:
        erro = Erro("ERRO: em declarações apos programa,procedimento ou funcao", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token

    
def Analisa_comando_simples(token, fila_tokens, fila_erros):
    if token.simbolo == "sidentificador":
        # pode ser atribuição de variável, função ou chamada de procedimento
        token = Analisa_atrib_chprocedimento(token, fila_tokens, fila_erros)
    elif token.simbolo == "sse":
        token = Analisa_se(token, fila_tokens, fila_erros)
    elif token.simbolo == "senquanto":
        token = Analisa_enquanto(token, fila_tokens, fila_erros)
    elif token.simbolo == "sleia":
        token = Analisa_leia(token, fila_tokens, fila_erros)
    elif token.simbolo == "sescreva":
        token = Analisa_escreva(token, fila_tokens, fila_erros)
    else:
        token = Analisa_comandos(token, fila_tokens, fila_erros)
    return token


def Analisa_atrib_chprocedimento(token, fila_tokens, fila_erros):
    if token.simbolo == "sidentificador":
        if TS.get_categoria(token.lexema) == "variavel":
            tipo_var = TS.get_tipo(token.lexema)
            token = fila_tokens.get()
            if token.simbolo == "satribuicao":
                token = Analisa_atribuicao(token, fila_tokens, fila_erros, tipo_var)
            else:
                erro = Erro("ERRO:esperado ':=' apos identificador em atribuicao", "ERRO SINTATICO")
                fila_erros.put(erro)
        elif TS.get_categoria(token.lexema) == "funcao":
            # função: verificar se existe retorno obrigatório
            tipo_func = TS.get_tipo(token.lexema)
            token = fila_tokens.get()
            if token.simbolo == "satribuicao":
                token = Analisa_atribuicao(token, fila_tokens, fila_erros, tipo_func)
            else:
                erro = Erro("ERRO:esperado atribuir o retorno da funcao", "ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            # é chamada de procedimento
            token = Chamada_procedimento(token, fila_tokens, fila_erros)
    return token


def Analisa_leia(token, fila_tokens, fila_erros):
    token = fila_tokens.get()
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            # verifica se a variável foi declarada
            if TS.pesquisa_var_func_tabela_inteira(token.lexema):
                # verifica se a variável é do tipo inteiro
                if not TS.verifica_tipo(token.lexema, "inteiro"):
                    erro = Erro(f"ERRO: variavel '{token.lexema}' nao é do tipo inteiro em 'leia'", "ERRO SEMANTICO")
                    fila_erros.put(erro)
                else:
                    token = fila_tokens.get()
                    if token.simbolo == "sfecha_parenteses":
                        token = fila_tokens.get()
                    else:
                        erro = Erro("ERRO:esperado ')' após identificador", "ERRO SINTATICO")
                        fila_erros.put(erro)
            else:
                erro = Erro(f"ERRO: variavel '{token.lexema}' não declarada", "ERRO SEMANTICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador após '('", "ERRO SINTATICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO:esperado '(' após 'leia'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_escreva(token, fila_tokens, fila_erros):
    token = fila_tokens.get()
    if token.simbolo == "sabre_parenteses":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            if TS.pesquisa_var_func_tabela_inteira(token.lexema):    
                token = fila_tokens.get()
                if token.simbolo == "sfecha_parenteses":
                    token = fila_tokens.get()
                else:
                    erro = Erro("ERRO:esperado ')' após identificador em 'escreva'", "ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                erro = Erro(f"ERRO: variavel '{token.lexema}' nao declarada", "ERRO SEMANTICO")
                fila_erros.put(erro)
        else:
            erro = Erro("ERRO:esperado identificador apos '(' em 'escreva'", "ERRO SINTATICO")
            fila_erros.put(erro) 
    else:
        erro = Erro("ERRO: esperado '(' após 'escreva'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_enquanto(token, fila_tokens, fila_erros):
    token = fila_tokens.get()
    token = Analisa_expressao(token, fila_tokens, fila_erros, ["inteiro", "booleano"])
    if token.simbolo == "sfaca":
        token = fila_tokens.get()
        token = Analisa_comando_simples(token, fila_tokens, fila_erros)
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_se(token, fila_tokens, fila_erros):
    token = fila_tokens.get()
    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens, fila_erros, ["inteiro", "booleano"])

    if token.simbolo == "sentao":
        token = fila_tokens.get()
        token = Analisa_comando_simples(token, fila_tokens, fila_erros)

        if token.simbolo == "ssenão":
            token = fila_tokens.get()
            token = Analisa_comando_simples(token, fila_tokens, fila_erros)
    else:
        erro = Erro("ERRO:esperado 'entao' após expressão no 'se'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_declaracao_procedimento(token, fila_tokens, fila_erros):
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        if not TS.pesquisa_declproc_tabela(token.lexema):
            # insere o procedimento na tabela de símbolos
            TS.insere_tabela(token.lexema, "procedimento", tipo=None, nivel=None, end=None)
            # gera um novo rótulo para a geração de código
            rotulo = TS.novo_rotulo()
            # entra em um novo escopo
            TS.enter_scope()
            
            token = fila_tokens.get()
            if token.simbolo == "spontovirgula":
                token = fila_tokens.get()
                # analisa o bloco do procedimento
                token = Analisa_bloco(token, fila_tokens, fila_erros)
            else:
                erro = Erro("ERRO:esperado ';' após nome do procedimento", "ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: procedimento '{token.lexema}' ja declarado", "ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO:esperado identificador após 'procedimento'", "ERRO SINTATICO")
        fila_erros.put(erro)

    # sai do escopo ao fim do procedimento
    TS.exit_scope()
    return token


def Analisa_subrotinas(token, fila_tokens, fila_erros):
    # enquanto o token atual for "procedimento" ou "função"
    while token.simbolo == "sprocedimento" or token.simbolo == "sfuncao":
        if token.simbolo == "sprocedimento":
            token = Analisa_declaracao_procedimento(token, fila_tokens, fila_erros)
        else:
            token = Analisa_declaracao_funcao(token, fila_tokens, fila_erros)

        # após a declaração, deve vir ponto e vírgula
        if token.simbolo == "spontovirgula":
            token = fila_tokens.get()
        else:
            erro = Erro("ERRO:esperado ';' após declaração de sub-rotina", "ERRO SINTATICO")
            fila_erros.put(erro)

    return token


def Analisa_declaracao_funcao(token, fila_tokens, fila_erros):
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        iden = token.lexema

        if not TS.pesquisa_declfunc_tabela(token.lexema):
            # insere a função na tabela de símbolos
            TS.insere_tabela(token.lexema, "funcao", tipo=None, nivel=None, end=None)
            # gera um novo rótulo para a geração de código
            rotulo = TS.novo_rotulo()
            # entra em um novo escopo
            TS.enter_scope()

            token = fila_tokens.get()

            # espera ':' 
            if token.simbolo == "sdoispontos":
                token = fila_tokens.get()

                if token.simbolo == "sinteiro" or token.simbolo == "sbooleano":
                    # atribui o tipo de retorno da função
                    TS.insere_tipo(iden, token.lexema)
                    
                    token = fila_tokens.get()
                    # espera ';'
                    if token.simbolo == "spontovirgula":
                        token = fila_tokens.get()
                        # chama o bloco da função
                        token = Analisa_bloco(token, fila_tokens, fila_erros)
                    else:
                        erro = Erro("ERRO:esperado ';' após declaração de função", "ERRO SINTATICO")
                        fila_erros.put(erro)
                else:
                    erro = Erro("ERRO:tipo de retorno da funcao nao reconhecido", "ERRO SINTATICO")
                    fila_erros.put(erro)
            else:
                erro = Erro("ERRO:esperado ':' após identificador da função", "ERRO SINTATICO")
                fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: funcao '{token.lexema}' ja declarada", "ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro("ERRO: esperado identificador após 'funcao'", "ERRO SINTATICO")
        fila_erros.put(erro)

    # sai do escopo ao fim da função
    TS.exit_scope()
    return token


def Analisa_expressao(token, fila_tokens, fila_erros, var_tipo=None):
    # analisa uma expressão simples
    token = Analisa_expressao_simples(token, fila_tokens, fila_erros, var_tipo)

    # se encontrar operador relacional
    if token.simbolo in ["smaior", "smaiorig", "sig", "smenor", "smenorig", "sdif"]:
        token = fila_tokens.get()
        token = Analisa_expressao_simples(token, fila_tokens, fila_erros, var_tipo)

    return token


def Analisa_expressao_simples(token, fila_tokens, fila_erros, var_tipo=None):
    # consome + ou - iniciais, se houver
    if token.simbolo in ["smais", "smenos"]:
        token = fila_tokens.get()
        if not TS.verifica_tipo(token.lexema, "inteiro") and not var_tipo == "inteiro":
            erro = Erro("ERRO: operador '+' ou '-' aplicado a tipo nao inteiro", "ERRO SEMANTICO")
            fila_erros.put(erro)

    # analisa o primeiro termo
    token = Analisa_termo(token, fila_tokens, fila_erros, var_tipo)

    # enquanto aparecer +, - ou "ou"
    while token.simbolo in ["smais", "smenos", "sou"]:
        token = fila_tokens.get()
        token = Analisa_termo(token, fila_tokens, fila_erros, var_tipo)

    return token


def Analisa_termo(token, fila_tokens, fila_erros, var_tipo=None):
    # analisa o primeiro fator
    token = Analisa_fator(token, fila_tokens, fila_erros, var_tipo)

    # enquanto houver *, div ou "e"
    while token.simbolo in ["smult", "sdiv", "se"]:
        token = fila_tokens.get()
        token = Analisa_fator(token, fila_tokens, fila_erros, var_tipo)

    return token


def Analisa_fator(token, fila_tokens, fila_erros, var_tipo=None):
    # variável ou função
    if token.simbolo == "sidentificador":
        # verifica se é uma função ou variável
        if TS.pesquisa_tabela(token.lexema):
            if TS.get_categoria(token.lexema) == "funcao":
                # verifica se o tipo da função corresponde ao esperado
                if TS.verifica_tipo(token.lexema, var_tipo):
                    token = fila_tokens.get()
                else:
                    erro = Erro(f"ERRO: tipo de retorno da funcao '{token.lexema}' nao corresponde ao esperado ('{var_tipo}')", "ERRO SEMANTICO")
                    fila_erros.put(erro)
            else:
                # é variável
                if TS.verifica_tipo(token.lexema, var_tipo):
                    token = fila_tokens.get()
                else:
                    erro = Erro(f"ERRO: tipo da variavel '{token.lexema}' nao corresponde ao esperado ('{var_tipo}')", "ERRO SEMANTICO")
                    fila_erros.put(erro)
        else:
            erro = Erro(f"ERRO: identificador '{token.lexema}' nao declarado", "ERRO SEMANTICO")
            fila_erros.put(erro)
    elif token.simbolo == "snumero":
        # é número
        token = fila_tokens.get()
    elif token.simbolo == "snao":
        # operador lógico "não"
        token = fila_tokens.get()
        token = Analisa_fator(token, fila_tokens, fila_erros, var_tipo="booleano")
    elif token.simbolo == "sabre_parenteses":
        # expressão entre parênteses
        token = fila_tokens.get()
        token = Analisa_expressao(token, fila_tokens, fila_erros, var_tipo)
        if token.simbolo == "sfecha_parenteses":
            token = fila_tokens.get()
        else:
            erro = Erro("ERRO: esperado ')'", "ERRO SINTATICO")
            fila_erros.put(erro)
    elif token.simbolo == "sverdadeiro" or token.simbolo == "sfalso":
        # valor booleano
        if var_tipo != "booleano":
            erro = Erro(f"ERRO: valor booleano '{token.lexema}' nao corresponde ao tipo esperado '{var_tipo}'", "ERRO SEMANTICO")
            fila_erros.put(erro)
        token = fila_tokens.get()
    else:
        erro = Erro("ERRO: fator invalido", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_atribuicao(token, fila_tokens, fila_erros, var_tipo=None):
    token = fila_tokens.get()
    # espera uma expressão do lado direito
    token = Analisa_expressao(token, fila_tokens, fila_erros, var_tipo)
    return token


def Chamada_procedimento(token, fila_tokens, fila_erros):
    # o token recebido já deve ser um identificador
    if TS.pesquisa_tabela(token.lexema) is not None:  
        if TS.get_categoria(token.lexema) == "procedimento":
            token = fila_tokens.get()
        else:
            erro = Erro(f"ERRO: identificador '{token.lexema}' nao é um procedimento", "ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro(f"ERRO: identificador '{token.lexema}' nao encontrado na tabela de simbolos", "ERRO SEMANTICO")
        fila_erros.put(erro)

    return token
