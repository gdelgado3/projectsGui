import base64
import json
import mimetypes
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from src.prompts import VISION_PROMPT,ROTULO_PROMPT

load_dotenv()

MODEL="claude-sonnet-5"
client=Anthropic()

def analisar_imagem(caminho_imagem):
    # Recebe o caminho da imagem, lê os bytes da imagem e guarda em bytes_imagem.
    with open(caminho_imagem,"rb")as f:
        bytes_imagem=f.read()
    # Media type vai com o mimetypes adivinhar o tipo da foto (jpeg, png...) e
    # caso falhe dá fallback para image/jpeg.
    media_type=mimetypes.guess_type(caminho_imagem)[0] or "image/jpeg"
    # imagem_base64 vai transformar os bytes da imagem inicialmente em base64
    # para depois conseguir dar decode para texto através do utf8.
    imagem_base64=base64.standard_b64encode(bytes_imagem).decode("utf-8")
    # resposta vai especificar o que é passado para a API, como o máximo de
    # tokens, o tipo da imagem, o media type e os dados propriamente ditos, e
    # passamos o prompt para ele responder.
    resposta=client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[
            {"role":"user",
             "content":[
                 {
                     "type":"image",
                     "source":{
                         "type":"base64",
                         "media_type":media_type,
                         "data":imagem_base64,
                     },
                 },
            {"type": "text","text":VISION_PROMPT}, ],}
        ],
    )

    # Percorremos os blocos da resposta à procura de um do tipo "text" — só aí
    # é que damos strip do conteúdo e guardamos em texto. Se o ciclo acabar
    # sem encontrar nenhum, texto continua None e informamos que não
    # encontramos nenhum bloco.
    texto = None
    for bloco in resposta.content:
        print([b.type for b in resposta.content])
        if bloco.type == "text":
            texto = bloco.text.strip()
            break

    if texto is None:
        print("Nenhum bloco de texto encontrado na resposta da API.")
        return None

    # Se o texto vier com crases, tiramos as crases e tiramos o prefixo json
    # que está associado a essas crases.
    if texto.startswith("```"):
        texto=texto.strip("`").removeprefix("json").strip()

    # Tratamento de erros: tentamos carregar o texto em json — se der, então
    # tivemos sucesso e retornamos; caso contrário, mostramos o texto e
    # retornamos None.
    try:
        textocarregado=json.loads(texto)
        return textocarregado
    except:
        print(texto)
        return None

# Se formos pela main way (a way normal): o sys.argv[1] vai reconhecer o
# caminho, chamamos a função com o caminho obtido e damos print se houver
# resultado, se não retornamos erro.
if __name__=="__main__":
    caminho=sys.argv[1]
    resultado=analisar_imagem(caminho)
    if resultado is None:
        print ("Erro none retornado")
    else:
        print (resultado)


# A ler_rotulo é muito semelhante: temos uma leitura de bytes, extraímos o
# tipo de imagem com fallback, passamos para base64 texto e mandamos a
# prompt rótulo para o Claude. O resto é muito semelhante ao de cima — só
# para dizer que fica no tratamento de erros porque não há uma "secondary
# way" (foi feita para testar manualmente no início).
def ler_rotulo(caminho_imagem):
    with open(caminho_imagem,"rb") as f2:
        bytes_rotulo=f2.read()
    tipofoto=mimetypes.guess_type(caminho_imagem)[0] or ("image/jpeg")
    rotulobase64=base64.standard_b64encode(bytes_rotulo).decode("utf-8")
    respostarotulo=client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {"role":"user",
                 "content":[
                     {
                         "type":"image",
                         "source":{
                             "type":"base64",
                             "media_type":tipofoto,
                             "data":rotulobase64,
                         },
                     },
                {"type": "text","text":ROTULO_PROMPT}, ],}
            ],
        )

    texto1=None
    for blocorespostarotulo in respostarotulo.content:
        print([b.type for b in respostarotulo.content])
        if blocorespostarotulo.type=="text":
            texto1=blocorespostarotulo.text.strip()
            break

    if texto1 is None:
        print("Nenhum bloco de texto encontrado na resposta da API.")
        return None

    if texto1.startswith ("```"):
        texto1=texto1.strip("`").removeprefix("json").strip()

    try:
        textorotulo=json.loads(texto1)
        return textorotulo
    except:
        print(texto1)
        return None
        



