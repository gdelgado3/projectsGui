# bot-financeiro 📈

Bot financeiro que analisa cerca de 100 empresas e tenta perceber, com métodos clássicos de *value investing*, se estão subvalorizadas — enviando um alerta no Telegram quando encontra uma. Não compra nem vende nada: é só um sinal para o utilizador decidir.

## Objetivo e método

O projeto parte de 4 métodos usados por investidores de valor como Warren Buffett e Benjamin Graham, aplicados aos dados da *balance sheet*, do *cash flow* e da *income statement* de cada empresa:

- **Net-Net de Graham** — compara ativos correntes e passivo total com a capitalização de mercado.
- **P/VC** (preço/valor contabilístico) — compara o preço de mercado com o capital próprio da empresa.
- **P/E** (preço/lucro) — compara o preço de mercado com o lucro da empresa.
- **Dividend Yield** — retorno em dividendos face ao preço da ação.

Para cada empresa, cada rácio é normalizado através da média do respetivo setor (as empresas da mesma tabela `empresas`), e combinado numa **pontuação final ponderada**. Empresas sem dados suficientes para algum rácio têm o peso desse rácio redistribuído pelos restantes, penalizando ligeiramente a pontuação (menos informação = mais risco). Sempre que a pontuação final é **≥ 0.7**, a empresa é considerada subvalorizada e entra no alerta.

## Arquitetura

O pipeline corre em 3 fases sequenciais:

1. **Ingestão** — os dados de mercado (balance sheet, income, cash flow) são recolhidos da API da [Finnhub](https://finnhub.io/).
2. **Cálculo de pontuações** — em Python, a partir dos dados filtrados da ingestão, calculam-se os 4 rácios, as médias por setor e a pontuação final de cada empresa.
3. **Notificação** — um bot do Telegram envia ao utilizador a lista de empresas com pontuação ≥ 0.7.

```
Finnhub API → ingestão (src/ingestao.py) → SQLite (src/db.py) → cálculo de pontuações → Telegram
```

## Stack técnica

- **Python**
- **SQLite3** — persistência dos dados de empresas, dados financeiros e pontuações
- **pandas** — leitura da lista de empresas-alvo
- **requests** — chamadas às APIs (Finnhub e Telegram)
- **Telegram Bot API** — envio dos alertas

## Setup

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd bot-financeiro

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Configurar as variáveis de ambiente
cp .env.example .env
# preencher FINNHUB_API_KEY, TELEGRAM e TELEGRAM_CHAT_ID no .env

# 4. Criar as tabelas da base de dados
python -c "from src.db import criar_tabelas; criar_tabelas()"
```

## Como correr

**Manualmente**, a qualquer momento:

```bash
python main.py
```

**Automaticamente**, uma vez por dia: o `main.py` está preparado para ser chamado por um agendador do sistema (ex.: `cron`). Nota: se estiveres a correr em WSL, o `cron` só dispara enquanto o WSL estiver ativo — para garantir a execução diária mesmo com o PC em suspensão, o mais fiável é agendar através do **Task Scheduler do Windows**, que invoca o `wsl.exe` a correr o `main.py`.

## Estrutura do projeto

```
bot-financeiro/
├── main.py                  # ponto de entrada — cria tabelas e corre o bot completo
├── requirements.txt
├── .env.example
├── data/
│   ├── empresas_alvo.csv    # ~100 empresas-alvo, por setor
│   └── bot_financeiro.db    # base de dados SQLite (gerada)
└── src/
    ├── db.py                # camada de acesso à BD (tabelas, inserts, queries)
    ├── ingestao.py           # ingestão, cálculo de rácios/pontuações, envio do alerta
    └── fmp_client.py         # exploração inicial da API FMP (abandonada, mantida por histórico)
```

### `src/db.py`

Cria e gere as 4 tabelas da base de dados: `empresas`, `dados_financeiros`, `dividendos` e `pontuacoes`. Expõe funções de inserção (`inserir_empresa`, `inserir_dados_financeiros`, `inserir_dividendo`, `inserir_pontuacao`) e de consulta (`buscar_empresa_id`, `buscar_dados_financeiros_recentes`, `buscar_empresas_rentaveis`, `busca_dados_BD`). `inserir_dados_financeiros` é idempotente: se já existirem dados financeiros recentes para a empresa, reaproveita-os em vez de duplicar a linha — importante para permitir correr o bot várias vezes sem multiplicar os dados nem os alertas.

### `src/ingestao.py`

O ficheiro mais longo e central do projeto. Principais responsabilidades:

- `carregar_empresas_alvo` — lê a lista de empresas-alvo (`data/empresas_alvo.csv`) para um DataFrame.
- `obter_ou_criar_empresa` — devolve o id da empresa na BD, criando-a se ainda não existir.
- `buscar_valor` — a Finnhub devolve os dados *as reported*, ou seja, cada empresa pode usar um nome de campo diferente para o mesmo conceito (ex. "Total Assets" vs "TotalAssetsNet"). Esta função usa listas de nomes candidatos por campo para uniformizar a extração.
- `ingerir_dados_financeiros` / `ingerir_todas_as_empresas` — vão buscar os *financials as reported* à Finnhub (com *backoff* em caso de limite de pedidos) e inserem-nos na BD.
- `buscar_dados_pontuacao` — vai buscar capitalização de mercado, número de ações e dividendos.
- `montar_dados_pontuacao` — junta os dados da BD com os de `buscar_dados_pontuacao` num único tuplo por empresa.
- `calculo_formulas` — calcula os 4 rácios de cada empresa e sinaliza (via *flags*) os que não puderam ser calculados por falta de dados.
- `loop_calculo_formulas` / `calcula_media_setores` — agrupam as empresas por setor e calculam a média de cada rácio, excluindo os valores inválidos.
- `normaliza_e_calcula_pontuacoes` — normaliza cada rácio face à média do setor, pondera-os (com redistribuição de peso quando faltam dados) e calcula a pontuação final.
- `main_loop_pontuacoes` — corre a cadeia de cálculo e regista as pontuações na BD.
- `junta_dados_importantes_cliente` / `envia_mensagem_empresas_subvalorizadas` — selecionam as empresas com a pontuação mais recente ≥ 0.7 e enviam o alerta via Telegram.
- `correr_bot_completo` — encadeia ingestão → pontuação → alerta.

### `main.py`

Ponto de entrada do bot: cria as tabelas (caso não existam), corre `correr_bot_completo` e imprime o número de alertas enviados. Pensado para ser chamado uma vez por dia por um agendador do sistema.

## Limitações conhecidas

- Setores como seguros e imobiliário não têm um conceito claro de "ativos" comparável ao de outras indústrias, pelo que o Net-Net de Graham não é calculável para essas empresas.
- A uniformização dos *financials as reported* da Finnhub para um conjunto fixo de campos é aproximada — depende de listas de nomes candidatos, que podem não cobrir todas as variações usadas pelas empresas.
- Empresas estrangeiras que reportam à SEC através do formulário **20-F** (em vez do 10-K anual padrão dos EUA) não são cobertas pela ingestão atual, que assume o formato 10-K.
- As médias por setor usadas para normalizar os rácios são calculadas apenas com as empresas presentes na base de dados — um universo limitado — em vez de benchmarks de mercado mais amplos.

## Possíveis melhorias futuras

- Substituir as médias setoriais internas por *benchmarks* externos (ex. dados sectoriais de Damodaran), reduzindo o enviesamento de uma amostra pequena.
- Fazer *refactor* dos tuplos posicionais usados entre funções (ex. `empresa[8]`) para dicionários ou *dataclasses*, tornando o código mais legível e menos frágil a mudanças de ordem dos campos.
- Adicionar *scraping* ao estilo [Dataroma](https://www.dataroma.com/) para cruzar as empresas subvalorizadas com as carteiras de grandes investidores (via 13F), como sinal de confiança adicional.

## Aviso

Este bot **não executa nenhuma operação de compra ou venda** — serve apenas como auxiliar de análise, sinalizando possíveis empresas subvalorizadas. A responsabilidade e a decisão de investir são inteiramente do utilizador. Nada aqui constitui aconselhamento financeiro.
