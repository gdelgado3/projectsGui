# Prompt vision, para a análise do prato — a prompt dada à API do Claude
# para a análise das fotos (a dos rótulos usa a ROTULO_PROMPT, em baixo).
VISION_PROMPT = """Analisa esta foto de comida. Identifica cada componente distinto e estima
a porção em gramas.

Contexto: o utilizador é português. Se identificares pratos tipicamente
portugueses (bacalhau à brás, carne de porco à alentejana, francesinha, etc.),
usa esses nomes específicos.

Regras:
- Cada componente distinto conta separadamente (arroz + carne + salada = 3 items).
- Molhos visíveis contam como componente separado.
- Se não conseguires identificar algo, mete "confianca" baixa e descreve.
- Se a foto NÃO for de comida, devolve lista vazia + observação.

Devolve APENAS este JSON, sem mais texto:

{
  "alimentos": [
    {
      "nome": "arroz branco cozido",
      "porcao_g": 150,
      "confianca": 0.85,
      "notas": "aparenta ser uma dose média"
    }
  ],
  "porcao_total_visivel": "prato de tamanho médio",
  "observacoes_gerais": "prato equilibrado com fonte de proteína, hidratos e vegetais"
}"""

# Prompt para a leitura dos rótulos (usada por ler_rotulo).
ROTULO_PROMPT="""Analisa esta foto de um rótulo ou tabela de valores nutricionais de um
produto embalado. Lê os valores impressos exatamente como aparecem na
imagem — não estimes, não adivinhes, transcreve o que está escrito.

Regras:
- Usa os valores "por 100g" se estiverem disponíveis.
- Se só houver valores "por dose/porção", usa esses e indica a base usada.
- Se não conseguires ler algum valor com confiança, usa null nesse campo.
- Se a imagem não for uma tabela nutricional, devolve "erro": true.

Devolve APENAS este JSON, sem mais texto:

{
  "nome_produto": "iogurte proteico",
  "kcal": 65,
  "proteina_g": 10,
  "hidratos_g": 4,
  "gordura_g": 1.5,
  "base_quantidade":10,
  "base_unidade":"g",
  "erro": false
}"""
