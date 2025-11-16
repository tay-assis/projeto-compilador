# ============================================
# TabelaSimbolos.py - implementação (Modelo 1)
# Implementação baseada no material do professor
# Cada entrada: lexema, categoria, tipo, nivel, info
# categoria: "variavel", "procedimento", "funcao", "programa", "marcador"
# info: endereço (para variáveis) ou rótulo (para procedimentos/funções) ou None
# ============================================

# Tabela (pilha)
tabela_simbolos = []
topo = -1

# Nível léxico atual (0 = programa)
nivel_atual = -1   # começa em -1; ao abrir programa deve chamar enter_scope() para nivel 0

# Controle de endereçamento por nível: endereco (offset) cresce conforme variáveis inseridas
enderecos_por_nivel = {}  # dict: nivel -> proximo_offset (int)

# Contador de rótulos (para geração de código)
_rotulo_counter = 0

# ===========================
# Funções utilitárias
# ===========================

def _novo_rotulo():
    """Gera e retorna um novo rótulo (string)."""
    global _rotulo_counter
    _rotulo_counter += 1
    rot = f"L{_rotulo_counter}"
    print(f"[TabelaSimbolos] Novo rotulo criado: {rot}")
    return rot

def iniciar_enderecamento_para_nivel(nivel):
    """Inicializa o contador de endereços para um nível (se ainda não existir)."""
    if nivel not in enderecos_por_nivel:
        enderecos_por_nivel[nivel] = 0
        print(f"[TabelaSimbolos] Enderecamento iniciado para nivel {nivel} (offset=0)")

def liberar_enderecamento_nivel(nivel):
    """Remove contador de endereços de um nível (quando fechar o escopo)."""
    if nivel in enderecos_por_nivel:
        del enderecos_por_nivel[nivel]
        print(f"[TabelaSimbolos] Enderecamento removido para nivel {nivel}")


# ===========================
# Reiniciar tabela (usar no início do analisador)
# ===========================
def resetar_tabela():
    """Limpa a tabela e reseta contadores. Deve ser chamado no início da compilação."""
    global tabela_simbolos, topo, nivel_atual, enderecos_por_nivel, _rotulo_counter
    tabela_simbolos.clear()
    topo = -1
    nivel_atual = -1
    enderecos_por_nivel = {}
    _rotulo_counter = 0
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
    iniciar_enderecamento_para_nivel(nivel_atual)
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
    liberar_enderecamento_nivel(nivel_fechado)
    nivel_atual -= 1
    print(f"[TabelaSimbolos] Saiu do escopo, novo nivel_atual={nivel_atual}")
    return nivel_fechado


# ===========================
# Inserção genérica na tabela
# ===========================
def insere_tabela(lexema, categoria, tipo=None, nivel=None, info=None):
    """
    Insere um símbolo na tabela.
    - lexema: string
    - categoria: "variavel", "procedimento", "funcao", "programa", "marcador"
    - tipo: "inteiro"/"booleano"/None (ou "programa" para nome de programa)
    - nivel: se None, será usado nivel_atual (recomendado)
    - info: se categoria == "variavel" -> será calculado como offset no nivel;
            se categoria in ["procedimento","funcao"] e info is None -> atribui rótulo automaticamente.
    """
    global topo, tabela_simbolos, nivel_atual

    if nivel is None:
        nivel = nivel_atual

    # Variáveis recebem endereço (offset) por nível
    if categoria == "variavel":
        # if nivel is None:
        #     raise RuntimeError("insere_tabela: nivel é None ao inserir variável")
        iniciar_enderecamento_para_nivel(nivel)
        endereco = enderecos_por_nivel[nivel]
        info = endereco
        enderecos_por_nivel[nivel] += 1
        print(f"[TabelaSimbolos] Atribuido endereco {info} para variavel '{lexema}' no nivel {nivel}")

    # Procedimento/Função recebem rótulo se não fornecido
    if categoria in ("procedimento", "funcao"):
        if info is None:
            info = _novo_rotulo()

    simbolo = {
        "lexema": lexema,
        "categoria": categoria,
        "tipo": tipo,
        "nivel": nivel,
        "info": info
    }

    tabela_simbolos.append(simbolo)
    topo += 1
    print(f"[TabelaSimbolos] Inserido: {simbolo}")

    return topo  # retorna índice onde foi inserido (útil)


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
    insere_tabela("marcador", "marcador", tipo=None, nivel=nivel, info=None)


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
            print(f"[TabelaSimbolos] pesquisa_declvar_tabela: '{lexema}' ja declarado neste bloco.")
            return True
    return False


def pesquisa_declproc_tabela(lexema):
    """
    - Pesquisa se procedimento já foi declarado no nível 0 (programa).
    - Retorna True se já existe.
    """
    for simbolo in tabela_simbolos:
        if simbolo["nivel"] == 0 and simbolo["categoria"] == "procedimento":
            if simbolo["lexema"] == lexema:
                print(f"[TabelaSimbolos] pesquisa_declproc_tabela: procedimento '{lexema}' ja declarado.")
                return True
    return False


def pesquisa_declfunc_tabela(lexema):
    """
    - Pesquisa se função já foi declarada no nível 0 (programa).
    - Retorna True se já existe.
    """
    for simbolo in tabela_simbolos:
        if simbolo["nivel"] == 0 and simbolo["categoria"] == "funcao":
            if simbolo["lexema"] == lexema:
                print(f"[TabelaSimbolos] pesquisa_declfunc_tabela: funcao '{lexema}' ja declarada.")
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
            print(f"[TabelaSimbolos] pesquisa_tabela: encontrado {simbolo}")
            return simbolo
    print(f"[TabelaSimbolos] pesquisa_tabela: '{lexema}' nao encontrado.")
    return None


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
                print(f"[TabelaSimbolos] Tipo de '{var}' atualizado para '{tipo}'")
                atualizado = True
                break
        if not atualizado:
            print(f"[TabelaSimbolos] AVISO: variavel '{var}' nao encontrada para atribuir tipo '{tipo}'.")


def insere_tipo(lexema, tipo):
    """
    Atualiza o tipo do símbolo cujo lexema é dado (usado para funções, ou para variáveis individuais).
    """
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema:
            simbolo["tipo"] = tipo
            print(f"[TabelaSimbolos] insere_tipo: tipo atualizado: {simbolo}")
            return
    print(f"[TabelaSimbolos] insere_tipo: simbolo '{lexema}' nao encontrado.")


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