from src.AnalisadorLexical import AnalisadorLexico

if __name__ == "__main__":
    arquivo_input = "exemplos/programa2.txt"
    arquivo_output = "outputs/tokens.txt"

    analisador = AnalisadorLexico(arquivo_input)
    analisador.analisar()
    analisador.salvar_tokens(arquivo_output)