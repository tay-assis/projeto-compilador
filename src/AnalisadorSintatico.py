def AnalisadorSintatico(fila_tokens):
    print("[Sintático] Iniciado, aguardando tokens...")
    while True:
        token = fila_tokens.get()  # Bloqueia até ter algo na fila
        if token is None:  # Sinal de fim
            print("[Sintático] Fim dos tokens. Encerrando.")
            break
        print("[Sintático] Recebeu:", token)