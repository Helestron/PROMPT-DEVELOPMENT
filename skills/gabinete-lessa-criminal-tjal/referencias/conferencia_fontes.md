# Conferência de jurisprudência, dispositivos legais e regimentais (Fase 2-B)

Referência da Fase 2-B do SKILL.md e do passo R3 do Modo B. Regra-mãe: **só se cita o que
existe, diz o que se afirma e está vigente** — conferido na fonte, transcrito e registrado no
ledger antes da redação. Redigir de memória e conferir depois obriga a reescrever fundamentações
inteiras.

## 1. Ledger de verificações (`_verificacoes.json`)

Uma entrada por citação candidata, no esquema documentado em `scripts/conferir_citacoes.py`:
`id`, `tipo` (`precedente`, `sumula`, `tema`, `dispositivo`, `regimento` ou `doutrina`),
`chave`, órgão, relator, datas de julgamento e publicação, `fonte`, **`trecho_literal`**, para
dispositivos e regimento a data `redacao_vigente_conferida_em`, e `status` (`VERIFIED`,
`REJECTED` ou `PENDENTE`). A minuta só pode citar entradas `VERIFIED`; `conferir_citacoes.py --ledger` é
portão da Fase 4 — citação sem entrada, `REJECTED` ou `PENDENTE` bloqueia a versão limpa, e,
havendo duas entradas para a mesma citação, prevalece a mais restritiva. Precedente do TJAL
citado pelo número CNJ entra no ledger como `precedente`, com o próprio número na chave; passe
`--processo <número>` para que o número do feito não seja tomado por citação.

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
memória do modelo produzem, com frequência conhecida, ementa parafraseada, número trocado e
precedente inexistente. Método: varredura nas pistas → confirmação de cada candidato na fonte
primária → transcrição literal e dados completos → só então a redação.

**Delegação**: a verificação pode ser distribuída a subagentes, em consultas agrupadas por tema;
cada um devolve os campos do ledger, com o trecho literal. O resultado de subagente também é
conferido por amostragem antes de virar `VERIFIED`.

## 3. Dispositivos regimentais — Regimento Interno do TJAL

Texto vigente **disponível no skill**: `referencias/ritjal_integral.txt`, extraído do PDF
consolidado fornecido pelo gabinete em 01/10/2026 (`referencias/ritjal_consolidado_emenda19.pdf`;
Regimento aprovado pelo Pleno em 20/08/2024, com as Emendas n.ºs 17/2025, 18/2026 e 19/2026),
que prevalece em caso de dúvida sobre a extração. O PDF marca o texto revogado **por tachado**; a
extração (`scripts/extrair_regimento.py`) o exclui do texto vigente e o guarda em
`referencias/ritjal_revogados.txt` (antigos parágrafos únicos dos arts. 32 e 63 e redações
anteriores dos arts. 93 e 99), apenas para consulta histórica. Mapa temático com transcrições:
`referencias/regimento_tjal.md`.

1. **Consulta e transcrição por script**, nunca de memória:
   `python scripts/regimento.py 62 63 192` devolve o texto vigente de cada artigo. A anotação
   "(Incluído/Alterado pela Emenda …)" que acompanha os dispositivos emendados é do PDF e não
   integra a citação; o script avisa quando ela está presente.
2. **Portão regimental**: `python scripts/regimento.py --fila Minuta_….docx` lista os artigos do
   RITJAL citados na minuta, com o texto vigente, no esquema do ledger (`tipo: "regimento"`,
   status `PENDENTE`). Confira a **pertinência** (o artigo diz o que a minuta afirma?), mude o
   status para `VERIFIED` ou `REJECTED` e só então rode `conferir_citacoes.py`.
3. **Remissões externas do Regimento**: o RITJAL remete à Lei n.º 6.564/2005 (Código de
   Organização Judiciária) quanto ao quantitativo de Desembargadores (art. 2º), à composição e ao
   quórum mínimo das Câmaras (art. 6º) e à eleição de sua presidência (art. 16); o quórum da
   Câmara Criminal, porém, está no próprio Regimento (art. 141). Remete também a Resoluções do
   TJAL (lavratura de acórdãos — art. 181; sessões virtuais — art. 152; plantão — art. 75) e ao
   Código de Normas da CGJ/AL (RESE interposto por apenas um ou alguns dos réus, ou por um réu
   enquanto outro apela — arts. 322 e 327). O Código de Normas está no skill
   (`referencias/cgj_normas_integral.txt`; arts. 797 e 798); a Lei n.º 6.564/2005 e as Resoluções
   não estão — cite-as apenas depois de obtido o texto oficial.
4. **Casos omissos e dúvidas**: aplicam-se, no que couber, o RISTF e o RISTJ, nessa ordem
   (art. 392); havendo divergência de interpretação regimental ou ausência de previsão interna,
   qualquer Desembargador pode, antes de votar, pedir o pronunciamento prévio do Pleno (art. 389,
   I e II).
5. **Atualização**: nova emenda → `python scripts/extrair_regimento.py <PDF consolidado>`
   (requer `pip install pdfplumber`), depois `python scripts/gerar_mapa_regimento.py`, e
   reconferir todas as entradas `regimento` do ledger anteriores à emenda.

**Jurisprudência do TJAL**: repositórios oficiais são o DJe e a Revista do TJAL (art. 299); o
Tribunal mantém banco de precedentes e de teses de IRDR e IAC (arts. 297 e 298) e relação de
súmulas (art. 300). Súmula do TJAL e tese de IRDR ou IAC autorizam o desprovimento monocrático
(art. 62) — confira sempre a vigência no banco oficial.

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

**Precedentes qualificados** (súmula vinculante, repercussão geral, recursos repetitivos, IAC e
IRDR): analise sempre a adequação do caso; na minuta, só se trata do tema quando aplicado ou
invocado por parte (`estilo_gabinete.md`, item 6.a). Suspensão nacional determinada em tema
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
