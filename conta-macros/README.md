# Conta-Macros

Aplicação que auxilia a prática de exercício físico, contando as macros das
refeições/alimentos que o utilizador vai ingerindo ao longo do dia.

## Funcionalidades

- Tirar foto de um prato e calcular as macros de vários alimentos distintos automaticamente
- Tirar foto de um rótulo nutricional e adaptar os valores à quantidade realmente ingerida
- Confirmar/ajustar as unidades e quantidades dos alimentos reconhecidos, para maior precisão
- Guardar o histórico de refeições do dia
- Ver o total de macros consumidos no dia

## Stack Técnica

- **Python**— linguagem de programação
- **Streamlit** — interface (UI)
- **Anthropic API** — reconhecimento de imagem (pratos e rótulos)
- **pandas** — leitura e consulta da base de dados de alimentos
- **rapidfuzz** — correspondência aproximada entre os alimentos reconhecidos e os da base de dados
- **SQLite** — histórico de refeições

## Como correr localmente

(Suporte fora da máquina local está planeado para a v2.)

```bash
pip install -r requirements.txt
```

Cria um ficheiro `.env` com a tua chave da API:

```
ANTHROPIC_API_KEY=a_tua_chave_aqui
```

Corre a aplicação:

```bash
streamlit run app.py
```

## Estrutura do Projeto

- **`data/`** — base de dados de alimentos (`alimentos_pt.csv`), com 57 alimentos
  e os respetivos valores de kcal, proteína, hidratos e gordura.
- **`src/prompts.py`** — prompts enviados à API da Anthropic junto com a foto:
  um para análise de pratos/alimentos, outro para leitura de rótulos.
- **`src/vision.py`** — reconhecimento de imagem. `analisar_imagem()` converte
  a foto em bytes, envia à API e devolve os alimentos identificados já
  organizados; `ler_rotulo()` faz o mesmo para rótulos nutricionais.
- **`src/nutrition.py`** — depois do resultado do `vision.py`,
  `encontrar_alimento()` correlaciona os alimentos identificados com os da
  base de dados (usando rapidfuzz como indicador de confiança do match),
  `obter_peso_unitario()` obtém o peso de referência por unidade, e
  `calcular_macros()` calcula as macros totais de cada refeição.
- **`src/storage.py`** — histórico de refeições em SQLite.
  `guardar_refeicao()` grava uma refeição; `obter_historico_hoje()` devolve
  o histórico do dia.
- **`app.py`** — liga tudo e apresenta os resultados através do Streamlit.

## Limitações

- Base de dados com apenas 57 alimentos (a expandir na v2)
- A IA não é 100% precisa — por vezes há erros na leitura de rótulos, e podem
  surgir divergências entre leituras que deveriam dar o mesmo resultado
- UI funcional mas simples — melhoria de aparência prevista para a v2
