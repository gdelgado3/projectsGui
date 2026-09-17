from datetime import date
import sqlite3
import json


# Em storage abordamos o histórico, importamos a date, a sqlite e json.

def guardar_refeicao(alimentos,macros):
    # Abrimos uma conexão com o sqlite e depois damos um cursor a essa conexão.
    conexao=sqlite3.connect("data/historico.sqlite")
    cursor=conexao.cursor()
    # Caso a tabela não exista, criamos a tabela daquela refeição com os
    # dados de uma refeição em específico.
    cursor.execute("""CREATE TABLE IF NOT EXISTS refeicoes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        alimentos_json TEXT,
        kcal REAL,
        proteina_g REAL,
        hidratos_g REAL,
        gordura_g REAL
        )"""
    )
    # text é o texto em json dos alimentos, data_hoje a data diária.
    text=json.dumps(alimentos)
    data_hoje=date.today().isoformat()
    # O que fazemos em seguida é executar no nosso cursor/BD a inserção de
    # dados de uma refeição.
    cursor.execute("""INSERT INTO refeicoes (data, alimentos_json, kcal, proteina_g, hidratos_g, gordura_g)
        VALUES (?,?,?,?,?,?)""",(data_hoje,text,macros["kcal"],macros["proteina_g"],macros["hidratos_g"],macros["gordura_g"]))
    # Damos commit na BD e depois fechamos a conexão.
    conexao.commit()
    conexao.close()


def obter_historico_hoje():
    # Voltamos a abrir a conexão e o cursor com a base de dados da sqlite.
    conexao=sqlite3.connect("data/historico.sqlite")
    cursor=conexao.cursor()
    data_hoje=date.today().isoformat()
    # Simplesmente vamos executar/mostrar aquelas que se aplicam ao dia em
    # específico, retornando-o.
    cursor.execute("""SELECT * FROM refeicoes WHERE data = ?""",(data_hoje,))
    resultado=cursor.fetchall()
    conexao.close()
    return resultado
