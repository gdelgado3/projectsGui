import sqlite3
def criar_tabelas():
    conexao=sqlite3.connect("data/bot_financeiro.db")
    cursor=conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS empresas(id INTEGER PRIMARY KEY,symbol TEXT,nome TEXT,sector TEXT)") #fixo
    cursor.execute("CREATE TABLE IF NOT EXISTS dados_financeiros(id INTEGER PRIMARY KEY,empresa_id  INTEGER REFERENCES empresas(id),ano INTEGER,totalCurrentAssets INTEGER,totalLiabilities INTEGER,totalStockholdersEquity INTEGER,netIncome INTEGER,eps REAL,revenue INTEGER)")#anual variavel
    cursor.execute("CREATE TABLE IF NOT EXISTS dividendos(id INTEGER PRIMARY KEY,empresa_id  INTEGER REFERENCES empresas(id),data TEXT,dividend REAL,yield REAL,frequency TEXT)")#trianual variavel
    cursor.execute("CREATE TABLE IF NOT EXISTS pontuacoes(id INTEGER PRIMARY KEY,dados_financeiros_id INTEGER REFERENCES dados_financeiros(id),data_calculo TEXT,market_cap_usado REAL,score_net_net REAL,score_pvc REAL,score_pe REAL,score_dividend_yield REAL,pontuacao_final REAL,preco_por_acao REAL)")


conexao_dados_financeiros=sqlite3.connect("data/bot_financeiro.db")
cursor_dados=conexao_dados_financeiros.cursor()

def buscar_dados_financeiros_recentes(cursor_dados,empresas_id):
    busca_cursor_dados=cursor_dados.execute("SELECT * FROM dados_financeiros WHERE empresa_id=? ORDER BY ano DESC LIMIT 1",(empresas_id,))
    dados_mais_recentes=busca_cursor_dados.fetchone()
    return dados_mais_recentes

def inserir_empresa(cursor_dados,symbol,nome,sector):
    insercao_empresa=cursor_dados.execute("INSERT INTO empresas(symbol,nome,sector) VALUES (?,?,?)",(symbol,nome,sector))
    conexao_dados_financeiros.commit()
    id_da_empresa=insercao_empresa.lastrowid
    return id_da_empresa  

def inserir_dados_financeiros(cursor_dados, empresa_id, ano, totalCurrentAssets, totalLiabilities, totalStockholdersEquity, netIncome, eps, revenue):
    busca=buscar_dados_financeiros_recentes(cursor_dados,empresa_id)
    if busca is None:
        insercao_dados=cursor_dados.execute("INSERT INTO dados_financeiros(empresa_id, ano, totalCurrentAssets, totalLiabilities, totalStockholdersEquity, netIncome, eps, revenue) VALUES (?,?,?,?,?,?,?,?)",(empresa_id,ano, totalCurrentAssets, totalLiabilities, totalStockholdersEquity, netIncome, eps, revenue))
        id_dados=insercao_dados.lastrowid
    else:
        id_dados=busca[0]
    conexao_dados_financeiros.commit()
    return id_dados

def inserir_dividendo(cursor_dados, empresa_id, data, dividend, yield_, frequency):
    insercao_dividendos=cursor_dados.execute("INSERT INTO dividendos(empresa_id, data, dividend, yield, frequency) VALUES (?,?,?,?,?)",(empresa_id, data, dividend, yield_, frequency))
    conexao_dados_financeiros.commit()
    id_dividendos=insercao_dividendos.lastrowid
    return id_dividendos

def inserir_pontuacao(cursor_dados, dados_financeiros_id, data_calculo, market_cap_usado, score_net_net, score_pvc, score_pe, score_dividend_yield, pontuacao_final,precoacao):
    insercao_pontuacao=cursor_dados.execute("INSERT INTO pontuacoes( dados_financeiros_id, data_calculo, market_cap_usado, score_net_net, score_pvc, score_pe, score_dividend_yield, pontuacao_final,preco_por_acao) VALUES (?,?,?,?,?,?,?,?,?)",(dados_financeiros_id, data_calculo, market_cap_usado, score_net_net, score_pvc, score_pe, score_dividend_yield, pontuacao_final,precoacao))
    conexao_dados_financeiros.commit()
    id_pontuacao=insercao_pontuacao.lastrowid
    return id_pontuacao

def buscar_empresa_id(cursor_dados,symbol):
    busca_cursor_empresa=cursor_dados.execute("SELECT id FROM empresas WHERE symbol=? LIMIT 1",(symbol,))
    id_empresa_tuplo=busca_cursor_empresa.fetchone()
    if id_empresa_tuplo is None:
        return None
    else:
        return id_empresa_tuplo[0]

def buscar_empresas_rentaveis(cursor_dados):
    busca=cursor_dados.execute("Select empresas.symbol,dados_financeiros.netIncome FROM dados_financeiros JOIN empresas ON dados_financeiros.empresa_id==empresas.id WHERE dados_financeiros.netIncome>0")
    resultado_empresas_rentaveis=busca.fetchall()
    return resultado_empresas_rentaveis

def busca_dados_BD(cursor_dados):
    join_symbol_dados=cursor_dados.execute("SELECT empresas.symbol,empresas.sector,dados_financeiros.* FROM empresas JOIN dados_financeiros ON dados_financeiros.empresa_id==empresas.id")
    resultados=join_symbol_dados.fetchall()
    return resultados

if __name__=="__main__":
    tabelas=criar_tabelas()
    empresa=inserir_empresa(cursor_dados,"NFLX","Streamlandia Corp","Entretenimento")
    dados=inserir_dados_financeiros(cursor_dados, empresa, 2025, 50_000_000, 12_000_000, 38_000_000, 9_500_000, 4.32, 120_000_000)
    dividendo=inserir_dividendo(cursor_dados, empresa, "2025-06-15", 0.15, 0.62, "Quarterly")
    pontuacao=inserir_pontuacao(cursor_dados, dados, "2026-08-31", 250_000_000, 0.81, 0.55, 12.3, 0.62, 0.74)
    info=buscar_dados_financeiros_recentes(cursor_dados,empresa)
    print(info)