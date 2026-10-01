# Roteiro de análise criminal em 2º grau — Câmara Criminal

Referência das Fases 2 e 3 e do Modo B do SKILL.md. **Este arquivo orienta a análise; não
autoriza citação.** Todo dispositivo, súmula, tema ou precedente aqui mencionado é **pista**: só
vai à minuta depois de conferido na fonte oficial e registrado como `VERIFIED` no ledger (Fase
2-B). Leis penais e processuais mudam com frequência (Lei n.º 13.964/2019, Lei n.º 14.843/2024,
Lei n.º 14.994/2024, entre outras): confira sempre a redação vigente no Planalto, e a vigente
**na data do fato** para o direito material (art. 5º, XL, da CF; arts. 2º e 4º do CP).

## 1. Classes, ritos, competência regimental e o que o gabinete produz

Base legal (pista a conferir) e base regimental (texto vigente em `referencias/ritjal_integral.txt`;
mapa em `referencias/regimento_tjal.md`; consulta com `python scripts/regimento.py <artigo>`).

| Classe | Lei (conferir) | RITJAL | Órgão | Ato típico do gabinete |
|---|---|---|---|---|
| Apelação criminal | arts. 593 a 603 e 609 a 618 do CPP | arts. 48, II; 324 a 327; 49 e 50 (revisor) | Câmara Criminal | despacho de vista à PGJ (art. 324); relatório e remessa ao revisor (art. 325); voto; ementa; não conhecida e processada como RESE → baixa para retratação em dez dias (art. 326) |
| Recurso em sentido estrito | arts. 581 a 592 do CPP | arts. 321 a 323; 149 (julgado antes das apelações) | Câmara Criminal (salvo lista de jurados: Presidente) | despacho de vista à PGJ e inclusão em pauta (art. 323); voto; ementa; conferir sequencial (art. 322; CGJ/AL, arts. 797 e 798) |
| Agravo em execução | art. 197 da LEP | arts. 328 a 330 (prazo de cinco dias; rito do RESE; sem efeito suspensivo, salvo desinternação) | Câmara Criminal | vista à PGJ e pedido de dia (art. 329, §§ 3º e 4º); voto |
| Habeas corpus | art. 5º, LXVIII, da CF; arts. 647 a 667 do CPP | arts. 48, III; 189 a 195; 63, §§ 3º a 5º (referendo); 121, VI (independe de pauta); 43, IX, f (Pleno, conforme o paciente) | Câmara Criminal ou Pleno | decisão liminar; **voto de referendo** se concessiva; despacho de informações e vista à PGJ (dois dias — art. 191); indeferimento liminar (art. 192, parágrafo único); prejudicialidade (art. 192); voto; ementa |
| Mandado de segurança criminal | Lei n.º 12.016/2009 | arts. 114; 196 a 199 | Câmara Criminal | liminar (art. 196); voto |
| Embargos de declaração | arts. 619 e 620 do CPP | arts. 333 a 336; 109; 121, V | relator do acórdão | voto (em mesa, sem revisão — art. 334); decisão monocrática se opostos contra decisão monocrática (art. 335); tempestividade sempre expressa |
| Embargos infringentes e de nulidade | art. 609, parágrafo único, do CPP | arts. 337 a 339; 111; 164; 43, IX, m | admissibilidade: relator do acórdão embargado; julgamento: Pleno, com novo relator da Câmara Criminal | decisão de admissibilidade (art. 338); voto (limitado à divergência — art. 337, parágrafo único) |
| Revisão criminal | arts. 621 a 631 do CPP | arts. 43, IX, l; 112; 215 a 219 | Pleno | relatório; despacho sobre provas (art. 217); voto — vedada a relatoria e a revisão a quem relatou ou revisou o acórdão atacado (art. 112) |
| Desaforamento | arts. 427 e 428 do CPP | arts. 48, VI; 220 a 222 | Câmara Criminal (preferência) | despacho de informações (dez dias) e vista à PGJ (cinco dias); voto |
| Carta testemunhável | arts. 639 a 646 do CPP | arts. 331 e 332 | Câmara Criminal | vista à PGJ; voto (pode julgar o mérito do recurso se instruída — art. 332) |
| Correição parcial | — | arts. 241 a 243 | Câmara Criminal (matéria criminal) | liminar (art. 243); voto |
| Conflito de competência criminal (1º grau) | arts. 113 a 117 do CPP | arts. 48, VIII; 121, I; 227 a 231 | Câmara Criminal | voto (independe de pauta) |
| Recursos infracionais (ECA) | Lei n.º 8.069/1990 | art. 48, VII | Câmara Criminal | voto |
| Ação penal originária | Lei n.º 8.038/1990 (conferir) | arts. 204 a 214 | conforme Constituição Estadual e Lei n.º 6.564/2005 (conferir) | atos de instrução; relatório; extinção da punibilidade monocrática após a PGJ (art. 213) |

**Papel do gabinete em cada processo** — identifique antes de tudo:

- **Relator**: dirige o processo e profere os atos (art. 61); decide monocraticamente nas
  hipóteses do art. 62 (recurso prejudicado; desprovimento de recurso contrário a súmula do STF,
  do STJ ou do TJAL, a repetitivo, a IRDR ou a IAC; nas originárias, só extinção sem mérito ou
  previsão legal — parágrafo único); julga desistências e deserções (art. 61, VIII); concede
  fiança (art. 61, XII); pede dia (art. 61, XIV); lavra e assina o acórdão (arts. 61, XVII, e
  182), em até dez dias do encerramento da sessão (art. 182, § 3º).
- **Revisor** (apelação e demais demandas criminais com revisão): o Desembargador que se seguir
  ao relator na ordem decrescente de antiguidade (art. 49) — confirma, completa ou retifica o
  relatório, sugere diligências e pede dia, em até dez dias (arts. 49 e 50); pode ser designado
  na própria sessão (arts. 51 e 159). Embargos de declaração não têm revisão (art. 334).
- **Vogal**: examina o voto do relator para acompanhar, divergir, declarar voto (art. 176) ou
  pedir vista (arts. 173 e 174) — Modo B.

**Atenção à competência do Pleno**: revisão criminal (art. 43, IX, l), embargos infringentes
contra decisões da Câmara Criminal (art. 43, IX, m) e HC cujo paciente esteja entre as
autoridades do art. 43, IX, f. Nesses feitos, o voto é proferido no Pleno; ajuste o cabeçalho e o
modelo do SG5.

## 2. Ordem lógica da análise (relator)

1. **Urgência**: réu preso (e há quanto tempo), liminar pendente em HC, prescrição próxima
   (`scripts/prescricao.py`), prioridade legal (idoso, vítima vulnerável), metas do CNJ.
2. **Admissibilidade**: cabimento, adequação, tempestividade (interposição e razões),
   legitimidade, interesse, regularidade formal; no HC, adequação da via (HC substitutivo,
   supressão de instância, indeferimento de liminar na origem).
3. **Matérias de ordem pública, de ofício e em favor do réu**: prescrição e demais causas
   extintivas da punibilidade (art. 61 do CPP); nulidades absolutas; incompetência absoluta;
   ilegalidade flagrante (concessão de HC de ofício — art. 654, § 2º, do CPP); abolitio
   criminis e lei posterior mais benéfica; ANPP em processos sem trânsito (conferir o estado
   atual da jurisprudência do STF). Matéria que as partes não tiveram oportunidade de debater,
   ainda que cognoscível de ofício, atrai o art. 161 do RITJAL (suspensão e manifestação em
   cinco dias): marque-a em vermelho na anotada e indique o caminho — despacho prévio de
   manifestação ou suscitação na sessão.
4. **Preliminares** arguidas, uma a uma (art. 563 do CPP: sem prejuízo, não há nulidade;
   arts. 564, 571 e 572: momento e preclusão das relativas).
5. **Mérito**: materialidade; autoria; tipicidade (objetiva e subjetiva); ilicitude;
   culpabilidade; desclassificação; concurso de crimes; valoração da prova com fls. —
   depoimentos policiais em cotejo com o restante da prova, reconhecimento pessoal (art. 226 do
   CPP), cadeia de custódia (arts. 158-A a 158-F do CPP), confissão extrajudicial retratada,
   palavra da vítima em crimes clandestinos, prova emprestada, prova ilícita e derivada
   (art. 157 do CPP).
6. **Dosimetria** (item 3) — revista inteira quando impugnada; na apelação exclusiva da defesa,
   a revisão pode manter ou reduzir, **nunca agravar** (art. 617 do CPP; vedada também a
   reformatio in pejus indireta).
7. **Consectários**: regime (art. 33 do CP; detração — art. 387, § 2º, do CPP); substituição
   (art. 44) e sursis (art. 77); multa; reparação mínima (art. 387, IV, do CPP — exige pedido e
   contraditório, conferir orientação do STJ); efeitos da condenação (arts. 91 e 92 do CP;
   perdimento de bens na Lei n.º 11.343/2006); prisão preventiva e direito de recorrer em
   liberdade (art. 387, § 1º, do CPP); honorários de defensor dativo, quando houver.
8. **Efeito extensivo** a corréu não recorrente em situação idêntica (art. 580 do CPP).
9. **Dispositivo** congruente: conhecimento (total/parcial), provimento (total/parcial/não),
   cada alteração de pena com o quantum final, regime e providências.

## 3. Dosimetria — conferência obrigatória por script

Para cada réu e cada crime, preencha o JSON de `scripts/dosimetria.py` com os critérios **que a
sentença ou o voto declararam** e rode o script: a conta deve fechar. Pontos de controle:

- **1ª fase (art. 59)**: cada circunstância desfavorável com fundamento concreto, não inerente ao
  tipo; vedado usar inquéritos e ações em curso para exasperar (pista: Súmula 444/STJ); vedado
  bis in idem (mesmo fato na 1ª e na 2ª fase, ou circunstância que qualifica o crime); fração
  declarada e coerente (1/8 do intervalo, 1/6 da mínima ou outra fundamentada).
- **2ª fase**: agravantes e atenuantes; compensação reincidência × confissão (conferir a
  orientação vigente do STJ); confissão usada para condenar atrai a atenuante (pista: Súmula
  545/STJ; no tráfico, pista: Súmula 630/STJ); limite do mínimo legal (pista: Súmula 231/STJ —
  conferir vigência e eventual revisão).
- **3ª fase**: causas de aumento e de diminuição em cascata; concurso de majorantes da parte
  especial (art. 68, parágrafo único, do CP); fração de majorantes com fundamentação concreta e
  não pelo simples número delas (pista: Súmula 443/STJ); tráfico privilegiado (art. 33, § 4º, da
  Lei n.º 11.343/2006 — requisitos e vedações; pista: Tema 1.139/STJ sobre ações penais em curso).
- **Multa** proporcional à privativa (arts. 49 e 60 do CP).
- **Regime e substituição**: o script devolve o quadro legal (art. 33, § 2º; art. 44); o
  regime mais gravoso que o quantum permitir exige fundamentação concreta (pistas: Súmulas
  440/STJ, 718 e 719/STF; reincidente com pena até 4 anos — pista: Súmula 269/STJ).
- **Concurso de crimes** (arts. 69, 70 e 71 do CP): rode o script por crime e some/exaspere à
  parte, registrando no ledger de cálculos.

## 4. Prescrição — conferência obrigatória por script

Em todo processo, rode `scripts/prescricao.py` com a pena em abstrato e, havendo condenação com
trânsito para a acusação (ou improvimento do seu recurso), com a pena em concreto de **cada
crime isoladamente** (art. 119 do CP; sem o acréscimo da continuidade — pista: Súmula 497/STF).
Marcos interruptivos (art. 117 do CP), redução etária (art. 115), causas suspensivas (art. 116
do CP; art. 366 do CPP) e a vedação de termo inicial anterior à denúncia para fatos posteriores à
Lei n.º 12.234/2010 (art. 110, § 1º) são juízos do julgador; o script os aplica conforme o JSON.
Acórdão confirmatório da condenação como marco interruptivo: conferir a orientação vigente do
STF e do STJ. Prescrição consumada → a minuta a reconhece de ofício, antes do mérito.

## 5. Habeas corpus — roteiro específico

1. Ato coator e autoridade coatora identificados; **competência** — Câmara Criminal (art. 48,
   III) ou Pleno, conforme o paciente (art. 43, IX, f); prevenção (arts. 95 e 103).
2. **Indeferimento liminar** (art. 192, parágrafo único): pedido manifestamente incabível,
   incompetência manifesta do Tribunal ou reiteração de outro com os mesmos fundamentos —
   verifique no e-SAJ os HCs anteriores do mesmo paciente. Demais hipóteses de cabimento (HC
   substitutivo, supressão de instância; pista: Súmula 691/STF) são enfrentadas com fundamento.
3. **Liminar** (art. 189, III): fumus boni iuris e periculum libertatis em exame perfunctório.
   - **Concessiva** → produz efeitos imediatos (art. 63, § 2º), mas vai a **referendo** do
     colegiado: a Secretaria inclui o processo em mesa, independentemente de pauta, na primeira
     sessão subsequente à assinatura, sob pena de decaimento (art. 63, §§ 3º e 4º); não
     referendada, cessam os efeitos e restabelece-se o ato impugnado (§ 5º). **Minute junto a
     decisão e o voto de referendo** (tipo `referendo`), registre na lista de trabalho a sessão
     prevista e alerte o usuário.
   - Comunicação imediata da concessão às autoridades (art. 194) e alvará de soltura no BNMP
     pela Secretaria (art. 319); fiança, se for o caso, processada pelo relator (art. 195).
   - Contra a decisão liminar cabe agravo em quinze dias (art. 190).
4. Instrução: informações da autoridade coatora (art. 662 do CPP) e parecer da PGJ em dois dias
   (art. 191); o relator pode nomear advogado ao impetrante leigo e interrogar o paciente
   (art. 189, I e II).
5. Mérito da prisão preventiva: pressupostos e requisitos (arts. 312 e 313 do CPP);
   fundamentação concreta e contemporânea (art. 312, § 2º; art. 315, § 2º); vedação de
   decretação de ofício (art. 311); revisão nonagesimal (art. 316, parágrafo único — conferir
   alcance segundo o STF); excesso de prazo pela razoabilidade, à luz da complexidade e da
   atuação da defesa; medidas cautelares diversas (art. 319); condições pessoais favoráveis não
   bastam isoladamente; prisão domiciliar (arts. 318 e 318-A).
6. **Prejudicialidade**: cessada a coação, o HC é julgado prejudicado, podendo o Tribunal
   declarar a ilegalidade (art. 192, caput); fato superveniente com fls.
7. Julgamento: independe de pauta, salvo requerimento de inclusão (art. 121, VI); prioridade
   (art. 148, I); empate favorece o paciente (art. 193); assistente de acusação não sustenta
   oralmente (art. 156, § 5º).

## 6. Nulidades frequentes em 2º grau (pistas para a verificação)

Deficiência ou ausência de defesa (pista: Súmula 523/STF); renúncia do único defensor sem
intimação do réu para constituir outro (pista: Súmula 708/STF); nulidade não arguida no recurso
da acusação não se reconhece contra o réu (pista: Súmula 160/STF); efeito devolutivo da apelação
contra decisões do júri adstrito aos fundamentos da interposição (pista: Súmula 713/STF);
busca domiciliar sem fundadas razões (pistas: Tema 280/STF; HC 598.051/SP, STJ); reconhecimento
pessoal sem as formalidades do art. 226 do CPP (pista: HC 598.886/SC, STJ); quebra da cadeia de
custódia; interceptação e dados telemáticos sem autorização; inversão da ordem do interrogatório
(art. 400 do CPP); citação por edital sem esgotamento; ausência de intimação pessoal do
defensor público ou dativo (art. 370, § 4º, do CPP).

## 7. Tribunal do júri em grau de recurso

Apelação limitada às hipóteses do art. 593, III, do CPP; decisão manifestamente contrária à prova
dos autos admite um único novo júri pelo mesmo motivo (art. 593, § 3º); soberania dos veredictos
(art. 5º, XXXVIII, c, da CF); quesito absolutório genérico e clemência (conferir orientação
vigente do STF); execução imediata da condenação pelo júri (pista: Tema 1.068/STF — conferir tese
e alcance).

## 8. Prazos e marcos regimentais que o gabinete controla

| Evento | Prazo / regra | RITJAL |
|---|---|---|
| Revisor examinar e pedir dia | até dez dias | arts. 49 e 50 |
| Pauta publicada antes da sessão | cinco dias úteis, no mínimo | arts. 70 e 120 |
| Sessão ordinária da Câmara Criminal | quartas-feiras | art. 128, VI |
| Referendo de decisão concessiva | primeira sessão subsequente à assinatura, sob pena de decaimento | art. 63, §§ 3º a 5º |
| Parecer da PGJ no HC | dois dias | art. 191 |
| Agravo contra liminar em HC | quinze dias | art. 190 |
| Agravo contra indeferimento liminar de embargos de declaração | cinco dias | art. 334, parágrafo único |
| Embargos infringentes e de nulidade | dez dias; contrarrazões em dez dias | arts. 337 e 338 |
| Agravo em execução | cinco dias | art. 328 |
| Pedido de vista | dez dias, prorrogáveis por mais dez; voto-vista sempre escrito | arts. 173 e 174 |
| Fundamentos do voto vencido | 72 horas | art. 179 |
| Assinatura do acórdão pelo relator | dez dias do encerramento da sessão | art. 182, § 3º |
| Matéria nova não submetida às partes | suspensão e manifestação em cinco dias | art. 161 |
| Apelação processada como RESE | retratação no 1º grau em dez dias | art. 326 |
| Desaforamento | informações em dez dias; PGJ em cinco dias | arts. 220 e 221 |
| Arguição de suspeição do relator | quinze dias da publicação da distribuição | art. 246 |

Prioridades: demandas criminais e, entre elas, réus presos; idosos e doentes graves; HC e MS
(art. 74); na sessão, HC, causas criminais de réus presos, conflitos e MS (art. 148), e RESE
antes das apelações (art. 149).

## 9. Segredo e proteção de dados

Crimes contra a dignidade sexual tramitam em segredo de justiça (art. 234-B do CP): no chat e em
qualquer texto fora dos autos, iniciais das partes e da vítima; na minuta, observe o padrão do
gabinete para vítimas (iniciais) e menores (Lei n.º 8.069/1990). Votos de outros gabinetes são
documentos internos pré-sessão: não saem do ambiente do gabinete.
