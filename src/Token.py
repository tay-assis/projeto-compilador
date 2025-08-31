class Token:
    def __init__(self, lexema, simbolo):
        self.lexema = lexema
        self.simbolo = simbolo

    def __repr__(self):
        return f"Token(lexema='{self.lexema}', simbolo='{self.simbolo}')"
