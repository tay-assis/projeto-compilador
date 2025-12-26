# Compilador Simples

As etapas de construção do compilador são:
1. **Análise Léxica**: Esta etapa envolve a leitura do código-fonte e a conversão em tokens. Cada token representa uma unidade significativa, como palavras-chave, identificadores, operadores e literais.
2. **Análise Sintática**: Nesta fase, os tokens gerados na análise léxica são organizados em uma estrutura hierárquica chamada árvore sintática (AST - Abstract Syntax Tree). A árvore representa a estrutura gramatical do código-fonte.
3. **Análise Semântica**: Esta etapa verifica se a árvore sintática está semanticamente correta. Isso inclui a verificação de tipos, escopo de variáveis e outras regras semânticas do idioma.
4. **Geração de Código Intermediário**: A partir da árvore sintática, um código intermediário é gerado. Este código é uma representação abstrata do programa que facilita a otimização e a geração de código final.
5. **Geração de Código Final**: Finalmente, o código intermediário otimizado é traduzido para o código de máquina ou outro formato de saída desejado, como bytecode ou código assembly.