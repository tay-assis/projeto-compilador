from AnalisadorLexical import AnalisadorLexico

if __name__ == "__main__":
    analisador = AnalisadorLexico("programa2.txt")
    analisador.analisar()
    analisador.salvar_tokens() # salva no txt