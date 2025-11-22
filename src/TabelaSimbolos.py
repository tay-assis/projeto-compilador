# ============================================
# TabelaSimbolos.py - implementação (Modelo 1)
# Implementação baseada no material do professor
# Cada entrada: lexema, categoria, tipo, nivel, end
# categoria: "variavel", "procedimento", "funcao", "programa", "marcador"
# end: endereço (para variáveis e funções)
# ============================================

# Tabela (pilha)
tabela_simbolos = []
topo = -1

# Nível léxico atual (0 = programa)
nivel_atual = -1   # começa em -1; ao abrir programa deve chamar enter_scope() para nivel 0

# Endereço global
endereco_global = 1

# Contador de rótulos (para geração de código)


# ===========================
# Reiniciar tabela (usar no início do analisador)
# ===========================
def resetar_tabela():
    """Limpa a tabela e reseta contadores. Deve ser chamado no início da compilação."""
    global tabela_simbolos, topo, nivel_atual, endereco_global, _rotulo_counter
    tabela_simbolos.clear()
    topo = -1
    nivel_atual = -1
    endereco_global = 1
    print("[TabelaSimbolos] Tabela reiniciada.")


# ===========================
# Controle de escopo (enter/exit)
# ===========================
def enter_scope():
    """
    Entra em um novo escopo:
    - incrementa nivel_atual
    - inicializa endereçamento para esse nível
    - insere marcador na tabela
    Retorna o novo nível.
    """
    global nivel_atual
    nivel_atual += 1
    push_marcador(nivel_atual)
    print(f"[TabelaSimbolos] Entrou em escopo, nivel_atual={nivel_atual}")
    return nivel_atual

def exit_scope():
    """
    Sai do escopo atual:
    - desempilha símbolos até o marcador
    - remove o contador de endereçamento do nível
    - decrementa nivel_atual
    Retorna o nível antigo (aquele que foi fechado).
    """
    global nivel_atual
    nivel_fechado = nivel_atual
    fechar_escopo()
    nivel_atual -= 1
    print(f"[TabelaSimbolos] Saiu do escopo, novo nivel_atual={nivel_atual}")
    return nivel_fechado


# ===========================
# Inserção genérica na tabela
# ===========================
def insere_tabela(lexema, categoria, tipo=None, nivel=None, end=None,rotulo_1=None):
    """
    Insere um símbolo na tabela.
    - lexema: string
    - categoria: "variavel", "procedimento", "funcao", "programa", "marcador"
    - tipo: "inteiro"/"booleano"/None (ou "programa" para nome de programa)
    - nivel: se None, será usado nivel_atual (recomendado)
    - end: adiciona o endereço (variável e função).
    """
    global topo, tabela_simbolos, nivel_atual, endereco_global

    if nivel is None:
        nivel = nivel_atual

    # Variáveis recebem endereço (offset) por nível
    if categoria == "variavel":
        end = endereco_global
        endereco_global += 1
        print(f"[Semantico] Atribuido endereco {end} para variavel '{lexema}' no nivel {nivel}")
    # Para função retorna o rótulo diretamente e adiciona o endereço da função na tabela
    elif categoria == "funcao":
        if end is None:
            end = endereco_global
            endereco_global += 1
            rotulo = rotulo_1
    
    elif categoria == "procedimento":
            rotulo = rotulo_1
    


    simbolo = {
        "lexema": lexema,
        "categoria": categoria,
        "tipo": tipo,
        "nivel": nivel,
        "end": end,
        "rotulo":rotulo_1
    }

    tabela_simbolos.append(simbolo)
    topo += 1
    print(f"[TabelaSimbolos] Inserido: {simbolo}")


# ===========================
# Remover último símbolo
# ===========================
def pop_simbolo():
    """Remove o símbolo do topo (se existir) e atualiza topo."""
    global topo, tabela_simbolos
    if topo >= 0:
        removido = tabela_simbolos.pop()
        topo -= 1
        print(f"[TabelaSimbolos] Removido: {removido}")
        return removido
    return None


# ===========================
# Marcador de escopo
# ===========================
def push_marcador(nivel):
    """Insere um marcador de escopo na tabela (categoria 'marcador')."""
    insere_tabela("marcador", "marcador", tipo=None, nivel=nivel, end=None,rotulo_1=None)


# ===========================
# Fechar escopo (desempilha até marcador)
# ===========================
def fechar_escopo():
    """
    - Remove da tabela todos os símbolos até encontrar o marcador correspondente.
    - Usa-se quando se fecha um bloco (procedimento, função, bloco inicio/fim, etc).
    """
    global topo
    print("[TabelaSimbolos] Fechando escopo (desempilhando ate marcador)...")
    while topo >= 0 and tabela_simbolos[topo]["categoria"] != "marcador":
        pop_simbolo()
    # remover o marcador também (se existir)
    if topo >= 0 and tabela_simbolos[topo]["categoria"] == "marcador":
        pop_simbolo()
    print("[TabelaSimbolos] Escopo fechado.")


# ===========================
# PESQUISAS (conformes no material do professor)
# ===========================

def pesquisa_declvar_tabela(lexema):
    """
    - Pesquisa se lexema já foi declarado como variável no ESCOPO atual.
    - Procura de cima para baixo; para ao encontrar marcador (fim do bloco atual).
    - Retorna True se declarado no mesmo bloco, False caso contrário.
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["categoria"] == "marcador":
            return False
        if simbolo["lexema"] == lexema and simbolo["categoria"] == "variavel":
            print(f"[Semantico] pesquisa_declvar_tabela: '{lexema}' ja declarado neste bloco.")
            return True
    return False


def pesquisa_declproc_tabela(lexema):
    """
    - Procura se um procedimento já foi declarado.
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema and simbolo["categoria"] == "procedimento":
            print(f"[TS] procedimento '{lexema}' já declarado neste bloco.")
            return True
    return False


def pesquisa_declfunc_tabela(lexema):
    """
    - Procura se uma função já foi declarada.
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema and simbolo["categoria"] == "funcao":
            print(f"[Semantico] funcao '{lexema}' ja declarada neste bloco.")
            return True
    return False


def pesquisa_tabela(lexema):
    """
    - Pesquisa qualquer símbolo (variável, procedimento, função, etc) do topo para baixo.
    - Retorna a entrada (dicionário) se encontrada; 
    - None caso contrário.
    - NÃO para no marcador (porque pode estar em escopo externo).
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema:
            print(f"[Semantico] pesquisa_tabela: encontrado {simbolo}")
            return simbolo
    print(f"[Semantico] pesquisa_tabela: '{lexema}' nao encontrado.")
    return None

def pesquisa_var_func_tabela_inteira(lexema):
    """
    - Pesquisa se lexema foi declarado como variável e função em qualquer escopo.
    - Retorna True se declarado, False caso contrário.
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema and simbolo["categoria"] == "variavel":
            print(f"[Semantico] pesquisa_var_func_tabela_inteira: '{lexema}' ja declarado.")
            return True
        if simbolo["lexema"] == lexema and simbolo["categoria"] != "funcao":
            return True
    return False


# ===========================
# Atribuição de tipo
# ===========================
def atribuir_tipo_variaveis(lista_vars, tipo):
    """
    - Atualiza o campo 'tipo' para todas as variáveis em lista_vars.
    - Procura do topo para baixo e atualiza a primeira ocorrência de cada var.
    """
    if not lista_vars:
        return
    for var in lista_vars:
        atualizado = False
        for simbolo in reversed(tabela_simbolos):
            if simbolo["lexema"] == var and simbolo["categoria"] == "variavel":
                simbolo["tipo"] = tipo
                print(f"[Semantico] Tipo de '{var}' atualizado para '{tipo}'")
                atualizado = True
                break
        if not atualizado:
            print(f"[Semantico] AVISO: variavel '{var}' nao encontrada para atribuir tipo '{tipo}'.")


def insere_tipo(lexema, tipo):
    """
    Atualiza o tipo do símbolo cujo lexema é dado (usado para funções, ou para variáveis individuais).
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema:
            simbolo["tipo"] = tipo
            print(f"[Semantico] insere_tipo: tipo atualizado: {simbolo}")
            return
    print(f"[Semantico] insere_tipo: simbolo '{lexema}' nao encontrado.")

def verifica_tipo(lexema, tipo_esperado):
    """
    Verifica se o símbolo com o lexema dado tem o tipo esperado.
    'tipo_esperado' pode ser um string ("inteiro"/"booleano")
    ou uma lista de tipos permitidos (ex: ["inteiro", "booleano"]).
    """
    simbolo = pesquisa_tabela(lexema)
    if simbolo is None:
        print(f"[Semantico] verifica_tipo: simbolo '{lexema}' nao encontrado.")
        return False

    tipo_real = simbolo["tipo"]

    # Se tipo_esperado for lista → aceitar qualquer um
    if isinstance(tipo_esperado, list):
        if tipo_real in tipo_esperado:
            print(f"[Semantico] verifica_tipo: tipo de '{lexema}' = '{tipo_real}' confere com um dos tipos permitidos {tipo_esperado}.")
            return True
        else:
            print(f"[Semantico] verifica_tipo: tipo de '{lexema}' = '{tipo_real}' NAO confere com nenhum dos tipos permitidos {tipo_esperado}.")
            return False

    # Caso contrário → comparação normal
    if tipo_real == tipo_esperado:
        print(f"[Semantico] verifica_tipo: tipo de '{lexema}' confere com '{tipo_esperado}'.")
        return True
    else:
        print(f"[Semantico] verifica_tipo: tipo de '{lexema}' ('{tipo_real}') NAO confere com '{tipo_esperado}'.")
        return False

    
def get_categoria(lexema):
    """
    Retorna a categoria do símbolo com o lexema dado, ou None se não encontrado.
    """
    simbolo = pesquisa_tabela(lexema)
    if simbolo is not None:
        return simbolo["categoria"]
    return None

def get_tipo(lexema):
    """
    Retorna o tipo do símbolo com o lexema dado, ou None se não encontrado.
    """
    simbolo = pesquisa_tabela(lexema)
    if simbolo is not None:
        return simbolo["tipo"]
    return None

def get_endereco(lexema):

    simbolo = pesquisa_tabela(lexema)
    if simbolo is not None:
        return simbolo["end"]
    return None

def get_rotulo(lexema):

    simbolo = pesquisa_tabela(lexema)
    if simbolo is not None:
        return simbolo["rotulo"]
    return None

def get_dalloc():
    end_ini = 0
    end_fim = 0

    for simbolo in reversed(tabela_simbolos):
        if(nivel_atual != simbolo["nivel"]):
            break
        print(simbolo)
        if simbolo["end"] != None:
            end_ini == simbolo["end"]
            break
    
    for simbolo in reversed(tabela_simbolos):
        if(nivel_atual != simbolo["nivel"]):
            break
        print(simbolo)
        end_fim+=1
    end_fim -=1
    return end_ini,end_fim




# ===========================
# Funções auxiliares de leitura da tabela
# ===========================
def obter_tabela():
    """Retorna a lista interna (cópia superficial) - útil para debug/visualização."""
    return list(tabela_simbolos)

def imprimir_tabela():
    """Imprime a tabela de símbolos no estado atual (para debug)."""
    print("========== TABELA DE SIMBOLOS ==========")
    for i, s in enumerate(tabela_simbolos):
        print(f"{i}: {s}")
    print("========================================")

# Fim do arquivo