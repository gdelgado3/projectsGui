import pandas as pd
from src.db import cursor_dados,buscar_empresa_id,inserir_empresa,inserir_dados_financeiros,busca_dados_BD,inserir_pontuacao
import os
from dotenv import load_dotenv
import requests
import time
from datetime import datetime

CANDIDATOS = {
"revenue": ["us-gaap_Revenues", "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"],
"netIncome": ["us-gaap_NetIncomeLoss", "us-gaap_ProfitLoss"],
"eps": ["us-gaap_EarningsPerShareBasic", "us-gaap_EarningsPerShareBasicAndDiluted"],
"totalCurrentAssets": ["us-gaap_AssetsCurrent"],
"totalLiabilities": ["us-gaap_Liabilities"],
"totalStockholdersEquity": ["us-gaap_StockholdersEquity", "us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
"dividendos": ["us-gaap_PaymentsOfDividends", "us-gaap_PaymentsOfDividendsCommonStock"],
}

load_dotenv()
keyfinn=os.getenv("FINNHUB_API_KEY")
keyTelegram=os.getenv("TELEGRAM")
chat_id=os.getenv("TELEGRAM_CHAT_ID")



def carregar_empresas_alvo(caminho="data/empresas_alvo.csv"):
    df=pd.read_csv(caminho)
    return df

def obter_ou_criar_empresa(cursor_dados,symbol,nome,sector):
    busca=buscar_empresa_id(cursor_dados,symbol)
    if busca is None:
        busca=inserir_empresa(cursor_dados,symbol,nome,sector)
    return busca

def buscar_valor(lista_items,candidatos):
    for candidato in candidatos:
        for linha in lista_items:
            if linha["concept"]==candidato:
                return linha["value"]
    return None

def ingerir_dados_financeiros(cursor_dados,empresa_id,symbol,key):
    delay=1
    FARurl=f"https://finnhub.io/api/v1/stock/financials-reported?symbol={symbol}&token={key}"
    while delay<30:
        dados=requests.get(FARurl)
        dados_json=dados.json()
        if dados.status_code==200:
            break
        elif dados.status_code==429:
            time.sleep(delay)
            delay*=2
            continue
        raise Exception ("Erro")

    if delay>=30:
        raise Exception("Erro")
    balance=dados_json["data"][0]["report"]['bs']
    income=dados_json["data"][0]["report"]["ic"]
    ano=dados_json["data"][0]["year"]
    revenue = buscar_valor(income, CANDIDATOS["revenue"])
    netIncome = buscar_valor(income, CANDIDATOS["netIncome"])
    eps = buscar_valor(income, CANDIDATOS["eps"])
    totalCurrentAssets = buscar_valor(balance, CANDIDATOS["totalCurrentAssets"])
    totalLiabilities=buscar_valor(balance, CANDIDATOS["totalLiabilities"])
    totalStockholdersEquity=buscar_valor(balance, CANDIDATOS["totalStockholdersEquity"])
    insercaodadosfinanceiros=inserir_dados_financeiros(cursor_dados,empresa_id,ano,totalCurrentAssets,totalLiabilities,totalStockholdersEquity,netIncome,eps,revenue)
    return insercaodadosfinanceiros

def ingerir_todas_as_empresas():
    dfempresas=carregar_empresas_alvo(caminho="data/empresas_alvo.csv")
    lista_sucesso=[]
    lista_insucesso=[]
    for index,linha in dfempresas.iterrows():
        empresa=obter_ou_criar_empresa(cursor_dados,linha["symbol"],linha["nome"],linha["sector"])
        try:
            ingerir_dados_financeiros(cursor_dados,empresa,linha["symbol"],keyfinn)
            lista_sucesso.append(linha["symbol"])
        except Exception as erro:
            lista_insucesso.append((linha["symbol"],str(erro)))
            continue
    return lista_sucesso,lista_insucesso

def buscar_dados_pontuacao(symbol,keyfinn):
    FARurl=f"https://finnhub.io/api/v1/stock/financials-reported?symbol={symbol}&token={keyfinn}"
    delay=1
    while delay<30:
            FAR=requests.get(FARurl)
            FAR_json=FAR.json()
            if FAR.status_code==200:
                break
            elif FAR.status_code==429:
                time.sleep(delay)
                delay*=2
                continue
            raise Exception("ERRO")
    if delay>=30:
        raise Exception("ERRO")
    delay=1
    cf=FAR_json["data"][0]["report"]["cf"]
    p2url=f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={keyfinn}"
    while delay<30:
        p2data=requests.get(p2url)
        p2data_json=p2data.json()
        if p2data.status_code==200:
            break
        elif p2data.status_code==429:
            time.sleep(delay)
            delay*=2
            continue
        raise Exception ("Erro")
    if delay>=30:
        raise Exception("Erro")
        
    marketCapitalization=p2data_json["marketCapitalization"]*1000000
    numeroshares=p2data_json["shareOutstanding"]
    resultadosdividendos=buscar_valor(cf,CANDIDATOS["dividendos"])
    return (marketCapitalization,resultadosdividendos,numeroshares)

def montar_dados_pontuacao(cursor_dados):
    dadosBD=busca_dados_BD(cursor_dados)
    listadados=[]
    for empresa in dadosBD:
        try:
            pontuacaoempresa=buscar_dados_pontuacao(empresa[0],keyfinn)
            tuplodadosfinanc=(empresa[0],empresa[1],empresa[2],empresa[3],empresa[4],empresa[5],empresa[6],empresa[7],empresa[8],empresa[9],empresa[10])
            tuplopont=pontuacaoempresa
            tuplodadosfinanc=tuplodadosfinanc+tuplopont
            listadados.append(tuplodadosfinanc)
        except:
            continue
    return listadados

def calculo_formulas(dadosempresa):
    flagnetnetinv=False
    flagpvcpenaliza=False
    flagdividendosa0=False
    flagpvcneutraliza=False
    flagincomenegativo=False
    flagpvcnegativo=False
    if dadosempresa[5]!=None and dadosempresa[6]!=None:
        nao_tem_assets=0
        ncav=dadosempresa[5]-dadosempresa[6]
        if 2/3*ncav>dadosempresa[11]:
            scorenetnet=1
        else:
            scorenetnet=0
    else:
        nao_tem_assets=1
        scorenetnet=-1
    pvc=dadosempresa[11]/dadosempresa[7]
    pe=dadosempresa[11]/dadosempresa[8]
    if dadosempresa[12] is None:
        dividend=0
        dividendyield=dividend/dadosempresa[11]
    else:
        dividendyield=dadosempresa[12]/dadosempresa[11]
    if nao_tem_assets==1:
        flagnetnetinv=True
    if dadosempresa[8]<0:
        flagincomenegativo=True
    if pvc<0:
        flagpvcnegativo=True
    if flagpvcnegativo==True and flagincomenegativo==True:
        flagpvcpenaliza=True
    elif (flagpvcnegativo==True and flagincomenegativo==False):
        flagpvcneutraliza=True
    if dadosempresa[12]==None:
        flagdividendosa0=True
    return (dadosempresa[0],dadosempresa[1],scorenetnet,pvc,pe,dividendyield,nao_tem_assets,dadosempresa[2],dadosempresa[11],dadosempresa[8],flagnetnetinv,flagpvcneutraliza,flagpvcpenaliza,flagdividendosa0,flagincomenegativo,dadosempresa[13])
    
def loop_calculo_formulas(listadados):
    dicsetores={}
    for empresa in listadados:
        try:
            indices_empresa=calculo_formulas(empresa)
            if empresa[1]in dicsetores:
                    dicsetores[empresa[1]].append(indices_empresa)
            else:
                    dicsetores[empresa[1]]=[]
                    dicsetores[empresa[1]].append(indices_empresa)
        except:
            continue
        
    return dicsetores

def calcula_media_setores(dicsetores):
    listamediassetores=[]
    for setor in dicsetores:
        countempresas=0
        somapvc=0
        somape=0
        somadividendyield=0
        for empresa in dicsetores[setor]:
            countempresas+=1
            if not empresa[11] and not empresa[12]:
                somapvc+=empresa[3]
            if not empresa[14]:
                somape+=empresa[4]
            somadividendyield+=empresa[5]
            
        mediapvc=somapvc/countempresas
        mediape=somape/countempresas
        mediadividendyield=somadividendyield/countempresas
        listamediassetores.append((setor,mediapvc,mediape,mediadividendyield))
    return listamediassetores


def normaliza_e_calcula_pontuacoes(listamediassetores,dicsetores,cursor_dados):
    listapontuacaoempresa=[]
    for setor in dicsetores:
        for mediassetores in listamediassetores:
            if mediassetores[0]==setor:
                for empresa in dicsetores[setor]:
                    if mediassetores[1]!=0:
                        normalizacaopvc=max(0,(mediassetores[1]-empresa[3])/mediassetores[1])
                    else:
                        normalizacaopvc=0
                    if mediassetores[2]!=0 and empresa[4]>0:
                        normalizacaope=max(0,(mediassetores[2]-empresa[4])/mediassetores[2])
                    else:
                        normalizacaope=0
                    if mediassetores[3]!=0:
                        normalizacaodividendyield=min(1,empresa[5]/mediassetores[3])
                    else:
                        normalizacaodividendyield=0
                    componentes=[{"peso_base":0.19,"score":empresa[2],"invalido":empresa[6]==1,"fracao_perdida":0.0},
                    {"peso_base":0.27,"score":normalizacaopvc,"invalido":empresa[11] or empresa[12],"fracao_perdida":1.0 if empresa[12] else 0.0},
                    {"peso_base":0.27,"score":normalizacaope,"invalido":empresa[14],"fracao_perdida":1.0},
                    {"peso_base":0.27,"score":normalizacaodividendyield,"invalido":empresa[13],"fracao_perdida":0.5}]
                    peso_a_redestribuir=sum(c["peso_base"]*(1-c["fracao_perdida"]) for c in componentes if c["invalido"])
                    peso_valido=sum(c["peso_base"] for c in componentes if not c["invalido"])

                    pontuacao=0
                    for c in componentes:
                        if c["invalido"]:
                            c["score"]=None
                            continue  #já usado para peso_a_redestribuir
                        peso_efetivo=c["peso_base"]+(c["peso_base"]/peso_valido)*peso_a_redestribuir
                        pontuacao+=peso_efetivo*c["score"]
                    data_calcul=datetime.now()
                    preco_por_acao=empresa[8]/(empresa[15]*1000000)
                    listapontuacaoempresa.append((cursor_dados,empresa[7],data_calcul,empresa[8],empresa[2],componentes[1]["score"],componentes[2]["score"],componentes[3]["score"],pontuacao,preco_por_acao))
    return listapontuacaoempresa

def main_loop_pontuacoes(cursor_dados):
    listaidinseridas=[]
    dados_pontuacao=montar_dados_pontuacao(cursor_dados)
    calculoindices=loop_calculo_formulas(dados_pontuacao)
    mediasetores=calcula_media_setores(calculoindices)
    listapontuacoes=normaliza_e_calcula_pontuacoes(mediasetores,calculoindices,cursor_dados)
    for pontuacoes in listapontuacoes:
        try:
            insertpontuacao=inserir_pontuacao(pontuacoes[0],pontuacoes[1],pontuacoes[2],pontuacoes[3],pontuacoes[4],pontuacoes[5],pontuacoes[6],pontuacoes[7],pontuacoes[8],pontuacoes[9])
            listaidinseridas.append(insertpontuacao)
        except:
            continue
    return listaidinseridas

def junta_dados_importantes_cliente(cursor_dados):
    acima_limiar=cursor_dados.execute("SELECT pontuacoes.preco_por_acao,pontuacoes.data_calculo,pontuacoes.score_net_net,pontuacoes.score_pvc,pontuacoes.score_pe,pontuacoes.score_dividend_yield,pontuacoes.pontuacao_final,pontuacoes.dados_financeiros_id,dados_financeiros.empresa_id,empresas.symbol,empresas.nome FROM pontuacoes JOIN dados_financeiros ON dados_financeiros.id==pontuacoes.dados_financeiros_id JOIN empresas ON dados_financeiros.empresa_id==empresas.id WHERE pontuacoes.pontuacao_final>=0.7 AND pontuacoes.id IN(SELECT MAX(pontuacoes.id) FROM pontuacoes JOIN dados_financeiros ON pontuacoes.dados_financeiros_id=dados_financeiros.id GROUP BY empresa_id)")
    dados_acima_limiar=acima_limiar.fetchall()
    return dados_acima_limiar

def envia_mensagem_empresas_subvalorizadas(cursor_dados):
    listarespostabot=[]
    empresas_subvalorizadas=junta_dados_importantes_cliente(cursor_dados)
    for empresa in empresas_subvalorizadas:
        nome=empresa[10]
        simbolo=empresa[9]
        precoacao=empresa[0]
        scorenetnet=empresa[2]
        scorepvc=empresa[3]
        scorepe=empresa[4]
        scoredividend=empresa[5]
        pontuacao=empresa[6]
        if precoacao!=None:
            precoacao=round(empresa[0],2)
        else:
            precoacao="N/A"
        if scorenetnet!=None and scorenetnet!=-1:
            scorenetnet=round(empresa[2],2)
        else:
            scorenetnet="N/A"
        if scorepvc!=None:
            scorepvc=round(empresa[3],2)
        else:
            scorepvc="N/A"
        if scorepe!=None:
            scorepe=round(empresa[4],2)
        else:
            scorepe="N/A"
        if scoredividend!=None:
            scoredividend=round(empresa[5],2)
        else:
            scoredividend="N/A"
        if pontuacao!=None:
            pontuacao=round(empresa[6],2)
        else:
            pontuacao="N/A"
        url= f"https://api.telegram.org/bot{keyTelegram}/sendMessage"
        try:
            respostabot=requests.post(url,data={"chat_id":chat_id,"text":f"A ação de: {nome} \n com o simbolo: {simbolo} \n com score net net: {scorenetnet}, \n scorepvc: {scorepvc}, \n scorepe: {scorepe} \n e score dividend yield: {scoredividend} \n acabou de atingir a pontuação de: {pontuacao} \n com o valor por ação: {precoacao}"})
            listarespostabot.append(respostabot.json())
        except:
            continue
    return listarespostabot


def correr_bot_completo(cursor_dados):
    ingerir_todas_as_empresas()
    main_loop_pontuacoes(cursor_dados)
    enviamensagens=envia_mensagem_empresas_subvalorizadas(cursor_dados)
    return enviamensagens




