# Revisão de votos de outros gabinetes (Modo B)

Referência do Modo B do SKILL.md. Serve a três situações, todas disciplinadas pelo Regimento
Interno do TJAL (`referencias/regimento_tjal.md`):

1. **Revisor** nas demandas criminais com revisão (art. 613, I, do CPP; RITJAL, art. 49): o
   gabinete do Desembargador que se seguir ao relator na ordem decrescente de antiguidade
   **confirma, completa ou retifica o relatório** (art. 49, I), pode **sugerir diligências** ao
   relator (art. 49, III, e parágrafo único) e **pede dia** para julgamento (art. 49, II) — tudo
   em **até dez dias** (art. 50). Pode ser designado na própria sessão e concordar em mesa com o
   relatório (arts. 51 e 159).
2. **Vogal**: o Desembargador vota após o relator e o revisor, na ordem decrescente de
   antiguidade (art. 158). Pode acompanhar, divergir, **declarar em separado os fundamentos do
   voto** (arts. 167, parágrafo único, e 176) ou **pedir vista** (art. 173).
3. **Vencido**: se o Desembargador ficar vencido — inclusive quando chega ao mesmo resultado
   por fundamento determinante diverso (art. 180) —, os fundamentos do voto vencido devem ser
   apresentados por escrito ou em áudio em **72 horas** (art. 179), e integram o acórdão.

O produto é sempre interno: a **nota de revisão**; e, quando a posição sugerida o exigir, a
**minuta** do Desembargador (retificação ou complemento do relatório, declaração de voto, voto
divergente, voto-vista, fundamentos do voto vencido), que segue o fluxo normal das Fases 3 a 5.

**De onde vêm os votos**: o material dos processos incluídos em pauta é remetido aos demais
gabinetes por meio eletrônico, via **intrajus** (RITJAL, art. 123), assim como a cópia do
relatório quando a lei o exigir (art. 73); além disso, a Câmara pode usar pasta ou drive
compartilhado. Leia de onde o material estiver, sempre em modo leitura, e guarde a cópia de
trabalho na pasta própria do gabinete antes de inventariar.

**Calendário**: a Câmara Criminal reúne-se às **quartas-feiras** (art. 128, VI), com pauta
publicada ao menos cinco dias úteis antes (arts. 70 e 120); HC, embargos de declaração julgados
na sessão subsequente, conflitos e questões de ordem independem de pauta (art. 121). Sessões
virtuais seguem o art. 152 e a Resolução do TJAL; nelas, sustentações orais gravadas chegam até
48 horas úteis antes e ficam no sistema de votação (art. 155) — ouça-as antes de fechar a nota.

## R0. Regras da pasta compartilhada

- **Somente leitura.** Nada se grava, move, renomeia, comenta ou apaga na pasta ou no drive
  compartilhado — nem marcação de "lido". A saída vai para `pastas.saida_revisao` (pasta própria
  do gabinete). `scripts/inventario_votos.py` abre os arquivos apenas em modo leitura.
- Arquivos `~$*` e temporários indicam edição em curso: ignore-os e, se o voto principal estiver
  aberto por outro usuário, registre e revise a versão estável.
- Acesso: pasta local ou de rede (`\\servidor\...`), Google Drive para computador ou OneDrive
  sincronizados — leia pelo caminho local. Havendo apenas conector de nuvem (Google Drive),
  use as ferramentas de leitura do conector, sem criar nem alterar arquivos.
- Votos alheios são documentos internos pré-sessão, sob sigilo funcional: não os resuma no chat
  além do necessário, não os envie a serviço externo, use iniciais para partes em segredo.

## R1. Inventário e seleção

```
python scripts/inventario_votos.py "<pasta compartilhada>" --saida "<saida_revisao>/_inventario_revisao.json" --gabinete-proprio "Lessa"
```

O inventário aponta **NOVO**, **ALTERADO** (o relator reescreveu depois da última revisão — a
nota anterior perde validade e a revisão se refaz sobre a diferença) e **INALTERADO**, com
número CNJ (validado pelo dígito), relator, tipo de peça e sessão. Ordem de trabalho: (1) prazos
regimentais correndo contra o gabinete — fundamentos de voto vencido (72 horas, art. 179), voto
de referendo de liminar concessiva na próxima sessão (art. 63, § 4º), vista (dez dias, art. 173),
revisão (dez dias, art. 50); (2) sessão mais próxima; (3) dentro dela, HC, réu preso, prescrição
próxima (arts. 74 e 148). Lote padrão: até 10 votos, salvo indicação do usuário. Votos do
próprio gabinete são excluídos do Modo B.

## R2. Autos

Os autos do processo são baixados pelo e-SAJ (Fase 1; `referencias/esaj_autos.md`). **Não se
revisa voto sem os autos**: o relatório do relator é objeto de conferência, não fonte.

## R3. Conferência do voto (Fase 2-B do SKILL.md, aplicada ao texto alheio)

1. `python scripts/conferir_citacoes.py <voto> --listar --saida <saida>/_fila_<numero>.json` —
   extrai todas as citações (precedentes, súmulas, temas, dispositivos legais e regimentais);
   para os artigos do RITJAL, `python scripts/regimento.py --fila <voto>` traz o texto vigente
   de cada um, pronto para o confronto de pertinência.
2. Verificação de cada uma na fonte oficial, com registro no ledger (Fase 2-B): existência,
   órgão, relator, datas, **pertinência** (o julgado diz o que o voto lhe atribui?), vigência
   (súmula cancelada, tese revista, dispositivo alterado ou revogado — inclusive a redação
   vigente na data do fato para o direito material).
3. `python scripts/conferir_citacoes.py <voto> --ledger <ledger>` — a lista final de citações
   não confirmadas, rejeitadas ou de diploma não identificado entra na nota de revisão.

## R4. Análise independente e confronto

Faça a análise do caso **como se fosse o relator** (roteiro de `referencias/criminal_2grau.md`)
e só então confronte com o voto. Pontos de confronto obrigatórios:

| Eixo | Pergunta |
|---|---|
| Relatório | Narra com fidelidade e com as fls. corretas as razões, contrarrazões, parecer e a sentença? Omite pedido ou tese defensiva? |
| Admissibilidade | Conheceu do que devia e só do que devia? Tempestividade e cabimento conferidos? |
| Ordem pública | Prescrição (rodar `prescricao.py`), nulidade absoluta, ilegalidade flagrante — algo que o voto deixou de reconhecer de ofício em favor do réu? |
| Enfrentamento | Cada tese das razões foi enfrentada (art. 93, IX, da CF; art. 315, § 2º, do CPP)? Monte a matriz tese → resposta do voto. |
| Prova | A valoração corresponde ao que está nas fls.? Depoimento citado diz o que o voto afirma? |
| Dosimetria | Rodar `dosimetria.py` com os critérios do voto: a conta fecha? Há bis in idem, fração sem fundamento, reformatio in pejus (art. 617 do CPP)? |
| Precedentes | Aderência a precedentes vinculantes (art. 927 do CPC, aplicado por analogia — art. 3º do CPP) e à orientação da própria Câmara; distinção ou superação fundamentadas? |
| Dispositivo | Congruente com a fundamentação? Quantum, regime, substituição e providências (prisão, comunicação) coerentes? Efeito extensivo considerado (art. 580)? |
| Ementa | Reflete a tese e o resultado (divergindo, prevalece o voto — RITJAL, art. 185)? Segue o padrão adotado pelo Tribunal (conferir a recomendação do CNJ sobre ementas)? |
| Casos gêmeos | Há processo análogo já julgado pela Câmara ou pelo Desembargador com solução diversa? |

## R5. Nota de revisão (produto interno)

`Revisao_<numero>_<relator-abreviado>.docx`, montada com `scripts/montar_minuta.py` e verificada
com `verificar_minuta.py --tipo nota_revisao --versao anotada`. Estrutura fixa, objetiva, sem
retórica:

1. **Identificação**: número, classe, relator, sessão, papel do gabinete (vogal/revisor),
   versão revisada (arquivo e SHA-256 do inventário).
2. **Posição sugerida** (uma linha): acompanhar; acompanhar com declaração de voto
   (arts. 167, parágrafo único, e 176); divergir parcialmente; divergir; pedir vista (art. 173);
   suscitar questão de ordem (art. 172) ou matéria não debatida pelas partes (art. 161);
   **como revisor**: confirmar o relatório e pedir dia, completar ou retificar o relatório,
   sugerir diligência ao relator (art. 49).
3. **Pontos que sustentam a posição**, numerados, cada um com as fls. dos autos e a referência
   ao parágrafo do voto revisado, separados em: (a) bloqueantes — erro de fato, nulidade,
   prescrição, conta errada, reformatio in pejus, citação inexistente ou impertinente; (b)
   relevantes — tese não enfrentada, fundamentação deficiente, divergência com a orientação da
   Câmara; (c) de forma — redação, fls. trocadas, ementa.
4. **Citações conferidas**: tabela do ledger (verificada / rejeitada / não localizada).
5. **Cálculos**: memória dos scripts de dosimetria e prescrição, quando rodados.
6. **Ressalva** de apoio à decisão e advertência dos vermelhos (inseridas pelo script).

A nota **aponta, não reescreve** o voto alheio; sugestão de redação ao relator, quando útil, vai
como texto entre aspas no ponto respectivo, para eventual encaminhamento pelo Desembargador.

## R6. Minuta do Desembargador (quando a posição não for "acompanhar")

Tipos do portão (`verificar_minuta.py --tipo …`) entre parênteses.

- **Revisor que completa ou retifica o relatório** (`relatorio`): texto do relatório com os
  acréscimos ou correções, com as fls., e o pedido de dia (nível B na Fase 5). Diligência
  sugerida: despacho curto dirigido ao relator, nos termos do art. 49, III; se o relator a
  entender desnecessária, os autos voltam ao revisor, que pode suscitá-la no voto (art. 49,
  parágrafo único).
- **Acompanhar com declaração de voto** (`declaracao_voto`): fundamentos próprios, curtos,
  quando a conclusão converge e as razões divergem (arts. 167, parágrafo único, e 176).
  Atenção: se a divergência for no **fundamento determinante**, o voto é vencido nesse ponto
  (art. 180) e atrai o prazo de 72 horas do art. 179.
- **Divergir (total ou parcialmente)** (`voto_vogal`): adota o relatório do relator (sem
  repeti-lo), delimita o ponto de divergência e o enfrenta com densidade plena, encerrando com
  o dispositivo próprio e "É como voto.". Em matéria criminal, o empate favorece o réu
  (art. 163, IV; no HC, art. 193); havendo dispersão sobre a pena, aplica-se o art. 167, III.
- **Voto-vista** (`voto_vista`): **sempre escrito, ainda que apenas para acompanhar**
  (art. 174), em dez dias prorrogáveis por mais dez mediante comunicação ao Presidente
  (art. 173); o pedido de vista é ato do Desembargador em sessão (nível C). Se, na vista,
  surgir matéria não debatida pelas partes, os autos vão ao relator para a providência do
  art. 161 (§ 5º).
- **Fundamentos do voto vencido** (`voto_vencido`): **72 horas** a partir do julgamento
  (art. 179), integrando o acórdão para todos os fins, inclusive prequestionamento; a
  publicação das conclusões aguarda a juntada (§ 1º). Prioridade máxima do lote.
- **Embargos infringentes**: o voto vencido favorável ao réu delimita os embargos (art. 337,
  parágrafo único); redija-o com essa consciência.

Essas minutas passam pela Fase 4 (revisão) e, se o usuário quiser, pela Fase 5 (inserção no
SG5 e finalização sem assinar). **Registrar voto em sessão e pedir vista são nível C** — nunca.

## R7. Chat e controle

No chat, uma linha por voto: número + relator (abreviado) + posição sugerida + situação (nota
pronta / minuta de voto pronta / inserida). Segunda linha só para ponto bloqueante (prescrição,
nulidade, conta errada, citação inexistente). Atualize `_inventario_revisao.json` com
`revisado_em` e o caminho da nota, para que a próxima rodada detecte alterações posteriores.
