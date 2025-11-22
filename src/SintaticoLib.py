from src.Erro import Erro
import src.TabelaSimbolos as TS
from src.Gera import gera

# pilha global para armazenar pares do DALLOC
pilha_dalloc = []
_rotulo_counter = 0
global alloc_counter
alloc_counter = 1


def novo_rotulo():
    """Gera e retorna um novo rótulo (string)."""
    global _rotulo_counter
    _rotulo_counter += 1
    rot = f"L{_rotulo_counter}"
    print(f"[TabelaSimbolos] Novo rotulo criado: {rot}")
    return rot


rotulo = novo_rotulo()

def Analisa_bloco(token, fila_tokens, fila_erros):
    token,n_allocs = Analisa_et_variaveis(token, fila_tokens, fila_erros)
    token = Analisa_subrotinas(token, fila_tokens, fila_erros)
    token = Analisa_comandos(token, fila_tokens, fila_erros)
    if n_allocs != 0:
        dalloc1,dalloc2 = pilha_dalloc.pop()
        gera("","DALLOC",dalloc1,dalloc2)
    return token


def Analisa_et_variaveis(token, fila_tokens, fila_erros):
    global alloc_counter
    n_allocs = 0
    if token.simbolo == "svar":
        token = fila_tokens.get()
        if token.simbolo == "sidentificador":
            while token.simbolo == "sidentificador":
                token,n_allocs = Analisa_Variaveis(token, fila_tokens, fila_erros,n_allocs)
                if token.simbolo == "spontovirgula":
                    token = fila_tokens.get()
                else:
                    erro = Erro("ERRO:etapa de variaveis", "ERRO SINTATICO")
                    fila_erros.put(erro)
        else:
            erro = Erro("ERRO:etapa de variaveis:esperando identificador", "ERRO SINTATICO")
            fila_erros.put(erro)
        
        gera("","ALLOC",alloc_counter,n_allocs)
        pilha_dalloc.append((alloc_counter,n_allocs))
        alloc_counter += n_allocs


    return token,n_allocs


def Analisa_Variaveis(token, fila_tokens, fila_erros,n_allocs):
    # lista temporária para armazenar variáveis do mesmo tipo
    lista_var = []
    while True:
        if token.simbolo == "sidentificador":
            if not TS.pesquisa_declvar_tabela(token.lexema) or not TS.pesquisa_var_func_tabela_inteira(token.lexema):
                lista_var.append(token.lexema)
                n_allocs+= 1
                TS.insere_tabela(token.lexema, "variavel", tipo=None, nivel=None, end=None,rotulo_1=None)
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

    return token,n_allocs


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
            end = TS.get_endereco(token.lexema)
            tipo_var = TS.get_tipo(token.lexema)
            token = fila_tokens.get()
            if token.simbolo == "satribuicao":
                token = Analisa_atribuicao(token, fila_tokens, fila_erros, tipo_var)
            else:
                erro = Erro("ERRO:esperado ':=' apos identificador em atribuicao", "ERRO SINTATICO")
                fila_erros.put(erro)
            gera("","STR",end,"")
        elif TS.get_categoria(token.lexema) == "funcao":
            # função: verificar se existe retorno obrigatório
            rotulo_funcao = TS.get_rotulo(token.lexema)
            tipo_func = TS.get_tipo(token.lexema)
            token = fila_tokens.get()
            if token.simbolo == "satribuicao":
                token = Analisa_atribuicao(token, fila_tokens, fila_erros, tipo_func)
                gera("","STR",0,"")
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
                    gera("","RD","","")
                    end = TS.get_endereco(token.lexema)
                    gera("","STR",end,"")
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
                end = TS.get_endereco(token.lexema)
                gera("","LDV",end,"")
                gera("","PRN","","")    
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
    global rotulo
    auxrot1 = None
    auxrot2 = None
    auxrot1 = rotulo
    gera(rotulo,"NULL","","")
    rotulo = novo_rotulo()
    token = fila_tokens.get()
    token = Analisa_expressao(token, fila_tokens, fila_erros, ["inteiro", "booleano"])
    if token.simbolo == "sfaca":
        auxrot2 = rotulo
        gera("","JMPF",rotulo,"")
        rotulo = novo_rotulo()
        token = fila_tokens.get()
        token = Analisa_comando_simples(token, fila_tokens, fila_erros)
        gera("","JMP",auxrot1,"")
        gera(auxrot2,"NULL","","")
    else:
        erro = Erro("ERRO:esperado 'faca' após expressão no 'enquanto'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_se(token, fila_tokens, fila_erros):
    global rotulo
    auxrot1 = None
    auxrot2 = None
    token = fila_tokens.get()
    # analisa a expressão condicional
    token = Analisa_expressao(token, fila_tokens, fila_erros, ["inteiro", "booleano"])

    if token.simbolo == "sentao":
        auxrot1 = rotulo
        gera("", "JMPF", rotulo, "")
        rotulo = novo_rotulo()
        token = fila_tokens.get()
        token = Analisa_comando_simples(token, fila_tokens, fila_erros)

        if token.simbolo == "ssenão":
            auxrot2 = rotulo
            gera("", "JMPF", rotulo, "")
            rotulo = novo_rotulo()
            gera(auxrot1, "NULL", "", "")
            token = fila_tokens.get()
            token = Analisa_comando_simples(token, fila_tokens, fila_erros)
            gera(auxrot2, "NULL", "", "")
        else:
            gera(auxrot1, "NULL", "", "")
    else:
        erro = Erro("ERRO:esperado 'entao' após expressão no 'se'", "ERRO SINTATICO")
        fila_erros.put(erro)
    return token


def Analisa_declaracao_procedimento(token, fila_tokens, fila_erros):
    global rotulo
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        if not TS.pesquisa_declproc_tabela(token.lexema):
            # insere o procedimento na tabela de símbolos
            TS.insere_tabela(token.lexema, "procedimento", tipo=None, nivel=None, end=None,rotulo_1=rotulo)
            # gera um novo rótulo para a geração de código
            #rotulo = TS.novo_rotulo()
            # entra em um novo escopo
            TS.enter_scope()
            gera(rotulo,"NULL","","")
            rotulo = novo_rotulo()
            
            
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
    gera("","RETURN","","")
    return token


def Analisa_subrotinas(token, fila_tokens, fila_erros):
    # enquanto o token atual for "procedimento" ou "função"
    global rotulo
    auxrot = None
    flag = 0
    if token.simbolo == "sprocedimento" or token.simbolo == "sfuncao":
        auxrot = rotulo
        gera("","JMP",rotulo,"")
        rotulo = novo_rotulo()
        flag = 1
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
    if flag == 1:
        gera(auxrot,"NULL","","")

    return token


def Analisa_declaracao_funcao(token, fila_tokens, fila_erros):
    global rotulo
    token = fila_tokens.get()

    if token.simbolo == "sidentificador":
        iden = token.lexema

        if not TS.pesquisa_declfunc_tabela(token.lexema):
            # insere a função na tabela de símbolos
            TS.insere_tabela(token.lexema, "funcao", tipo=None, nivel=None, end=0,rotulo_1=rotulo)
            # gera um novo rótulo para a geração de código
            #rotulo = TS.novo_rotulo()
            # entra em um novo escopo
            TS.enter_scope()
            rotulo_funcao = TS.get_rotulo(token.lexema)
            gera(rotulo_funcao,"NULL","","")
            rotulo = novo_rotulo()

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
    gera("","RETURN","","")
    return token


def Analisa_expressao(token, fila_tokens, fila_erros, var_tipo=None):
    # analisa uma expressão simples
    token_apos, posfixa = Converte_expressao_para_posfixa(token, fila_tokens, fila_erros)
    token = token_apos
    # verifica tipos usando a posfixa
    Verifica_tipo_posfixa(posfixa, fila_erros, var_tipo)
    gera_codigo_posfixa(posfixa,fila_erros)

    # retorna o token que veio após a expressão (compatível com seu estilo atual)
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
            rotulo_funcao = TS.get_rotulo(token.lexema)
            gera("","CALL",rotulo_funcao,"")
            token = fila_tokens.get()
        else:
            erro = Erro(f"ERRO: identificador '{token.lexema}' nao é um procedimento", "ERRO SEMANTICO")
            fila_erros.put(erro)
    else:
        erro = Erro(f"ERRO: identificador '{token.lexema}' nao encontrado na tabela de simbolos", "ERRO SEMANTICO")
        fila_erros.put(erro)

    return token

# Converte expressão a partir de `token` para pós-fixa (shunting-yard).
# Retorna (token_apos_expressao, posfixa_list)
def Converte_expressao_para_posfixa(token, fila_tokens, fila_erros):
    operadores = {
        # simbolo: (precedencia, associatividade)  associatividade: 'L' ou 'R'
        "snao": (5, 'R'),        # operador lógico unário (não)
        "uplus": (5, 'R'),       # + unário (interno)
        "uminus": (5, 'R'),      # - unário (interno)
        "smult": (4, 'L'),
        "sdiv": (4, 'L'),
        "smais": (3, 'L'),
        "smenos": (3, 'L'),
        "se": (2, 'L'),          # and
        "sou": (1, 'L'),         # or
        # relational (menor, maior, igual, dif) - menor precedencia que aritmetica
        "smaior": (0, 'L'),
        "smaiorig": (0, 'L'),
        "sig": (0, 'L'),
        "smenor": (0, 'L'),
        "smenorig": (0, 'L'),
        "sdif": (0, 'L'),
    }
    # símbolos que podem aparecer numa expressão (operandos / operadores / parênteses)
    operandos = {"sidentificador", "snumero", "sverdadeiro", "sfalso"}
    operadores_simbolos = set(operadores.keys()).union({"smais", "smenos", "smult", "sdiv", "sou", "se", "smaior","smaiorig","sig","smenor","smenorig","sdif","snao"})
    parenteses_abre = "sabre_parenteses"
    parenteses_fecha = "sfecha_parenteses"

    output = []   # lista pós-fixa (colocar tokens)
    stack = []    # stack de operadores (guardar simbolos ou tokens)

    # helper: decide se token faz parte de expressão
    def is_expr_symbol(t):
        if t is None:
            return False
        s = t.simbolo
        return s in operandos or s in operadores_simbolos or s in (parenteses_abre, parenteses_fecha)

    prev_was_operand = False  # usado para detectar operadores unários (+/-) e 'snao'

    # processa tokens até encontrar algo que não pertença à expressão
    while token is not None and is_expr_symbol(token):
        s = token.simbolo
        if s in operandos:
            # operando -> enviar para output
            output.append(token)
            prev_was_operand = True
            token = fila_tokens.get()
            continue
        if s == parenteses_abre:
            stack.append(token)   # empilha o token de '('
            prev_was_operand = False
            token = fila_tokens.get()
            continue
        if s == parenteses_fecha:
            # desempilha até encontrar '('
            found_open = False
            while stack:
                top = stack.pop()
                if top.simbolo == parenteses_abre:
                    found_open = True
                    break
                output.append(top)
            if not found_open:
                fila_erros.put(Erro("ERRO: parênteses desbalanceados - esperado '('", "ERRO SINTATICO"))
            prev_was_operand = True
            token = fila_tokens.get()
            continue

        # operador (pode ser binário ou unário)
        # detecta unário para + e - (e 'snao' sempre unário)
        if s in ("smais", "smenos"):
            if not prev_was_operand:
                # trata como unário
                s_un = "uplus" if s == "smais" else "uminus"
                # crie um "token fictício" para o operador unário - podemos reusar o token e alterar simbolo
                # mas para não mutar original, criamos um pequeno wrapper objeto usando uma cópia superficial
                token_un = token
                token_un.simbolo = s_un
                # use operadores map para precedencia (já definimos uplus/uminus)
                op_sym = s_un
                # shunting-yard: processa baseado em precedencia/associatividade
                while stack and stack[-1].simbolo in operadores and (
                    (operadores[stack[-1].simbolo][0] > operadores[op_sym][0]) or
                    (operadores[stack[-1].simbolo][0] == operadores[op_sym][0] and operadores[stack[-1].simbolo][1] == 'L')
                ):
                    output.append(stack.pop())
                stack.append(token_un)
                prev_was_operand = False
                token = fila_tokens.get()
                continue
            else:
                # binário +/-
                op_sym = s
        elif s == "snao":
            # 'nao' é sempre unário
            # usamos diretamente token (mas preferível marcar unário)
            op_sym = "snao"
        else:
            # outros operadores (binarios): smult, sdiv, se, sou, relacionais
            op_sym = s

        # shunting-yard: enquanto topo da pilha tem operador com maior precedencia (ou igual e left assoc) -> pop para output
        while stack and stack[-1].simbolo not in (parenteses_abre,):
            top_sym = stack[-1].simbolo
            if top_sym not in operadores:
                break
            prec_top, assoc_top = operadores[top_sym]
            prec_curr, assoc_curr = operadores[op_sym]
            if (prec_top > prec_curr) or (prec_top == prec_curr and assoc_curr == 'L'):
                output.append(stack.pop())
            else:
                break

        # empilha o operador atual (usar o token atual -> mas atenção, se mudou para uplus/uminus já tratamos antes)
        stack.append(token)
        prev_was_operand = False
        token = fila_tokens.get()

    # fim do loop: desempilha todo resto
    while stack:
        top = stack.pop()
        if top.simbolo == parenteses_abre or top.simbolo == parenteses_fecha:
            fila_erros.put(Erro("ERRO: parênteses desbalanceados", "ERRO SINTATICO"))
        else:
            output.append(top)

    # retorna token atual (que não faz parte da expressão) e a lista posfixa
    return token, output


# Verificação de tipos simples a partir de uma lista pós-fixa
# posfixa: lista de tokens (na ordem pós-fixa)
# var_tipo: tipo esperado (ou None se não houver expectativa)
# usa TS como na sua base para identificar tipos de identificadores
def Verifica_tipo_posfixa(posfixa, fila_erros, var_tipo=None):
    """
    Verifica tipos a partir de uma lista posfixa.
    var_tipo pode ser:
      - None -> sem expectativa
      - string -> "inteiro" ou "booleano"
      - list/tuple -> ["inteiro","booleano"]
      - string contendo representação de lista -> "['inteiro','booleano']"
    """
    stack_tipos = []

    def tipo_do_token(t):
        if t.simbolo == "snumero":
            return "inteiro"
        if t.simbolo in ("sverdadeiro", "sfalso"):
            return "booleano"
        if t.simbolo == "sidentificador":
            if not TS.pesquisa_tabela(t.lexema):
                fila_erros.put(Erro(f"ERRO: identificador '{t.lexema}' nao declarado", "ERRO SEMANTICO"))
                return None
            return TS.get_tipo(t.lexema)
        return None

    # --- normaliza var_tipo ---
    def normalize_var_tipo(vt):
        # None -> None
        if vt is None:
            return None
        # já é lista/tupla -> transformar em lista
        if isinstance(vt, (list, tuple)):
            return list(vt)
        # se for string que representa lista, tentar parsear
        if isinstance(vt, str):
            s = vt.strip()
            if s.startswith("[") and s.endswith("]"):
                try:
                    parsed = ast.literal_eval(s)
                    if isinstance(parsed, (list, tuple)):
                        return list(parsed)
                except Exception:
                    pass
            # caso comum: string simples "inteiro"
            return s
        # qualquer outro tipo -> usar direto
        return vt

    var_tipo_norm = normalize_var_tipo(var_tipo)

    # opcional: debug
    # print(f"[DEBUG] var_tipo original={var_tipo!r}, normalized={var_tipo_norm!r}")

    for t in posfixa:
        s = t.simbolo

        # operandos
        if s in ("snumero", "sverdadeiro", "sfalso", "sidentificador"):
            stack_tipos.append(tipo_do_token(t))
            continue

        # operadores unários
        if s in ("snao", "uplus", "uminus"):
            if not stack_tipos:
                fila_erros.put(Erro(f"ERRO: operador unário '{t.lexema if hasattr(t,'lexema') else s}' sem operando", "ERRO SEMANTICO"))
                continue
            operand = stack_tipos.pop()
            if operand is None:
                # já foi reportado (ex: identificador nao declarado) - apenas empilha None para continuar
                stack_tipos.append(None)
                continue
            if s == "snao":
                if operand != "booleano":
                    fila_erros.put(Erro(f"ERRO: operador 'nao' aplicado a tipo nao-booleano ('{operand}')", "ERRO SEMANTICO"))
                stack_tipos.append("booleano")
            else:  # uplus/uminus
                if operand != "inteiro":
                    fila_erros.put(Erro(f"ERRO: operador unário '+'/'-' aplicado a tipo nao-inteiro ('{operand}')", "ERRO SEMANTICO"))
                stack_tipos.append("inteiro")
            continue

        # operadores binários aritméticos
        if s in ("smult", "sdiv", "smais", "smenos"):
            if len(stack_tipos) < 2:
                fila_erros.put(Erro(f"ERRO: operador aritimético '{s}' com operandos insuficientes", "ERRO SEMANTICO"))
                continue
            b = stack_tipos.pop()
            a = stack_tipos.pop()
            if a is None or b is None:
                # se algum já estava inválido, apenas empilha None
                stack_tipos.append(None)
                continue
            if a != "inteiro" or b != "inteiro":
                fila_erros.put(Erro(f"ERRO: operador aritmético '{s}' aplicado a tipos nao inteiros ('{a}', '{b}')", "ERRO SEMANTICO"))
            stack_tipos.append("inteiro")
            continue

        # operadores lógicos
        if s in ("se", "sou"):
            if len(stack_tipos) < 2:
                fila_erros.put(Erro(f"ERRO: operador lógico '{s}' com operandos insuficientes", "ERRO SEMANTICO"))
                continue
            b = stack_tipos.pop()
            a = stack_tipos.pop()
            if a is None or b is None:
                stack_tipos.append(None)
                continue
            if a != "booleano" or b != "booleano":
                fila_erros.put(Erro(f"ERRO: operador lógico '{s}' aplicado a tipos nao-booleanos ('{a}', '{b}')", "ERRO SEMANTICO"))
            stack_tipos.append("booleano")
            continue

        # relacionais
        if s in ("smaior", "smaiorig", "sig", "smenor", "smenorig", "sdif"):
            if len(stack_tipos) < 2:
                fila_erros.put(Erro(f"ERRO: operador relacional '{s}' com operandos insuficientes", "ERRO SEMANTICO"))
                continue
            b = stack_tipos.pop()
            a = stack_tipos.pop()
            if a is None or b is None:
                stack_tipos.append(None)
                continue
            if a != "inteiro" or b != "inteiro":
                fila_erros.put(Erro(f"ERRO: operador relacional '{s}' aplicado a tipos nao inteiros ('{a}', '{b}')", "ERRO SEMANTICO"))
            stack_tipos.append("booleano")
            continue

        # caso não tratado:
        fila_erros.put(Erro(f"ERRO: operador desconhecido na posfixa '{s}'", "ERRO SEMANTICO"))

    # após avaliação, verifica consistencia com var_tipo se houver
    if len(stack_tipos) == 0:
        final_tipo = None
    else:
        final_tipo = stack_tipos[-1]

    # função auxiliar que compara final_tipo com var_tipo_norm
    def tipos_conferem(ft, vt):
        # se sem expectativa -> ok
        if vt is None:
            return True
        # se final é None (erro anterior) -> não conferir aqui, já reportado; trate como False para evitar mensagens redundantes
        if ft is None:
            return False
        # vt é lista -> checar membership
        if isinstance(vt, (list, tuple)):
            return ft in vt
        # vt é string -> comparar direto
        return ft == vt

    if var_tipo_norm is not None and final_tipo is not None and not tipos_conferem(final_tipo, var_tipo_norm):
        fila_erros.put(Erro(f"ERRO: tipo da expressao ('{final_tipo}') nao corresponde ao esperado ('{var_tipo_norm}')", "ERRO SEMANTICO"))

    return final_tipo


def gera_codigo_posfixa(posfixa, fila_erros):
    bin_ops = {
        "smais": "ADD",
        "smenos": "SUB",
        "smult": "MUL",
        "sdiv": "DIV",
        "se": "AND",    # 'e' lógico
        "sou": "OR",    # 'ou' lógico
        # relacionais: podem retornar booleano (1/0)
        "smaior": "CMA",
        "smaiorig": "CMAQ",
        "sigual": "CEQ",
        "smenor": "CME",
        "smenorig": "CMEQ",
        "sdif": "CDIF",
          # 'nao' lógico -> NOT
    }
    un_ops = {
        "uplus": None,   # + unário (não gera nada além de garantir tipo) -> não precisa de instrução
        "uminus": "NEG", # - unário -> NEG (0 - x) ou opcode NEG se suportado
        "snao": "NEG", 
    }
    # percorre a posfixa e emite instrucoes
    for t in posfixa:
        s = t.simbolo
        # operandos
        if s == "sidentificador":
            if not TS.pesquisa_tabela(t.lexema):
                fila_erros.put(Erro(f"ERRO: identificador '{t.lexema}' nao declarado", "ERRO SEMANTICO"))
            if  TS.get_categoria(t.lexema) == "funcao":
                rotulo_funcao = TS.get_rotulo(t.lexema)
                end = TS.get_endereco(t.lexema)
                gera("","CALL",rotulo_funcao,"")
                gera("", "LDV", end, "")
            else:
                end = TS.get_endereco(t.lexema)
                gera("", "LDV", end, "")
            continue
        if s == "snumero":
            gera("", "LDC", t.lexema, "")
            continue
        # operadores unarios
        if s in un_ops:
            opcode = un_ops[s]
            if opcode is None:
                # + unário: não precisa gerar instrução (por convenção), apenas ignora
                # se quiser forçar, pode gerar LDC 0 / SUB etc.
                continue
            else:
                # gera uma instrucao que opere no topo da pilha
                # exemplo: NEG (nega o topo), NOT (inverte bit lógico do topo)
                gera("", opcode, "", "")
            continue
        # operadores binarios
        if s in bin_ops:
            opcode = bin_ops[s]
            # em arquitetura de pilha, os dois operandos já foram carregados pela posfixa,
            # então só emitimos a instrucao que consome 2 valores e empilha o resultado.
            gera("", opcode, "", "")
            continue

        # caso nao mapeado
        fila_erros.put(Erro(f"ERRO: operador/desconhecido na posfixa '{s}'", "ERRO SEMANTICO"))







