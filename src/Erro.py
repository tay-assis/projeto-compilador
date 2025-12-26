class Erro:
    def __init__(self, mensagem, tipo):
        self.mensagem = mensagem  # texto do erro
        self.tipo = tipo          # tipo do erro

    def __repr__(self):
        return f"ErroCompilador(tipo='{self.tipo}', mensagem='{self.mensagem}')"