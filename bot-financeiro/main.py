
from src.db import criar_tabelas, cursor_dados
from src.ingestao import correr_bot_completo

if __name__=="__main__":
    criar_tabelas()
    resultado=correr_bot_completo(cursor_dados)
    print(f"{len(resultado)} alertas enviados")
