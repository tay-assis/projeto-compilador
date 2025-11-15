tabela_simbolos = []
topo = -1

def resetar_tabela():
    global tabela_simbolos, topo
    tabela_simbolos.clear()
    topo = -1
    print("[TabelaSimbolos] Tabela reiniciada.")

def insere_tabela(lexema, tipo, nivel, info):
    global topo, tabela_simbolos
    simbolo = {
        "lexema": lexema,
        "tipo": tipo,
        "nivel": nivel,
        "info": info
    }
    tabela_simbolos.append(simbolo)
    print(f"[TabelaSimbolos] Simbolo adicionado: {simbolo}")
    topo += 1

def atribuir_tipo_variaveis(lista_vars, tipo):
    global tabela_simbolos

    for var in lista_vars:
        for simbolo in reversed(tabela_simbolos):
            if simbolo["lexema"] == var:
                simbolo["tipo"] = tipo
                print(f"[TabelaSimbolos] Tipo de '{var}' atualizado para '{tipo}'")
                break

def pop_simbolo():
    global topo, tabela_simbolos
    if topo >= 0:
        tabela_simbolos.pop()
        topo -= 1

# def pesquisa_duplicvar_tabela(lexema, nivel):
#     for simbolo in reversed(tabela_simbolos):
#         if simbolo["nivel"] < nivel:
#             print(f"[TabelaSimbolos] Simbolo '{lexema}' nao encontrado no nivel {nivel}.")
#             break
#         if simbolo["lexema"] == lexema:
#             print(f"[TabelaSimbolos] Simbolo encontrado no nivel {nivel}: {simbolo}")
#             return True
#     return False

def pesquisa_duplicvar_tabela(lexema):
    for simbolo in reversed(tabela_simbolos):
        if simbolo["lexema"] == lexema:
            print(f"[TabelaSimbolos] Simbolo encontrado: {simbolo}")
            return simbolo
    return None

def push_marcador(nivel):
    insere_tabela("marcador", None, nivel, None)

def fechar_escopo():
    global topo
    while topo >= 0 and tabela_simbolos[topo]["lexema"] != "marcador":
        pop_simbolo()
    pop_simbolo()
