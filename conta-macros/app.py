import streamlit as st
from src.vision import analisar_imagem,ler_rotulo
from src.nutrition import calcular_macros,obter_peso_unitario
from src.storage import guardar_refeicao,obter_historico_hoje
import pandas as pd



# App.py acaba por ser a zona onde usamos todas as black boxes e usamos o
# streamlit como UI para os resultados e para a formatação do site.
database=pd.read_csv("data/alimentos_pt.csv")
st.title("Aplicação Conta-Macros")
ficheiro=st.file_uploader("upload refeições",type=["jpg", "jpeg", "png"])
# Caso receba algum ficheiro para analisar de prato, ou seja, se alguém tocar
# no botão, vamos ler os seus bytes da imagem, vamos escrever num caminho
# criado por nós os bytes que lemos da imagem, analisamos a imagem que
# acabamos de manipular e esse resultado fica guardado no st.session_state.
if ficheiro is not None:
    if st.button("ANALISAR")==True:
        leiturabytes=ficheiro.getvalue()
        with open("data/upload_temp.jpg","wb") as abrebytes:
            escritabytes=abrebytes.write(leiturabytes)
            imagemanalisada=analisar_imagem("data/upload_temp.jpg")
            st.session_state["resultado"]=imagemanalisada

# Fazemos algo muito semelhante com o rótulo, só guardamos a extensão dos
# rótulos para permitir maior flexibilidade à frente, mas de resto é igual.
ficheirorotulo=st.file_uploader("rotulo upload",type=["jpg", "jpeg", "png","webp"])
if ficheirorotulo is not None:
    extensao=ficheirorotulo.name.split(".")[-1]
    if st.button("Ler rotulo")==True:
        leiturabytes=ficheirorotulo.getvalue()
        with open(f"data/rotulo_temp.{extensao}","wb") as abrebytes:
            escritabytes=abrebytes.write(leiturabytes)
            imagemanalisada=ler_rotulo(f"data/rotulo_temp.{extensao}")
            st.session_state["rotulo_lido"]=imagemanalisada
# Criamos uma lista; se houver leitura de rótulo, fazemos um input para
# ajustar a quantidade consumida, para conseguirmos multiplicar por um fator
# de ajuste.
lista=[]
if "rotulo_lido" in st.session_state:
    st.write(st.session_state["rotulo_lido"])
    quantidadetotal=st.number_input(f"Quantidade consumida em {st.session_state["rotulo_lido"]["base_unidade"]} ",value=st.session_state["rotulo_lido"]["base_quantidade"])
    fatordeajuste=quantidadetotal/st.session_state["rotulo_lido"]["base_quantidade"]
    # Se se clicar para adicionar aos totais vindo de um rótulo, o que
    # fazemos é criar uma lista de extras onde metemos toda a informação
    # vinda da leitura do rótulo, criando uma lista de dicionários onde
    # cada dicionário tem os seus macros.
    if st.button("Adicionar aos totais") is True:
        listaextras=st.session_state.setdefault("extras", [])
        macrosrotulo=st.session_state["rotulo_lido"].copy()
        macrosrotulo["kcal"]=macrosrotulo["kcal"]*fatordeajuste
        macrosrotulo["proteina_g"]=macrosrotulo["proteina_g"]*fatordeajuste
        macrosrotulo["hidratos_g"]=macrosrotulo["hidratos_g"]*fatordeajuste
        macrosrotulo["gordura_g"]=macrosrotulo["gordura_g"]*fatordeajuste 
        listaextras.append(macrosrotulo)       
# Se houver algum resultado na session_state ou se extras não tiver vazio,
# vemos: se for o resultado, ou seja, se houver leitura de pratos antes,
# burocratizamos a label, o valor mínimo e máximo de unidades, os sliders e
# o peso unitário — que se não for None pode ser em gramas ou unidades,
# dependendo do utilizador.
if "resultado" in st.session_state or  st.session_state.get("extras"):
        if "resultado" in st.session_state:
            result=st.session_state["resultado"]
            for  indice,alimento in  enumerate(result["alimentos"]):
                label=alimento["nome"]
                min_value=0
                max_value=500
                value=alimento["porcao_g"]
                keyslider=str(indice)+"_slider"
                keyradio=str(indice)+ "_radio"
                keyunidades=str(indice) +"_unidades"
                peso_unitario=obter_peso_unitario(label,database)
                # Se for unidades, o slider estará em unidades, caso contrário
                # em gramas. Se o peso unitário for None nem sequer damos a
                # choice de haver escolha de unidades — é constante e certo
                # que será gramas.
                if peso_unitario is not None:
                    escolhaporcoes=st.radio(label,["gramas","unidades"],key=keyradio)
                    if escolhaporcoes=="unidades":
                        infoquantidade=st.slider("Quantidade",1,10,1,key=keyunidades)
                        infoalimento=infoquantidade*peso_unitario
                    else:
                        infoalimento=st.slider(label,min_value,max_value,value,key=keyslider,format="%dg")
                else:
                    infoalimento=st.slider(label,min_value,max_value,value,key=keyslider,format="%dg")
                # Damos append da informação obtida (nome e quantidade dos
                # alimentos, numa lista de dicts) para a variável lista, que
                # vai ser usada para chamar calcular_macros.
                lista.append({"nome":label,"porcao_g":infoalimento})
        macros=calcular_macros(lista)
        for valores in st.session_state.get("extras",[]):
            macros["kcal"]+=valores["kcal"]
            macros["proteina_g"]+=valores["proteina_g"]
            macros["hidratos_g"]+=valores["hidratos_g"]
            macros["gordura_g"]+=valores["gordura_g"]
        # Para cada alimento vamos somar as macros, escrevendo a soma dos
        # alimentos e a sua unidade de medida (kcal, g).
        output={"kcal":macros["kcal"],"proteina":macros["proteina_g"],"hidratos":macros["hidratos_g"],"gordura":macros["gordura_g"]}
        listamacros=["kcal","proteina","hidratos","gordura"]
        unidades={"kcal": "kcal", "proteina": "g", "hidratos": "g", "gordura": "g"}
        for macro in listamacros:
            texto= f"{round(output[macro],1)} {unidades[macro]}"
            st.metric(macro,texto)
        # Caso cliquemos no guardar refeição, chamamos a guardar_refeicao
        # para meter no sqlite3.
        if st.button("Guardar refeição") is True:
             guardar_refeicao(lista,macros)
             st.success("Refeição guardada com sucesso")






# O histórico é obtido também no sqlite3; para cada refeição guardada damos
# um índice com enumerate e escrevemos as macros que vão estar em histórico,
# fazemos a soma das macros no histórico e apresentamos a soma diária das
# refeições no histórico também, além da de cada refeição.
with st.expander("Historico de hoje"):
     historico=obter_historico_hoje()
     somaprot=0
     somakcal=0
     somagordura=0
     somahidratos=0
     for indice,refeicao in enumerate(historico):
          st.write(f"Refeição {indice+ 1}")
          st.write(f"{round(refeicao[3],1)}kcal")
          somakcal+=refeicao[3]
          st.write(f"{round(refeicao[4],1)} g proteina")
          somaprot+=refeicao[4]
          st.write(f"{round(refeicao[5],1)} g hidratos")
          somahidratos+=refeicao[5]
          st.write(f"{round(refeicao[6],1)} g gordura")
          somagordura+=refeicao[6]
          st.divider()
     listasummacros={"somakcal":somakcal,"somaprot":somaprot,"somahidratos":somahidratos,"somagordura":somagordura}
     listanomemacros=["somakcal","somaprot","somahidratos","somagordura"]
     unidade={"somakcal": "kcal", "somaprot": "g", "somahidratos": "g", "somagordura": "g"}
     for somamacroind in listanomemacros:
        texto=f"{round(listasummacros[somamacroind],1)} {unidade[somamacroind]}"
        st.metric(somamacroind,texto)
          
          
             
            
    
