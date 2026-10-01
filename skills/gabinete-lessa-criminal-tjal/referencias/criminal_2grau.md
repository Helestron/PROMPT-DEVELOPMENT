# Roteiro de análise criminal em 2º grau — Câmara Criminal

Referência das Fases 2 e 3 e do Modo B do SKILL.md. **Este arquivo orienta a análise; não
autoriza citação.** Todo dispositivo, súmula, tema ou precedente aqui mencionado é **pista**: só
vai à minuta depois de conferido na fonte oficial e registrado como `VERIFIED` no ledger (Fase
2-B). Leis penais e processuais mudam com frequência (Lei n.º 13.964/2019, Lei n.º 14.843/2024,
Lei n.º 14.994/2024, entre outras): confira sempre a redação vigente no Planalto, e a vigente
**na data do fato** para o direito material (art. 5º, XL, da CF; arts. 2º e 4º do CP).

## 1. Classes, ritos e o que o gabinete produz

| Classe | Base (conferir) | Ato típico do gabinete |
|---|---|---|
| Apelação criminal | arts. 593 a 603 e 609 a 618 do CPP | relatório; voto; ementa; despachos (vista à PGJ, razões na instância — art. 600, § 4º; intimação do réu para constituir defensor) |
| Recurso em sentido estrito | arts. 581 a 592 do CPP | relatório; voto; ementa |
| Agravo em execução | art. 197 da LEP (rito do RESE) | voto; ementa |
| Habeas corpus | art. 5º, LXVIII, da CF; arts. 647 a 667 do CPP | decisão liminar; despacho de informações (art. 662); decisão monocrática de não conhecimento/prejudicialidade, quando o Regimento a admitir; voto; ementa |
| Mandado de segurança criminal | Lei n.º 12.016/2009 | liminar; voto |
| Embargos de declaração | arts. 619 e 620 do CPP | voto (tempestividade sempre expressa) |
| Embargos infringentes e de nulidade | art. 609, parágrafo único, do CPP | voto (limitados à divergência favorável ao réu) |
| Revisão criminal | arts. 621 a 631 do CPP | relatório; voto (competência regimental — conferir) |
| Desaforamento | arts. 427 e 428 do CPP | voto |
| Carta testemunhável | arts. 639 a 646 do CPP | voto |
| Correição parcial, conflito de jurisdição, exceções | Regimento Interno e lei de organização judiciária — conferir | decisão/voto |

**Papel do gabinete em cada processo** — identifique antes de tudo: **relator** (minuta de
relatório, voto, ementa, decisões e despachos); **revisor** (art. 613, I, do CPP, nas apelações
de crimes apenados com reclusão — exame dos autos e do relatório, visto e pedido de dia, conforme
o Regimento); **vogal** (exame do voto do relator para acompanhar, divergir ou pedir vista —
Modo B). A disciplina regimental da revisão e da vista deve ser conferida no RITJAL vigente.

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
   atual da jurisprudência do STF).
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

1. Ato coator e autoridade coatora identificados; competência da Câmara.
2. Cabimento: HC substitutivo de recurso próprio; reiteração de pedido já julgado (verificar
   no e-SAJ os HCs anteriores do mesmo paciente); supressão de instância; pista: Súmula 691/STF.
3. **Liminar**: fumus boni iuris e periculum libertatis em exame perfunctório; indeferida,
   requisitar informações (art. 662 do CPP) e vista à PGJ (prazo do Decreto-Lei n.º 552/1969 —
   conferir).
4. Mérito da prisão preventiva: pressupostos e requisitos (arts. 312 e 313 do CPP);
   fundamentação concreta e contemporânea (art. 312, § 2º; art. 315, § 2º); vedação de
   decretação de ofício (art. 311); revisão nonagesimal (art. 316, parágrafo único — conferir
   alcance segundo o STF); excesso de prazo pela razoabilidade, à luz da complexidade e da
   atuação da defesa; medidas cautelares diversas (art. 319); condições pessoais favoráveis não
   bastam isoladamente; prisão domiciliar (arts. 318 e 318-A).
5. Perda de objeto (soltura, sentença superveniente que reexamina a prisão): prejudicialidade
   declarada com a fls. do fato superveniente.

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

## 8. Segredo e proteção de dados

Crimes contra a dignidade sexual tramitam em segredo de justiça (art. 234-B do CP): no chat e em
qualquer texto fora dos autos, iniciais das partes e da vítima; na minuta, observe o padrão do
gabinete para vítimas (iniciais) e menores (Lei n.º 8.069/1990). Votos de outros gabinetes são
documentos internos pré-sessão: não saem do ambiente do gabinete.
