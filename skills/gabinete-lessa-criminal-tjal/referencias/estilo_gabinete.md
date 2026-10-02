# Padrão de redação das minutas do gabinete

Referência da Fase 3 do SKILL.md. **Origem**: as regras de forma do skill `lote-minutas-esaj`
(consolidadas por correções expressas do magistrado de 1º grau em 08–09/2026), adaptadas às
peças de 2º grau. Valem como padrão inicial do gabinete **até que o Desembargador as altere**;
os modelos do gabinete (`pastas.modelos_gabinete`) orientam a identidade estilística, sem afastar
as regras mensuráveis do portão, e cada correção do Desembargador é registrada no caderno de
bordo e incorporada pelo autodesenvolvimento (SKILL.md, item 8). O portão
`scripts/verificar_minuta.py` aplica as regras mensuráveis; as demais são da revisão adversarial.
O tipo indicado em cada linha da tabela abaixo é o valor de `--tipo` no portão e, nas peças que
vão ao SG5, a chave de `saj_sg5.categorias` e `saj_sg5.modelos` em `config/gabinete.json` (a nota
de revisão é interna e não vai ao sistema).

## 1. Peças e estrutura

| Peça | Estrutura | Fecho do relatório | Última linha |
|---|---|---|---|
| Despacho — tipo `despacho` | DESPACHO → comando(s) | — | Publicações e intimações via DJEN |
| Decisão monocrática (liminar; prejudicialidade; desprovimento nas hipóteses do art. 62 do RITJAL; indeferimento liminar de HC e de embargos de declaração; deserção e desistência; extinção da punibilidade; demais hipóteses expressas — SKILL.md, Fase 2, item 2) — tipo `decisao` | DECISÃO MONOCRÁTICA → relatório → fundamentação → dispositivo → comandos à Secretaria | Brevemente relatado, passo a decidir. | Publicações e intimações via DJEN |
| Relatório do relator, com remessa ao revisor (RITJAL, arts. 49 e 50) — tipo `relatorio` | RELATÓRIO → eventos | É o relatório. | À douta revisão. |
| Voto do relator — tipo `voto` | RELATÓRIO → eventos → É o relatório. → VOTO → admissibilidade → questões de ofício → preliminares → mérito → dosimetria → consectários → dispositivo | É o relatório. | É como voto. |
| Voto de referendo de liminar concessiva (RITJAL, art. 63, §§ 3º a 5º) — tipo `referendo` | VOTO (REFERENDO DE LIMINAR) → síntese da decisão referendada (fls.) → razões para mantê-la → proposta de referendo | — | É como voto. |
| Voto divergente — tipo `voto_vogal` | VOTO DIVERGENTE → delimitação do ponto → fundamentação → dispositivo próprio | — (adota o relatório do relator) | É como voto. |
| Voto-vista, sempre escrito (art. 174) — tipo `voto_vista` | VOTO-VISTA → delimitação → fundamentação → dispositivo (ou adesão fundamentada) | — | É como voto. |
| Declaração de voto (arts. 167, parágrafo único, e 176) — tipo `declaracao_voto` | DECLARAÇÃO DE VOTO → fundamentos próprios | — | É como voto. |
| Fundamentos do voto vencido, em 72 horas (arts. 179 e 180) — tipo `voto_vencido` | VOTO VENCIDO → ponto de divergência → fundamentação → conclusão | — | É como voto. |
| Relatório retificado ou completado pelo revisor (art. 49, I) — tipo `relatorio` | RELATÓRIO → acréscimos e correções com fls. | É o relatório. | — |
| Ementa — tipo `ementa` | padrão de ementa adotado pelo TJAL (lavratura conforme Resolução do TJAL — RITJAL, art. 181; conferir também a recomendação do CNJ sobre padronização de ementas e o modelo do gabinete). Havendo divergência entre ementa e voto, **prevalece o voto** (art. 185): a ementa reproduz fielmente a tese e o resultado | — | — |
| Nota de revisão (interna) — tipo `nota_revisao` | `referencias/revisao_votos.md`, R5 | — | — |

As epígrafes admitidas são **apenas** os nomes das peças e das partes estruturais (RELATÓRIO,
VOTO, EMENTA etc.). A ementa tem estrutura própria e não se submete às regras de texto corrido.

## 2. Relatório

a. **Um parágrafo por evento**, na ordem dos autos: denúncia e seu recebimento; resposta à
acusação; instrução (registro da audiência e das fls. dos termos, sem narrar o que nela se
passou); alegações finais; sentença (condenação/absolvição, capitulação, pena, regime); razões;
contrarrazões; parecer da Procuradoria-Geral de Justiça. No HC: impetração, ato coator, pedido,
decisão liminar, informações, parecer.

b. **Síntese, não transcrição**: de cada peça vai o que pede, alega ou decide, na medida em que
importe ao julgamento, sempre com as fls. — sem resumo tópico a tópico, sem inventário de
documentos, sem reprodução de trechos.

c. **Sem datas e horários** de protocolos, juntadas, publicações ou intimações. Data que seja o
próprio objeto da decisão (tempestividade controvertida, prescrição, tempo de prisão para excesso
de prazo) vai para a fundamentação, demonstrada com as fls.

d. **Fecho invariável** conforme a peça (tabela do item 1), em parágrafo próprio.

## 3. Fundamentação

a. **Ordem lógica**: admissibilidade (sempre expressa no voto, em período sucinto; análise
detalhada só quando controvertida) → matérias de ordem pública e de ofício → preliminares →
mérito → dosimetria → consectários.

b. **Enfrentamento de todas as teses** das partes (art. 93, IX, da CF; art. 315, § 2º, do CPP;
art. 489, § 1º, do CPC, aplicado por analogia), uma a uma, acolhendo-as ou rejeitando-as com
fundamento verificável, apontando o equívoco na invocação de norma ou precedente impróprio e o
instituto correto.

c. **Valoração da prova com fls.** — a minúcia é da análise (dossiê, matriz); à minuta vai a
valoração que decide.

d. **Densidade argumentativa**: por questão enfrentada, em regra, o dispositivo legal vigente,
uma obra doutrinária conferida e um precedente verificado — os que melhor sustentam a conclusão;
amplie só quando a controvérsia o exigir. Concisão é atributo da forma; profundidade, da
fundamentação.

e. **Extensão contida**: suprime-se o que não decide — repetição do relatório, transcrição longa
de peças e ementas, precedentes em série, digressão teórica, fórmulas de estilo —, nunca
argumento, prova ou questão. Parágrafo que possa ser retirado sem deixar tese sem resposta deve
ser retirado.

f. **Contraditório sobre fundamento novo**: matéria não debatida pelas partes, **ainda que
cognoscível de ofício**, exige oportunidade de manifestação. Antes da sessão, o fundamento é o
art. 10 do CPC, por analogia (art. 3º do CPP) — despacho prévio de manifestação; surgida a
matéria nos debates ou na vista, o RITJAL manda suspender o julgamento e abrir cinco dias às
partes, salvo manifestação na própria sessão (art. 161, caput e §§ 3º e 5º), e o relator que
discorde submete a questão ao órgão (§ 6º). Na minuta, marque o ponto em vermelho e indique o
caminho. A cautela só cede diante de constrangimento ilegal à liberdade que não admita espera
(v.g., concessão de HC de ofício para soltura), hipótese em que a urgência é registrada na
anotada.

## 4. Dispositivo

a. Voto: "Ante o exposto, voto no sentido de conhecer [em parte] do recurso e dar-lhe
[parcial] provimento para …" / "… negar-lhe provimento, mantendo …"; HC: conceder, conceder em
parte ou denegar a ordem; não conhecer; julgar prejudicado. Cada alteração de pena traz o
quantum final por crime e réu, o regime, a substituição e as providências (expedição de alvará de
soltura "se por outro motivo não estiver preso", comunicação ao juízo de origem).

b. Objetivo, direto e enxuto: no dispositivo não se justifica, comanda-se.

c. Todos os comandos do dispositivo em um único parágrafo, numerados (1), (2)…; **comandos à Secretaria** em
parágrafo próprio, imediatamente após, aberto por **"À Secretaria,"** em negrito (vírgula,
nunca dois-pontos), simples e sucintos. Não se manda a Secretaria contar prazo nem certificar o
que os autos já mostram: a contagem e a leitura são do gabinete.

c-1. **Deveres regimentais da Secretaria** não precisam de comando, salvo urgência que justifique
reforço: expedição de alvará de soltura no BNMP (RITJAL, art. 319 — em decisão que solta,
admite-se o comando expresso, pela urgência); comunicação da decisão do RESE e do agravo em
execução ao juízo de origem, com cópia do acórdão (arts. 323, § 2º, e 330); inclusão em mesa do
processo com liminar concessiva para referendo (art. 63, § 4º); vista ao Ministério Público no MS
após as informações (art. 199). A vista ao recorrido para contrarrazões nos embargos
infringentes é aberta pela Secretaria (art. 338).

c-2. **Comunicação da ordem de HC é do relator**: a decisão concessiva é comunicada de imediato,
preferencialmente por meio eletrônico, às autoridades que devam cumpri-la, e a comunicação e o
salvo-conduto (no HC preventivo) são **firmados pelo relator** (art. 194, caput e parágrafo único). A
minuta concessiva traz, por isso, a ordem expressa de comunicação imediata — ou a fórmula de que
a decisão servirá como ofício — e, sendo o caso, o salvo-conduto.

d. Decisões e despachos encerram-se em "Publicações e intimações via DJEN", sem "publique-se",
"intime-se" ou "cumpra-se"; votos, em "É como voto."

## 5. Texto e formatação

a. **Texto corrido, sem tópicos na fundamentação**: nada de "I — Da preliminar", "Do mérito",
"Da dosimetria" no interior da peça. A passagem de um tema ao outro faz-se por período de
transição que feche o ponto decidido e anuncie o seguinte. Sem tabelas, caixas de texto ou
hiperlinks: o portão os recusa, porque o conversor para RTF não os leva ao SAJ.

b. **Parágrafos curtos, um por questão** (em regra até cinco ou seis períodos, ~120 palavras),
ligados por transições variadas ("Com efeito", "Nesse passo", "Por outro lado", "Superada essa
questão", "No que toca a", "Desse modo").

c. **Períodos completos**: vedada a frase fragmentada ("Rejeitada a preliminar.", "Passo ao
mérito."); a conclusão vem encadeada ("Desse modo, rejeito a preliminar de nulidade.").

d. **Travessão** só quando a intercalação for essencial; **dois-pontos** só para introduzir
citação literal em parágrafo próprio.

e. **Negrito** apenas: (i) nomes das partes no primeiro parágrafo; (ii) núcleo decisório do
dispositivo; (iii) "À Secretaria"; (iv) a palavra ou o trecho central que identifica o tema
enfrentado na fundamentação ("Quanto à **preliminar de nulidade da busca domiciliar**, …"),
nunca a frase ou o parágrafo inteiro.

f. Sem caixa alta (salvo epígrafes admitidas, ementas e citações que a contenham); itálico só
para estrangeirismos (habeas corpus, in dubio pro reo, reformatio in pejus); citação de até três
linhas entre aspas; com mais de três, parágrafo próprio com recuo de 4 cm, em corpo 11,
espaçamento simples e sem aspas; "n.º" para número (plural "n.ºs").

g. **Sem fecho de local, data e nome**: data e identificação vêm da assinatura digital.

## 6. O que fica fora da minuta

a. **Temas e precedentes qualificados** só quando aplicados ou invocados por parte; a análise de
adequação (sempre feita) fica no ledger e na anotada.

b. **Eventos passados** sem serventia ao julgamento não se analisam.

c. **Linguagem de método** ("leitura integral", "varredura dos autos", "extração de texto",
"OCR", "linha a linha"…) é vedada — afirma-se o resultado, com as fls. O portão distingue o
método do fato do processo: "extração de dados do celular" e "varredura policial no imóvel" são
fatos e não se vedam.

d. **Prazos e preclusões** só quando controvertidos ou conhecidos de ofício (intempestividade do
recurso, por exemplo); exceção fixa: embargos de declaração, tempestividade sempre expressa.

## 7. Destaques em vermelho (só na versão anotada)

Vermelho e negrito (`{{v: …}}` / `{{conferir: …}}` em `montar_minuta.py`) **apenas quando a
resposta não está nos autos**: documento ilegível, mídia não transcrita, evento superveniente
possível (petição pós-conclusão, soltura, óbito), tese não pacificada, divergência entre a linha
adotada e a orientação da Câmara ou do Desembargador, descompasso entre o modelo do gabinete e as
peculiaridades do caso, distinção ou superação de precedente qualificado, fundamento novo que
exija contraditório (item 3.f; RITJAL, art. 161), indício de impedimento ou suspeição (cuja
declaração é do Desembargador), risco de nulidade ou de prescrição. O que se
confere lendo ou calculando não se devolve ao magistrado como pergunta. Parcimônia: se tudo é
destaque, nada é destaque. Campos dependentes de dado não localizado vão entre colchetes e
impedem a versão limpa até serem resolvidos.
