# Contexto do projeto (para o Claude que for trabalhar aqui)

Este ficheiro existe porque o projeto foi planeado numa sessão do Claude Code
aberta noutra pasta (`food-tracker`), que não consegue operar diretamente
aqui. Lê isto antes de começar a codar.

## Quem é o Guilherme

1º ano de LEIC (Eng. Informática) no IST. Está a aprender a programar a
sério — quer **escrever o código ele próprio**, com o Claude a dar dicas,
explicações e apontar bugs (perguntas guiadas, não soluções prontas),
exceto para infraestrutura genuína (setup de projeto, bugs de biblioteca de
terceiros, etc. — isso o Claude pode simplesmente tratar). Nunca assumir que
"despachar" ou linguagem informal tipo "vamos rápido" é licença para saltar
este processo — é uma regra fixa dele, já testada e confirmada.

## Método de ensino (destilado do Food Tracker, para exponenciar a aprendizagem)

Guilherme fechou o Food Tracker com uma trajetória de crescimento clara e
mensurável (dependia de espreitar backups no início → escreveu 3 features
inteiras sozinho no fim → reteve e explicou o código todo depois de 10 dias
parado). O que funcionou, para replicar/intensificar aqui:

1. **Fundamentos antes da feature.** Sempre que aparece uma biblioteca nova
   (aqui: `requests`, forma de dados de uma API financeira), fazer primeiro
   exercícios isolados no terminal/REPL com ela, antes de a integrar na
   função real. Foi isto que resolveu o momento de maior frustração dele no
   Food Tracker (pandas/json/rapidfuzz do zero).
2. **Testar isolado antes de integrar.** Cada módulo novo deve ser testável
   sozinho (`if __name__=="__main__":`) antes de depender dele noutro sítio.
   Padrão usado em todo o Food Tracker, não abandonar aqui.
3. **Perguntas guia, nunca soluções — exceto infraestrutura genuína** (setup
   de projeto, bug de biblioteca/API de terceiros). Regra fixa, confirmada
   várias vezes: linguagem informal tipo "vamos despachar" NUNCA é licença
   para saltar isto.
4. **Pedir a ele a estrutura antes de a dar.** O salto de maturidade mais
   visível no Food Tracker começou quando lhe recusei dar os passos e ele
   propôs a sua própria estrutura. Fazer isto por defeito em tarefas novas,
   não só quando ele pedir.
5. **Deixar errar antes de apontar.** As aprendizagens mais profundas dele
   (mutabilidade de dicts/`.copy()`, semântica de `pd.isna`, reruns do
   Streamlit) vieram de ele bater no bug real e ser guiado a raciocinar,
   não de eu avisar preventivamente. Não sobre-proteger.
6. **Checkpoints de teach-back.** Pedir-lhe periodicamente (fim de secção
   grande, ou depois de uma pausa) para explicar o código de volta, por
   palavras dele. Isto revela lacunas reais (ex: achava que o pandas
   "transformava a imagem numa tabela") que testes de "corre ou não corre"
   não apanham.
7. **Calibrar autonomia por categoria, não de forma global.** Em padrões já
   dominados (ler `.env`, testar no terminal antes de integrar, manipular
   dicts/listas, controlo de fluxo) pode andar-se mais rápido, com revisão
   direta em vez de perguntas socráticas linha a linha. Em domínio
   genuinamente novo neste projeto — `requests`, forma de dados de uma API
   financeira, desenho de schema de BD com **múltiplas tabelas relacionadas**
   (o `storage.py` do Food Tracker só teve uma tabela, sem relações — isto é
   território novo) — manter o ritmo lento e guiado do início do Food
   Tracker.
8. **Sinal para subir autonomia numa categoria**: ele começa a apanhar bugs
   *antes* de serem apontados (aconteceu com `.copy()` e `pd.isna`). Quando
   isso acontecer numa área nova, é sinal para reduzir o nível de apoio
   nessa área especificamente.
9. **Pedido novo (2ª sessão da fase 5): quer também desenvolver mestria em
   arquitetura de sistemas**, não só sintaxe/código. Sempre que houver uma
   decisão de design maior (não "como escrevo este loop", mas "que padrão
   uso, que trade-off isto representa"), nomear explicitamente o princípio
   em jogo — ex: "build vs. buy/derive vs. fetch", "responsabilidade
   única", "acoplamento a serviços externos", "idempotência", "YAGNI",
   "não refatores código estável só porque tecnicamente podes". Isto é um
   eixo extra, não substitui o resto do método — continua a deixá-lo
   escrever o código.

## O que é este projeto

Bot de análise financeira: avalia balanços, DRs e fluxos de caixa de ~100
empresas, aplica o método Net-Net de Graham + rácio valor de
mercado/contabilístico + P/E + rendimento de dividendos, combina numa
pontuação (limiar 0.7 = subvalorizada), e manda alerta para **Telegram**
(era WhatsApp no plano original — mudado na fase 9, ver detalhe nessa
secção; motivo foi restrição real da plataforma WhatsApp/Meta, não
capricho). **Sem execução automática de trades** — só alerta, confirmação
manual.

Estimativa: núcleo ~90-96h (validada por outro Claude, inclui bónus de
scraping de investidores de valor). Ritmo esperado: 6-8h/semana.

## Decisões já tomadas (não voltar a discutir sem motivo)

- **API de dados financeiros: Finnhub (não FMP)** — mudança feita na 2ª
  sessão da fase 5, ver secção "Bloqueio resolvido" abaixo. A FMP fica no
  `.env` mas **não é usada no pipeline real** (só cobre ~10 mega-caps de
  graça, insuficiente). Guilherme tem key de ambas no `.env`
  (`FMP_API_KEY`, `FINNHUB_API_KEY`), não commitadas — ver `.env.example`
  (**nota**: `.env.example` ainda só lista a var da FMP, vale a pena
  atualizá-lo com `FINNHUB_API_KEY` também, ninguém fez isso ainda).
- **Sectores-alvo das ~100 empresas** (diversificação deliberada para reduzir
  correlação de risco): seguros, brinquedos e jogos, desenvolvimento
  imobiliário, software de aplicações, software e serviços de negócio,
  software e serviços de segurança, entretenimento, venda de peças
  automóveis, serviços e tecnologia de informação, programação e serviços
  aeroespaciais, energias.
- **"Rentáveis"** não é filtro de seleção prévia — só se aplica depois de
  puxar os dados financeiros de cada empresa (filtro pós-ingestão).
- **Bónus (não bloqueia o núcleo)**: cruzar a lista com holdings de
  investidores de valor (Buffett/Berkshire e outros "superinvestors") via
  **scraping de agregador tipo Dataroma** (~4-6h). SEC EDGAR 13F oficial fica
  **adiado para depois**, não é para já.

## Estado atual / próximo passo

Estrutura de projeto já criada (`src/`, `data/`, `.venv/`, `requirements.txt`
com `requests` + `python-dotenv`, `.env.example`, `.gitignore`). Deps
instaladas, `.env` com key real criado (key original foi colada em texto no
chat a certa altura — foi recomendado a Guilherme rodar a key na FMP; não
confirmado se o fez).

**Concluído**:
1. ✅ Deps instaladas, `.env` configurado.
2. ✅ `src/fmp_client.py` — testados 4 endpoints da FMP (todos para AAPL,
   market cap também testado em batch com AAPL/MSFT/GOOG), formas de dados
   confirmadas:
   - `income-statement` → 1 linha/ano, campos usados: `netIncome`, `eps`,
     `revenue`.
   - `balance-sheet-statement` → 1 linha/ano, campos usados:
     `totalCurrentAssets`, `totalLiabilities`, `totalStockholdersEquity`.
   - `market-capitalization-batch` → 1 linha/símbolo, campo `marketCap`
     (**REAL**, não INTEGER — já viu casas decimais em exemplos reais).
   - `dividends` → 1 linha/pagamento (trimestral), campos usados: `dividend`,
     `yield`, `date`, `frequency` (TEXT, ex: "Quarterly").
3. ✅ Schema da BD desenhado e implementado em `src/db.py`
   (`data/bot_financeiro.db`), 4 tabelas:
   - `empresas` (id, symbol, nome, sector) — fixo.
   - `dados_financeiros` (id, empresa_id FK→empresas, ano, + campos do
     income/balance statement) — 1 linha/ano.
   - `dividendos` (id, empresa_id FK→empresas, data, dividend, yield,
     frequency) — tabela separada de `dados_financeiros` por ter cadência
     trimestral vs. anual (não confundir "trimestral" com "trianual" — ele
     confundiu os termos uma vez, corrigido).
   - `pontuacoes` (id, dados_financeiros_id FK→dados_financeiros,
     data_calculo, market_cap_usado, score_net_net, score_pvc, score_pe,
     score_dividend_yield, pontuacao_final) — o limiar 0.7 fica como
     constante no código, não é guardado na BD.
   - Módulo segue o padrão testável sozinho (`criar_tabelas()` +
     `if __name__=="__main__":`).
   - Fórmulas dos 4 rácios já explicadas a ele (não voltar a re-explicar do
     zero, só relembrar se pedir): NCAV = totalCurrentAssets −
     totalLiabilities (Net-Net: marketCap < 2/3 NCAV); P/VC = marketCap /
     totalStockholdersEquity; P/E = marketCap / netIncome; dividend yield
     vem direto do campo `yield` da API.

4. ✅ **Fase 4 — camada de acesso à BD**, tudo em `src/db.py`:
   - Inserts: `inserir_empresa`, `inserir_dados_financeiros`,
     `inserir_dividendo`, `inserir_pontuacao` — todos com `?` placeholders +
     `conexao_dados_financeiros.commit()` + devolvem `lastrowid`.
   - Buscas: `buscar_dados_financeiros_recentes(cursor, empresa_id)`
     (`ORDER BY ano DESC LIMIT 1` + `fetchone()`), `buscar_empresa_id(cursor,
     symbol)` (`SELECT id` — não `SELECT *` — + `fetchone()[0]` para devolver
     só o int, não o tuplo).
   - Padrão de conexão: 1 conexão/cursor globais no módulo
     (`conexao_dados_financeiros` / `cursor_dados`), passados como argumento
     a todas as funções — decisão dele, para evitar abrir conexões a mais.
   - `if __name__=="__main__":` faz um round-trip de teste completo com
     dados fictícios (empresa "NFLX"/"Streamlandia Corp" fictícia — **isto
     ainda está gravado em `data/bot_financeiro.db`**; apagar o `.db` antes
     de começar a inserir dados reais na fase 5, ou o Guilherme já deve
     saber disso).
   - Bugs reais que ele apanhou e corrigiu sozinho, guiado: esquecer
     `sqlite3.connect()` sem caminho, trocar `INTEGER REFERENCES` por
     `REFERENCES INTEGER`, abrir uma 2ª conexão a um ficheiro `.db`
     diferente sem querer, confundir nome de coluna com nome de tabela
     (`FROM empresas_id` em vez de `FROM dados_financeiros`), e — recorrente
     3x na sessão — escrever `empresas_id` em vez de `id`/`empresa_id`
     (ver nota de padrão a corrigir, abaixo).
   - Conceito novo introduzido: transações/`commit()` (ele escolheu
     commitar a cada insert individual, preferindo segurança a
     performance — ok para escala de ~100 empresas), extrair valor de
     tuplo de 1 elemento (`fetchone()[0]`), porque não usar f-string em SQL
     (SQL injection) — usar sempre `?` + tuplo de parâmetros.

**BLOQUEIO RESOLVIDO (2ª sessão da fase 5) — mudámos de FMP para Finnhub:**

Confirmado com testes reais: FMP grátis = lista fixa de ~10 símbolos em
**qualquer** endpoint (income-statement, dividends, market-cap-batch todos
dão o mesmo padrão — só `RBLX, ADBE, MSFT, DIS, NFLX, ROKU, LMT, BA, XOM,
CVX` passam, 402 nos outros 90). Isto falhava o propósito do projeto (Net-
Net precisa de small-caps, não mega-caps).

Testámos o Finnhub como alternativa (Guilherme não quer pagar por upgrade —
respeitar):
- `stock/financials-reported?symbol=X&token=` → **100/100 símbolos
  cobertos**. Dá income+balance+cashflow "as reported" (dados brutos da SEC,
  tags XBRL tipo `us-gaap_NetIncomeLoss`, não nomes normalizados como a
  FMP). É diferente do endpoint `Financials` (esse sim é Premium/pago —
  normalizado entre empresas).
- `stock/profile2?symbol=X&token=` → dá `marketCapitalization` **já
  calculado** (não precisa de preço × ações à parte), também grátis, 100/100
  cobertos (confirmado só com um subconjunto por causa de rate limit
  atingido nos testes — ver nota de rate limit abaixo).
- `Dividends` e `Historical Market Cap` do Finnhub são Premium — mas os
  dividendos vêm de graça dentro do `cashflow` do `financials-reported`
  (`us-gaap_PaymentsOfDividends`), não precisamos do endpoint dedicado.

**Trade-off aceite conscientemente**: por ser "as reported" (não
normalizado), os nomes de campo XBRL variam entre empresas — o mesmo
problema que existiria indo direto ao SEC EDGAR, só que sem os outros 2
problemas do EDGAR (mapear symbol→CIK, parsear XML bruto — o Finnhub já
resolve os dois). Resolvido com uma função de fallback com lista de
candidatos por campo, ver abaixo.

**Mapeamento de campos confirmado** (testado com `JAKK`, ainda por validar
em mais empresas — pode variar):
```
revenue      → us-gaap_Revenues | us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax
netIncome    → us-gaap_NetIncomeLoss | us-gaap_ProfitLoss
eps          → us-gaap_EarningsPerShareBasic | us-gaap_EarningsPerShareBasicAndDiluted
totalCurrentAssets      → us-gaap_AssetsCurrent
totalLiabilities        → us-gaap_Liabilities
totalStockholdersEquity → us-gaap_StockholdersEquity | us-gaap_StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest
dividendos (cf)         → us-gaap_PaymentsOfDividends | us-gaap_PaymentsOfDividendsCommonStock
```

**Falta fazer, na ordem**:
1. Fase 5 — pipeline de ingestão para as ~100 empresas reais.
   ✅ Feito e testado ponta-a-ponta com sucesso (empresa real `JAKK`,
   valores confirmados batem com a API): `carregar_empresas_alvo()`,
   `obter_ou_criar_empresa()` (get-or-create idempotente),
   `buscar_valor(lista_items, candidatos)` em `src/ingestao.py` (fallback
   por lista de candidatos, ordem de prioridade importa — CUIDADO: ele
   escreveu isto errado 1x com os loops trocados, o mais prioritário só
   ganhava se calhasse vir primeiro na lista bruta da API, não pela ordem
   de `candidatos` — já corrigido), `ingerir_dados_financeiros(cursor,
   empresa_id, symbol, key)` — pede `financials-reported` +
   `profile2` (2 chamadas, menos que as 3-4 da FMP), extrai campos com
   `buscar_valor`, insere via `inserir_dados_financeiros`.
   - Ele próprio identificou e removeu variáveis não usadas
     (`marketcapitalization`, `cashflow`) da função — bom instinto de
     responsabilidade única (a função só deve encher `dados_financeiros`,
     não "aproveitar" dados que vieram de borla na resposta só porque
     estavam ali). Ficam para quando a fase 7 (pontuações) precisar deles —
     nessa altura decidir se vale a pena partilhar a chamada API ou pedir
     de novo.
   - **Rate limits confirmados reais** (429 em testes de hoje ao bater os
     100 símbolos seguidos sem espaçamento suficiente) — o loop principal
     vai mesmo precisar de backoff, não é só "por precaução".
   - ✅ **FASE 5 FUNCIONALMENTE COMPLETA** (3ª sessão): `ingerir_todas_as_empresas()`
     escrita e testada — corre as 100 empresas reais, **94/100 sucesso**.
     Backoff exponencial dentro de `ingerir_dados_financeiros` (loop
     `while delay<30`, dobra o delay em cada 429, `raise` explícito se
     esgotar tentativas — importante: o `raise` de "erro genérico" tem de
     estar **fora** do `if/elif`, senão dispara sempre, mesmo depois de um
     `continue` correto no 429 — ele já corrigiu isto). Loop principal
     (`ingerir_todas_as_empresas`) fica deliberadamente simples —
     `try/except Exception as e` à volta de 1 chamada, sem saber nada de
     `status_code` (essa responsabilidade vive só dentro de
     `ingerir_dados_financeiros`, decisão de arquitetura dele mesmo,
     validada — "onde o erro realmente acontece").
   - **6 falhas reais, padrão claro**: `SAP, CYBR, INFY, WIT, GLOB, SPOT` —
     todas empresas domiciliadas fora dos EUA (ADRs), que não submetem
     10-K padrão à SEC (usam 20-F) — `financials-reported` não tem dados
     estruturados da mesma forma para elas. Não é bug, é limitação real dos
     dados. Por tratar: aceitar como estão (ficam sem dados financeiros,
     ~6% da lista) ou trocar por equivalentes domésticas.
   - **Achado importante para a fase 7**: `totalCurrentAssets` e
     `totalLiabilities` vêm `None` para **100% dos sectores `seguros` e
     `desenvolvimento imobiliário`** (18/94 registos, confirmado com query
     agrupada por sector) — seguradoras e promotoras imobiliárias não usam
     classificação corrente/não-corrente nos balanços. **Net-Net (NCAV) vai
     ficar impossível de calcular para esses 2 sectores** com o
     mapeamento atual. Decisão a tomar na fase 7: procurar tags XBRL
     alternativas para estes sectores, ou aceitar que Net-Net não se aplica
     e tratar esses sectores de forma diferente na pontuação combinada (P/VC,
     P/E, dividend yield continuam a funcionar normalmente para eles).
   - **Falta ainda** (não bloqueia, fica para fase 6/7): dividendos
     (`cashflow`) ainda não entram na tabela `dividendos` — adiado
     deliberadamente para não fazer scope creep em `ingerir_dados_financeiros`
     (só enche `dados_financeiros`, responsabilidade única). Idem para
     `marketCapitalization` do `profile2` → tabela `pontuacoes`.
     `data/empresas_alvo.csv` e `.env.example` ainda não foram atualizados
     para refletir Finnhub como fonte principal.
2. ✅ **Fase 6 — filtro "rentáveis" pós-ingestão** — fechada (4ª sessão).
   `buscar_empresas_rentaveis(cursor)` em `src/db.py`, critério
   `netIncome > 0` (decisão dele, direto e simples). SQL puro com `JOIN`
   (ele pediu para praticar SQL em vez de pandas/`iterrows()` nesta fase —
   decisão validada com o princípio "filtra o mais perto possível da fonte
   dos dados", mesmo sendo desprezável à escala atual de ~94 linhas).
   **Resultado: 83/94 empresas rentáveis, 11 não.**
   Bugs corrigidos: `WHEERE` → `WHERE`, `empresa.symbol`/`empresa.id` →
   `empresas.` (mesmo padrão recorrente de nome de tabela errado, ver nota
   acima), `commit()` desnecessário removido (função só faz `SELECT`, não
   altera nada — não precisa de transação), assinatura alinhada para
   receber `cursor` como argumento (consistência com o resto do `db.py`).
3. ✅ **Fase 7 — lógica dos 4 rácios + pontuação combinada** — fechada (5ª
   sessão, a mais difícil do projeto até agora, ele próprio descreveu como
   "esta parte é a mais fdd do projeto lol"). Tudo em `src/ingestao.py`:

   **Pipeline**: `montar_dados_pontuacao(cursor)` (busca `dados_financeiros`
   + chama `buscar_dados_pontuacao` por empresa para market cap/dividendos
   frescos) → `loop_calculo_formulas(listadados)` (calcula rácios brutos +
   flags por empresa, agrupa num dict por `sector`) → `calcula_media_setores`
   (médias de P/VC, P/E, dividend yield **por sector**, usando os dados
   ingeridos, não benchmarks externos — decisão consciente, ver abaixo) →
   `normaliza_e_calcula_pontuacoes` (normaliza + combina) →
   `main_loop_pontuacoes` (insere tudo em `pontuacoes`).
   **Resultado final: 88/88 empresas pontuadas sem crash, `pontuacao_final`
   no intervalo [0, ~0.77] como esperado, 4 subvalorizadas (`BBW`, `LKQ`,
   `PARA`, `CRM`) com o limiar de 0.7.**

   **Decisão: médias por sector, não globais, e não do Damodaran.**
   Sectores diferentes têm perfis de rácios muito diferentes (software caro
   por natureza, seguros/energia baratos por natureza) — uma média global
   ia enviesar sistematicamente a favor de sectores "baratos por natureza".
   Considerámos benchmarks externos (Aswath Damodaran, NYU Stern — fonte
   real e séria, dados por sector em
   [pedata.html](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html)/
   [pbvdata.html](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pbvdata.html)/
   [divfund.html](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/divfund.html)),
   mas ficou de fora por custo (~3-5h extra: parsing de Excel + mapeamento
   manual dos 11 sectores próprios às ~90 categorias dele) — fica
   documentado como melhoria futura, não implementada.

   **Fórmula de combinação, evoluiu 3x nesta sessão**:
   1ª tentativa: pesos fixos por `if/elif` (19% Net-Net + 27%×3, ou 33.3%×3
   sem Net-Net) — funcionou para 2 combinações, mas explodiu quando
   apareceram mais casos-limite (ver achados abaixo) — a árvore de `if/elif`
   ficou insustentável (bugs de flags não repostas entre iterações, ordem
   errada de condições).
   2ª tentativa → **3ª e final: fórmula genérica orientada a dados**, não a
   `if/elif`. Cada rácio é um dict `{peso_base, score, invalido,
   fracao_perdida}`. Dois tratamentos possíveis quando um rácio é inválido:
   - **neutralizar** (`fracao_perdida=0.0`): exclui o rácio, o peso dele
     redistribui-se proporcionalmente pelos rácios válidos.
   - **penalizar** (`fracao_perdida=1.0`, ou um valor intermédio tipo
     `0.5`): o peso fica "queimado" (parcial ou totalmente), reduzindo o
     teto máximo da pontuação dessa empresa — decisão consciente dele:
     "a falta de dados também tem de ser punida".
   Fórmula: `peso_a_redistribuir = Σ peso_base×(1-fracao_perdida)` dos
   inválidos; `peso_total_validos = Σ peso_base` dos válidos; para cada
   válido, `peso_efetivo = peso_base + (peso_base/peso_total_validos)×peso_a_redistribuir`;
   `pontuacao = Σ peso_efetivo×score` só dos válidos. Isto cobre **todas**
   as combinações possíveis (testado até 4 flags em simultâneo) sem
   precisar de um branch por caso — generaliza bem, é o próprio Guilherme
   quem escolheu ir por aqui depois de ver a árvore de ifs descontrolar.

   **3 tipos de "dado inválido" descobertos e as suas regras**:
   - `nao_tem_assets` (falta `totalCurrentAssets`/`totalLiabilities`,
     sectores seguros/imobiliário) → **neutraliza** sempre (peso do Net-Net
     redistribui-se).
   - `totalStockholdersEquity` negativo (P/VC fica negativo/sem sentido) →
     depende do `netIncome` **dessa mesma empresa**: se positivo, é o
     padrão AZO/O'Reilly (recompras agressivas de ações — capital negativo
     mas empresa saudável) → **neutraliza**. Se negativo, é sinal real de
     risco/prejuízos acumulados → **penaliza** (perde peso todo).
   - `netIncome` negativo (P/E fica negativo/sem sentido) → sempre
     **penaliza** (decisão dele — "meti penalizar tudo", ao contrário do
     P/VC não há uma 2ª leitura "benigna" possível aqui).
   - Sector inteiro sem dividendos (`dividendyield` médio do sector = 0) →
     **penaliza parcialmente** (`fracao_perdida=0.5` — ele ajustou de 1.0
     para 0.5 a meio da sessão, achou que perder o peso todo era castigo
     a mais).

   **Achado crítico de dados**: a `calcula_media_setores` original somava
   **cegamente** todos os P/VC/P/E, mesmo os inválidos — isto causou uma
   média de sector **negativa** (`-10.42` em "venda de peças automóveis",
   por causa de `AZO`/`ORLY` com capital próprio negativo) que distorcia a
   pontuação de **todas** as outras empresas do sector (`GPC` chegou a sair
   com pontuação `11.99`, quando devia ser 0-1). Corrigido para excluir os
   inválidos da soma **antes** de calcular a média — usa os mesmos
   flags/índices que o `calculo_formulas` já produz por empresa (sem os
   recalcular, é só ler o que já está no tuplo — ele tentou chamar
   `calculo_formulas` outra vez dentro do `calcula_media_setores`
   passando-lhe o resultado já processado como se fosse a entrada
   original, índices completamente trocados — apanhado e corrigido).

   **Padrões de bug repetidos nesta sessão** (para reconhecer mais rápido
   se voltarem a aparecer): variáveis usadas antes de terem um valor por
   defeito atribuído em todos os ramos possíveis (`UnboundLocalError`,
   aconteceu ~5x só nesta fase — ele já reconhece o padrão sozinho a espaço
   mas ainda escreve o bug primeiro); nomes de chave inconsistentes entre
   escrever e ler um dict (`"preco_base"` vs `"peso_base"`); tentar mudar
   um elemento de um tuplo diretamente (`tuplo[i]=x`) — tuplos são
   imutáveis, mesmo erro já visto no `.append()` de tuplos lá atrás;
   confundir o output já processado de uma função com o seu próprio input
   (chamar a função outra vez sobre o resultado dela).

   **Nota (não urgente)**: `flagdividendosa0` no `calculo_formulas`
   verifica `dadosempresa[12]==0`, mas quando os dividendos vêm `None`
   (caso mais comum), `None==0` é `False` em Python — a flag não deteta
   esse caso corretamente. Não parece estar a causar resultado errado
   ainda (a proteção a nível de média de sector apanha isto por outro
   caminho), mas vale a pena rever/simplificar no futuro.

   **Falta ainda antes de fechar mesmo a fase 7** (pequeno, não é uma nova
   fase): `data/empresas_alvo.csv` e `.env.example` continuam por
   atualizar para refletir o Finnhub como fonte principal (nota antiga,
   ainda não resolvida).
4. ✅ **Fase 8 — limiar 0.7 + fluxo de decisão** — fechada (5ª sessão,
   mesma sessão da fase 7, mas rápida, ~30min — contraste direto com a
   fase 7: aqui não houve desenho novo nenhum, só reaproveitar padrões já
   dominados). `junta_dados_importantes_cliente(cursor)` em
   `src/ingestao.py` — `JOIN` encadeado de 3 tabelas
   (`pontuacoes → dados_financeiros → empresas`, pela cadeia de FKs),
   filtra `pontuacao_final >= 0.7`, devolve `market_cap_usado`,
   `data_calculo`, os 4 `score_*`, `pontuacao_final`, `symbol`, `nome`.
   **Resultado real: 4 empresas subvalorizadas — `BBW`, `CRM`, `PARA`,
   `LKQ`.**
   - Bug real e instrutivo: a 1ª versão do `JOIN` tinha as condições
     trocadas (`dados_financeiros.empresa_id == pontuacoes.dados_financeiros_id`,
     e `dados_financeiros.id == empresas.id` — comparações sem relação
     lógica nenhuma, PKs de tabelas diferentes). Não dava erro (os IDs
     coincidiam por acaso em parte dos dados, mascarando o bug), só depois
     de corrigido é que se viu que `PARA`/`LKQ` tinham `dados_financeiros_id`
     ≠ `empresa_id` — prova de que o bug era real, teria ligado nomes
     errados a pontuações certas. Lição: um `JOIN` sem erro não é o mesmo
     que um `JOIN` correto.
   - Mesmo padrão recorrente de nome de coluna/tabela errado (`empresas_id`
     em vez de `empresa_id`) — 5ª+ vez no projeto.
5. ✅ **Fase 9 — alerta automático** — fechada (5ª sessão, mesmo dia de
   maratona de fase 7/8/9). **MUDANÇA GRANDE: WhatsApp → Telegram**,
   decisão consciente dele, ver detalhe abaixo. Núcleo funcional do bot
   está fechado ponta-a-ponta agora: BD → pontuações → filtro 0.7 →
   alerta real recebido no telemóvel.

   **Porque WhatsApp foi abandonado**: qualquer mensagem que o **bot**
   inicia (não é resposta a algo que o utilizador escreveu) tem de usar um
   **Content Template pré-aprovado** — regra da própria Meta/WhatsApp, não
   é limitação de fornecedor específico (testámos isto a sério: bateu
   exatamente no mesmo muro com Twilio). Criar um template próprio exige o
   **Content Template Builder da Twilio**, que **não está disponível em
   conta trial** — só desbloqueia com upgrade pago (mínimo $20 de saldo
   inicial, sem mensalidade, mas ele não quis meter cartão para um projeto
   pessoal sem retorno — decisão respeitada, mesma lógica do "não pago
   FMP"). Usar um template genérico já feito (tipo "Appointment
   Reminders") era hack — mensagem financeira dentro de texto de "consulta
   médica" — ele recusou corretamente ("não me cheira").
   **Decisão final: Telegram.** Sem aprovação de templates, texto livre
   desde o minuto 1, sem verificação de negócio, sem cartão, biblioteca
   Python tão simples como a `twilio` (`python-telegram-bot`, mas no fim
   usámos só `requests.post` puro ao Bot API do Telegram, nem precisou da
   biblioteca completa).

   **Setup real**: bot criado via `@BotFather` no Telegram (`/newbot`) →
   token guardado em `.env` (nome real da var: `TELEGRAM`, não
   `TELEGRAM_BOT_TOKEN` como sugerido inicialmente — ele escolheu o nome
   dele, funciona igual) → `chat_id` descoberto via
   `GET https://api.telegram.org/bot{token}/getUpdates` depois de mandar
   uma mensagem ao bot (repara: só funciona se a mensagem for **recente**,
   updates antigos não aparecem) → envio real via
   `POST https://api.telegram.org/bot{token}/sendMessage` com
   `data={"chat_id":..., "text":...}`.
   **Conceito novo explicado**: `GET` (ler/consultar, o que já fazia em
   todo o projeto) vs. `POST` (agir/criar algo no servidor — mandar
   mensagem é uma ação, não uma leitura) — e porquê os parâmetros vão em
   `data=` (corpo do pedido) em vez da URL.

   **Funções em `src/ingestao.py`**:
   `junta_dados_importantes_cliente(cursor)` — `JOIN` encadeado de 3
   tabelas, filtra `pontuacao_final >= 0.7`, devolve tudo o que a mensagem
   precisa. `envia_mensagem_empresas_subvalorizadas(cursor)` — percorre o
   resultado, formata e manda 1 mensagem por empresa, com `try/except` a
   proteger o loop (uma falha não trava as outras) e lista acumulada de
   respostas devolvida no fim (não só a última — bug apanhado e corrigido,
   mesmo princípio já visto noutros loops do projeto: `return` fora do
   loop só devolve o último resultado a não ser que acumules numa lista
   antes).
   **Resultado real confirmado: 4/4 mensagens entregues** (`BBW`, `CRM`,
   `PARA`, `LKQ`) — confirmado por ele a receber no telemóvel.

   **Checkpoint conceptual importante que ele levantou sozinho**: será que
   `pontuacao_final >= 0.7` está na direção certa (não seria ao contrário,
   `<= 0.7`)? Verificado com ele passo a passo: os 4 rácios estão todos
   desenhados para "mais alto = mais barata face aos pares" (não "mais
   alto = maior/melhor empresa"), por isso o limiar está correto como
   está. Boa pergunta de sanidade, vale a pena documentar no README mais
   tarde para quem ler o código não ter a mesma dúvida.

   **Falta ainda**: `.env.example` continua sem `TELEGRAM`/`TELEGRAM_CHAT_ID`
   nem `FINNHUB_API_KEY` documentados (nota antiga, ainda não resolvida —
   já 3 fases sem ninguém tratar disto, considerar tratar como infra na
   próxima sessão).

   **Ronda extra pós-fase-9, mesma sessão — perguntas de sanidade sobre os
   dados reais que revelaram bugs genuínos**:
   - **`score_net_net` negativo/`-1`**: não é bug, é o sentinela deliberado
     de "Net-Net não se aplica" (falta `totalCurrentAssets`) — não entra
     como valor real na conta, só sinaliza para a fórmula genérica excluir
     esse componente.
   - **`score_dividend_yield = 1` em quase todas as subvalorizadas**:
     explicado, não é bug — sectores com muitas empresas sem dividendo
     (`0`) puxam a média do sector para baixo, por isso qualquer empresa
     que pague *alguma coisa* bate facilmente no teto de `1`.
   - **`score_pe > 1` em várias empresas reais (`CRWD=23`, `TTWO=11`,
     `ZS=10`...)** — bug real e corrigido: `normalizacaope` era sempre
     calculado, mesmo quando o P/E de base era negativo (empresas com
     `netIncome<0`), e esse valor bruto acabava gravado na BD mesmo que a
     fórmula genérica corretamente o excluísse da `pontuacao_final`. Fix:
     `if mediassetores[2]!=0 and empresa[4]>0: ... else: normalizacaope=0`
     (ele tentou primeiro `empresa[4]<1`, o que quebrava P/E normais como
     15/20/30 — confundiu o rácio bruto, sem limite superior, com o score
     normalizado, que sim deve andar entre 0-1; corrigido para só exigir
     positivo).
   - **`PARA` (Paramount Global) com market cap de ~$3.8M, absurdamente
     baixo** (~1000-100.000x menor que empresas vizinhas) — **confirmado
     real e repetível** via chamada fresca à API, não foi glitch pontual.
     Suspeita: fusão recente com a Skydance pode ter deixado o ticker
     `PARA` a apontar para uma entidade reorganizada muito menor, ou dados
     desatualizados no Finnhub. **Não é bug do código, é dado suspeito da
     fonte externa** — `PARA` pode estar a aparecer como "subvalorizada"
     por causa de dado mau, não sinal real. Preço por ação calculado
     (`$3.28`) confirma a mesma anomalia. Vale a pena, no futuro, uma
     verificação de sanidade (ex: rejeitar market caps abaixo de um
     mínimo plausível para uma empresa NYSE/NASDAQ real) — não
     implementado ainda.
   - **Preço por ação adicionado** (ele decidiu que o valor total da
     empresa, em milhares de milhões, não é útil numa mensagem de alerta
     — o preço por ação é o que se usa para decidir comprar). Nova coluna
     `preco_por_acao` em `pontuacoes`. Fonte: `profile2` já tinha
     `shareOutstanding`, só faltava extrair (não precisou de chamada API
     nova). Cálculo: `marketCap / (shareOutstanding × 1_000_000)` — mesmo
     cuidado de unidades de sempre (market cap já escalado para dólares
     em bruto, shares vem em milhões do Finnhub, precisa da mesma
     conversão). Bug apanhado no caminho: ele passou o `shareOutstanding`
     bruto direto para a coluna `preco_por_acao` sem nunca fazer a
     divisão — só transportou o dado pela cadeia toda sem o usar; e depois
     trocou `empresa[8]` (marketCap) por `empresa[9]` (netIncome) por
     engano no índice errado.
   - **Reflexão dele, válida**: os tuplos já vão em 15-16 posições, cada
     função "tem de saber de cor" o que está em cada índice — reconheceu
     isto sozinho como fonte da maior parte dos bugs de índice trocado da
     tarde. Fica registado como candidato a refactor futuro (fase 10/11):
     migrar de tuplos posicionais para `dict`/`namedtuple`/`dataclass` nas
     funções centrais (`calculo_formulas`, `normaliza_e_calcula_pontuacoes`),
     eliminaria esta classe de bug por completo. Não feito ainda,
     deliberadamente adiado para não interromper o fluxo a meio.
   **Resultado final confirmado, 3 mensagens reais entregues** com preço
   por ação plausível (`BBW $12.54`, `LKQ $254.79`, `PARA $3.28` — esta
   última reflete a anomalia de dados já documentada acima, não confiar
   nela).

   **⚠️ PRÓXIMO PASSO PENDENTE, explicitamente lembrado por ele para a
   próxima sessão**: trocar `0` por `None` na BD (`score_pvc`/`score_pe`/
   etc.) quando o componente correspondente é `invalido` — combinado
   antes de pararmos, ainda não implementado. Lembrete: usar as **flags
   de validade** já existentes (`empresa[6]==1`, `empresa[11] or
   empresa[12]`, `empresa[14]`, `mediassetores[3]==0`) para decidir
   quando gravar `None`, não o valor do score em si (`0` é ambíguo em
   todos os 4 rácios — pode ser "válido e calhou dar 0" ou "inválido,
   fallback" — só as flags distinguem os dois casos com certeza). O
   `None` só deve entrar no **tuplo final gravado na BD**, não nas
   variáveis internas usadas no cálculo da `pontuacao` (essas continuam a
   precisar de um número, não de `None`, para a fórmula genérica
   funcionar).
6. ✅ **Fase 10 — testes/afinação end-to-end** — fechada (6ª sessão,
   começou com o `None` pendente da sessão anterior, depois passou a
   testes de robustez a sério).

   **Peça 0 (pendente de ontem)**: `None` em vez de `0` para rácios
   inválidos — fechado. Fonte de verdade são as **flags de validade**
   (não o valor do score, que é ambíguo — pode ser "0 real" ou "0
   fallback" em todos os 4 rácios). `None` só entra no **tuplo final
   gravado na BD**, nunca nas variáveis internas usadas para calcular a
   `pontuacao` (essas continuam a precisar de número). Confirmado com
   dados reais: `max(score_pe)=0.93` agora (nunca mais >1), `None`
   aparece exatamente onde esperado (10 empresas sem P/E válido, 36 sem
   dividend yield válido, 1 sem P/VC válido).

   **`main.py`/`correr_bot_completo(cursor)`**: encadeia
   `ingerir_todas_as_empresas()` → `main_loop_pontuacoes()` →
   `envia_mensagem_empresas_subvalorizadas()`. Testado do zero absoluto
   (BD apagada, `criar_tabelas()`, 1 chamada só) — corre sozinho, sem
   intervenção manual, ponta-a-ponta. Decisão: bot corre **1x/dia**, via
   `cron` do sistema operativo (não lógica dentro do Python) — fica para
   a fase 11/deployment.

   **4 cenários extremos testados, 2 bugs reais encontrados e
   corrigidos**:
   1. **Correr o bot 2x sem limpar a BD** → revelou que `empresas` estava
      protegida (idempotente, `100` sempre), mas `dados_financeiros`
      **duplicava** (`94→188`) e `pontuacoes` **quase triplicava**
      (`88→265`, e 9 mensagens em vez de 3-4 — mesma empresa alertada 2x).
      Causa: `inserir_dados_financeiros` não tinha proteção nenhuma,
      inseria sempre uma linha nova. **Fix**: mesmo padrão "get or create"
      do `obter_ou_criar_empresa`, agora usando
      `buscar_dados_financeiros_recentes` como o "buscar". Bug de
      transição apanhado no caminho: tentou reaproveitar `inserir_empresa`
      por engano (confundiu os 2 padrões parecidos, mas para tabelas
      diferentes), e depois `insercao_dados.lastrowid` chamado sobre um
      `int` simples no ramo "já existe" (`AttributeError`, mesma família
      de erro do `.append()` em tuplos de sessões anteriores — nem tudo
      tem `.lastrowid`, só resultados de `execute()`).
   2. **`pontuacoes` continua a duplicar mesmo depois do fix acima** — mas
      aqui foi **decisão de design**, não bug: `pontuacoes` deve mesmo
      acumular **histórico** (o `market_cap_usado` muda todos os dias,
      faz sentido guardar a evolução ao longo do tempo, ao contrário de
      `dados_financeiros`/`empresas` que são estáveis). O problema real
      era só `envia_mensagem_empresas_subvalorizadas` estar a alertar
      sobre **todas** as pontuações históricas acima de 0.7, repetindo o
      mesmo alerta dia após dia. **Fix**: subquery SQL "máximo por grupo"
      em `junta_dados_importantes_cliente` — `WHERE pontuacoes.id IN
      (SELECT MAX(pontuacoes.id) FROM pontuacoes JOIN dados_financeiros
      ... GROUP BY empresa_id)` — só considera a pontuação **mais
      recente** de cada empresa antes de aplicar o limiar de 0.7.
      Primeira vez que ele usa este padrão SQL ("greatest-n-per-group"),
      levou algumas rondas de bugs de sintaxe (subquery entre aspas
      simples em vez de parênteses — vira string, não subquery real;
      `id` ambíguo entre 2 tabelas com a mesma coluna; um `in IN`
      duplicado; um resultado de teste (`jhahaha`) deixado no código a
      **contaminar** o cursor partilhado — 2º `execute()` no mesmo cursor
      substitui o resultado pendente do 1º, lição de arquitetura sobre
      cursores partilhados). Confirmado com teste real: correr
      `main_loop_pontuacoes` outra vez depois do fix não duplica alertas
      (`4` empresas, nenhuma repetida).
   3. **Falha de rede genuína** (não um código de erro da API — uma
      exceção real do Python, tipo `ConnectionError`, simulada com
      `unittest.mock.patch`) — confirmado que o `try/except` no nível
      certo (`ingerir_todas_as_empresas`) apanha qualquer tipo de
      exceção, não só os casos de status code já tratados no backoff
      interno. Pipeline continuou para as outras empresas sem parar.
   4. **Zero empresas subvalorizadas** (nenhuma passa o limiar nesse dia)
      — `envia_mensagem_empresas_subvalorizadas` devolve lista vazia sem
      tentar mandar nada, sem crash.

   **Nota cosmética para a fase 11**: mensagens de alerta mostram `None`
   cru quando um rácio é inválido (ex: "score pe None") — devia ser algo
   tipo "N/A" para quem lê a mensagem, não urgente.
7. Fase 11 — polish/README (`.env.example` desatualizado há várias fases,
   README ainda não escrito, "None" cru nas mensagens do Telegram,
   considerar o refactor de tuplos posicionais → dict/dataclass que ele
   próprio identificou como problema recorrente).
8. Bónus (não bloqueia): scraping tipo Dataroma de holdings de
   superinvestors.

Estimativa validada: núcleo ~90h, ritmo 6-8h/semana. Mapa de fases completo
(horas/%) já foi mandado a ele no chat pelo menos 2x — se pedir "manda as
fases outra vez", é referir-se a isto; reconstrói a tabela a partir desta
lista se precisar.

**Tempo real vs. orçamentado**: fase 3 orçamentada 5h, real ~3h. Fase 4
orçamentada 7h, real ~3.5-4h. Fase 5 (18h orçamentadas) fechada em 3
sessões, ~5-6h reais. Fase 6 (3h orçamentadas) fechada rápido, quase sem
atrito. **Fase 7 (18h orçamentadas) foi a primeira a não vir claramente
abaixo do orçamento** — foi uma sessão inteira e longa, densa em bugs
genuinamente difíceis (não sintaxe, lógica de negócio + matemática +
arquitetura a evoluir 3x). Não tenho o tempo real exato, mas foi
claramente a fase mais cara até agora em esforço de sessão, mesmo que
ainda dentro ou perto do orçamento em horas. Isto é esperado e não é sinal
de alarme — é território genuinamente novo (desenho de fórmula de negócio
do zero), consistente com o padrão do método de ensino de manter o ritmo
guiado em domínio novo.

Ele confirmou explicitamente que gostou do ritmo nas fases anteriores
("impecável", "curti do método") e reconhece o padrão sozinho ("fizemos
literal 12 horas de trabalho em 7"). Não é motivo para acelerar o método
guiado por defeito. Continuar a comparar tempo real vs. orçamentado por
fase à medida que ele reportar, para recalibrar as estimativas seguintes.

**Padrão a vigiar (não é urgente, só ficar atento)**: ele confunde nomes de
coluna (ex: escreve `empresas_id` em vez de `id`/`empresa_id`) com alguma
frequência — 3x na sessão da fase 4, em funções diferentes. Atualmente só
apanha isto pelo erro do SQLite em runtime, não confere o `CREATE TABLE`
antes de escrever a query. Ainda não é o momento de subir autonomia nesta
sub-área especificamente (falta o sinal do ponto 8 do método de ensino: ele
apanhar isto *antes* de correr) — mas vale a pena nudge-lo explicitamente
pra esse hábito da próxima vez que acontecer, em vez de só corrigir de
novo.

**Novo padrão (sessão 2 da fase 5)**: navegar níveis de dict/JSON aninhado
(`resposta["data"][0]["report"]["bs"]`) — ele salta níveis (esqueceu
`["data"]` antes do `[0]`, 2x seguidas até corrigir). Também deu o mesmo
nome (`data`) à variável Python e à chave `"data"` do JSON, o que o
confundiu ativamente — ele próprio identificou isto como causa da confusão
quando apontado. Vale a pena, da próxima vez que aparecer JSON aninhado,
sugerir nomes de variável que não colidam com chaves do próprio payload.

**Nota de segurança**: a key do Finnhub foi exposta em texto no chat (a
doc deles preenche os exemplos com a key real de quem está logado — ele não
reparou da 1ª vez). Recomendado rodar a key no dashboard do Finnhub, tal
como já tinha acontecido com a da FMP — não confirmado se ele já o fez para
nenhuma das duas.

## Projeto irmão

O Food Tracker (`/home/guidelgado/projetos/food-tracker`) é um projeto
anterior já fechado (MVP + 3 features extra + README), feito com o mesmo
Guilherme e o mesmo método de trabalho. Está a ser mantido por outra sessão
do Claude Code, que vai tratar da v2 (React + deploy). Não é preciso mexer
lá, mas serve de referência do nível de código dele e do estilo de trabalho
que resultou bem.
