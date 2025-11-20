def gera(rotulo, opcode, valor="", velor2=""):
    # monta a linha
    parts = [] #lista com os componentes da instrução
    if rotulo:
        parts.append(str(rotulo))
    if opcode:
        parts.append(str(opcode))
    if valor != "" and valor is not None:
        parts.append(str(valor))
    if velor2 != "" and velor2 is not None:
        parts.append(str(velor2))

    linha = " ".join(parts) + "\n" #separa os componentes e pula a linha

    # abre o arquivo em modo append (acrescentar)
    with open("saida.obj", "a", encoding="utf-8") as f:
        f.write(linha)