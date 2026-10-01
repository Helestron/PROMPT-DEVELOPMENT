# Conferência de jurisprudência, dispositivos legais e regimentais (Fase 2-B)

Referência da Fase 2-B do SKILL.md e do passo R3 do Modo B. Regra-mãe: **só se cita o que
existe, diz o que se afirma e está vigente** — conferido na fonte, transcrito e registrado no
ledger antes da redação. Redigir de memória e conferir depois obriga a reescrever fundamentações
inteiras.

## 1. Ledger de verificações (`_verificacoes.json`)

Uma entrada por citação candidata, no esquema documentado em `scripts/conferir_citacoes.py`:
`id`, `tipo` (precedente, súmula, tema, dispositivo, regimento, doutrina), `chave`, órgão,
relator, datas de julgamento e publicação, `fonte`, **`trecho_literal`**, para dispositivos e
regimento a data `redacao_vigente_conferida_em`, e `status` (`VERIFIED`, `REJECTED`,
`PENDENTE`). A minuta só pode citar entradas `VERIFIED`; `conferir_citacoes.py --ledger` é
portão da Fase 4 — citação sem entrada, `REJECTED` ou `PENDENTE` bloqueia a versão limpa.

O ledger é **por lote**, mas entradas `VERIFIED` podem ser reaproveitadas em lotes seguintes
quando a conferência tiver menos de 30 dias e a fonte não indicar alteração (súmula, tese ou
dispositivo); acima disso, reconfira.

## 2. Hierarquia de fontes

**Primárias (autorizam citação)**

- **STF**: pesquisa de jurisprudência; portais de repercussão geral (temas e teses); súmulas
  e súmulas vinculantes; Informativos.
- **STJ**: pesquisa de jurisprudência (acórdãos e decisões); Jurisprudência em Teses;
  Informativos; Súmulas anotadas; temas repetitivos (se a página de temas estiver bloqueada à
  automação, extraia os dados dos próprios acórdãos de afetação e de mérito).
- **TJAL**: jurisprudência de 2º grau (consulta de acórdãos) — essencial para conhecer a
  **orientação da Câmara Criminal** e os precedentes do próprio Desembargador; nunca prevalece
  sobre precedente qualificado do STF/STJ (art. 927 do CPC, aplicado por analogia — art. 3º do
  CPP), mas fundamenta a uniformidade e a coerência interna (art. 926 do CPC).
- **Planalto** (legislação federal compilada): texto vigente e histórico de redações; para o
  direito penal material, a redação vigente **na data do fato** e eventual lei posterior mais
  benéfica.
- **Diário Oficial / portal do TJAL**: Regimento Interno, resoluções e atos normativos do
  Tribunal (item 3).
- **CNJ**: resoluções e recomendações (atos normativos).

**Comprovação de autenticidade**: o inteiro teor ou a ementa oficial reproduzidos na plataforma
JusBrasil (sessão autenticada) valem como comprovação, ao lado dos sítios oficiais, registrada a
origem no ledger.

**Pistas, nunca citação**: JusIA e qualquer assistente generativo, blogs, resumos e a própria
memória do modelo — produzem ementa parafraseada, número trocado e precedente inexistente com
frequência conhecida. Método: varredura nas pistas → confirmação de cada candidato na fonte
primária → transcrição literal e dados completos → só então a redação.

**Delegação**: a verificação pode ser distribuída a subagentes, em consultas agrupadas por tema;
cada um devolve os campos do ledger, com o trecho literal. O resultado de subagente também é
conferido por amostragem antes de virar `VERIFIED`.

## 3. Dispositivos regimentais — Regimento Interno do TJAL

Competências da Câmara Criminal e da Seção/Pleno, poderes do relator para decidir
monocraticamente, revisão, vista, pauta e sessões (presenciais e virtuais), sustentação oral,
embargos de declaração, questões de ordem e prazos internos são **matéria regimental**. Regras:

1. Antes do primeiro lote, obtenha o texto vigente do RITJAL no portal oficial do Tribunal e
   salve-o em `referencias/ritjal_integral.txt` (texto pesquisável), com a data da obtenção e as
   emendas consolidadas. Preencha `referencias/regimento_tjal.md` com o mapa dos artigos que o
   gabinete usa, **cada um transcrito do texto obtido**.
2. Toda citação de artigo regimental passa pelo ledger com `tipo: "regimento"`, trecho literal
   e data de conferência. O mapa de `regimento_tjal.md` orienta; o integral autoriza.
3. Havendo emenda regimental posterior à data do mapa, reconfira os artigos afetados.
4. Regimentos do STF e do STJ entram apenas quando a matéria os exigir (v.g., admissibilidade de
   recursos aos tribunais superiores), pelo mesmo procedimento.

## 4. Dispositivos legais — vigência e pertinência

Para cada artigo citado: (i) existe com o conteúdo afirmado? (ii) a redação é a vigente (ou a da
data do fato, no direito material)? (iii) foi declarado inconstitucional, suspenso ou teve
interpretação conforme (v.g., dispositivos da Lei n.º 13.964/2019 objeto de ADIs no STF)? (iv)
o parágrafo e o inciso indicados são os corretos? Registre no ledger; erro de inciso é erro.

## 5. Precedentes — pertinência, não só existência

Para cada precedente: (i) existe com aquele número, órgão e relator; (ii) o trecho invocado está
no inteiro teor ou na ementa oficial; (iii) a tese **serve ao caso** (ratio decidendi, não obiter
dictum); (iv) não foi superado (overruling), cancelado ou modulado; (v) se for de turma, há
divergência entre as Turmas criminais do STJ (Quinta e Sexta)? Registre a divergência e a
posição da Terceira Seção, se houver.

**Precedentes qualificados** (súmula vinculante, repercussão geral, recursos repetitivos,
IAC, IRDR do TJAL): analise sempre a adequação do caso; na minuta, só se trata do tema quando
aplicado ou invocado por parte (estilo, item 5.a). Suspensão nacional determinada em tema
afetado alcança o processo? Decidir feito suspenso é risco de nulidade.

**Prevalência**: divergência entre o STJ/STF e o entendimento da Câmara ou do próprio
Desembargador → a minuta segue o precedente qualificado, com o registro da divergência em
vermelho na versão anotada; sendo a orientação do STJ não vinculante e havendo posição firme da
Câmara em sentido diverso, apresente as duas linhas na anotada e siga a do Desembargador,
marcando o risco recursal.

## 6. Doutrina

Autor, obra, edição, editora, ano e página **conferidos** (catálogo da editora, biblioteca
digital, exemplar disponível). Sem conferência, não se cita; prefira não citar doutrina a citar
de memória.
