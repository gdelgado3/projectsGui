from rapidfuzz import fuzz,process
import pandas as pd
from src.vision import analisar_imagem


def encontrar_alimento(nome,base):
    # Vamos ver se com o nome extraído conseguimos encontrar algo na nossa
    # tabela pandas.
    resultado=base[base["nome"]==nome];
    if resultado.empty==True:
        # Se for empty, então listamos todos os nomes dos alimentos e vamos
        # extrair aquele cujo rating rapidfuzz seja mais alto.
        lista=base["nome"].tolist()
        out=process.extractOne(nome,lista,scorer=fuzz.partial_ratio)
    else:
        # Caso não for empty, mandamos a linha desse elemento, com as macros deste.
        return resultado.iloc[0]

    # Se a percentagem do rapidfuzz for menor que 75, retornamos None; caso
    # contrário, vamos buscar a linha cujo nome é igual ao nome com maior
    # pontuação e retornamo-la.
    if out[1]<75:
        return None
    else:
        finals=base[base["nome"]==out[0]]
        return finals.iloc[0]

def obter_peso_unitario(nome,base):
    # Usamos a encontrar_alimento para nos retornar uma linha da tabela, e
    # caso encontremos um alimento cujo peso unitário não seja nulo,
    # retornamos esse peso unitário.
    linhaalimento=encontrar_alimento(nome,base)
    if linhaalimento is not None:
        if pd.isna(linhaalimento["peso_unitario_g"])==False:
            return linhaalimento["peso_unitario_g"]
        else:
            return None
    else:
        return None

def calcular_macros(alimentos_detectados):
    # Introduzimos com um dicionário começado por nós a zero, com as macros.
    totais = {"kcal": 0, "proteina_g": 0, "hidratos_g": 0, "gordura_g": 0}
    # Vamos ler da nossa base de dados de alimentos através do pandas,
    # transformando na mini tabela do pandas.
    base=pd.read_csv("data/alimentos_pt.csv")
    for alimento in alimentos_detectados:
        # Para cada alimento detetado vamos à procura da sua informação, com
        # a base de dados e o seu nome.
        line=encontrar_alimento(alimento["nome"],base)
        if line is None:
            # Se não houver alimento não acontece nada.
            continue
        else:
            # Vemos qual é a porção reconhecida a dividir pela constante da
            # BD que é 100g, e vamos adicionar aos totais (macros totais de
            # uma refeição) as macros de cada alimento, já fazendo a conta
            # com os seus fatores de mult.
            fatordemult=alimento["porcao_g"]/100 #na base de dados está tudo para 100 g
            totais["kcal"]+=line["kcal_100g"]*fatordemult
            totais["proteina_g"]+=line["proteina_g"]*fatordemult
            totais["hidratos_g"]+=line["hidratos_g"]*fatordemult
            totais["gordura_g"]+=line["gordura_g"]*fatordemult
    return totais

# Se formos pela main way, só chamamos a analisar_imagem com um caminho dado
# e, com a informação de analisar_imagem, podemos simplesmente ir calcular_macros.
if __name__ =="__main__":
    imagemanalisada=analisar_imagem("data/foto1.jpeg")
    if imagemanalisada is None:
        print("Erro parsing JSon")
    else:
        res=calcular_macros(imagemanalisada["alimentos"])
        print(res)

