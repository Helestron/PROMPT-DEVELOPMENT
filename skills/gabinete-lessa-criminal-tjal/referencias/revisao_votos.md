# Revisão de votos de outros gabinetes (Modo B)

Referência do Modo B do SKILL.md. Serve a duas situações: (i) o gabinete é **vogal** e precisa
decidir se acompanha o relator, acompanha com ressalva, diverge ou pede vista; (ii) o gabinete é
**revisor** (art. 613, I, do CPP) e examina os autos e o relatório do relator antes do pedido de
dia. O produto é sempre interno: a **nota de revisão**; e, quando a posição sugerida o exigir,
a **minuta de voto** do Desembargador (convergente com ressalva, divergente, voto-vista ou
declaração de voto), que segue o fluxo normal das Fases 3 a 5.

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
número CNJ (validado pelo dígito), relator, tipo de peça e sessão. Ordem de trabalho: sessão mais
próxima primeiro; dentro dela, réu preso, HC, prescrição próxima. Lote padrão: até 10 votos,
salvo indicação do usuário. Votos do próprio gabinete são excluídos do Modo B.

## R2. Autos

Os autos do processo são baixados pelo e-SAJ (Fase 1; `referencias/esaj_autos.md`). **Não se
revisa voto sem os autos**: o relatório do relator é objeto de conferência, não fonte.

## R3. Conferência do voto (item 3 do SKILL.md, aplicada ao texto alheio)

1. `python scripts/conferir_citacoes.py <voto> --listar --saida <saida>/_fila_<numero>.json` —
   extrai todas as citações (precedentes, súmulas, temas, dispositivos legais e regimentais).
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
| Ementa | Reflete a tese e o resultado? Segue o padrão adotado pelo Tribunal (conferir a recomendação do CNJ sobre ementas)? |
| Casos gêmeos | Há processo análogo já julgado pela Câmara ou pelo Desembargador com solução diversa? |

## R5. Nota de revisão (produto interno)

`Revisao_<numero>_<relator-abreviado>.docx`, montada com `scripts/montar_minuta.py` e verificada
com `verificar_minuta.py --tipo nota_revisao --versao anotada`. Estrutura fixa, objetiva, sem
retórica:

1. **Identificação**: número, classe, relator, sessão, papel do gabinete (vogal/revisor),
   versão revisada (arquivo e SHA-256 do inventário).
2. **Posição sugerida** (uma linha): acompanhar; acompanhar com ressalva de fundamentação;
   divergir parcialmente; divergir; pedir vista; suscitar questão de ordem (v.g., prescrição).
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

## R6. Minuta de voto do Desembargador (quando a posição não for "acompanhar")

- **Acompanhar com ressalva** → declaração de voto curta, com a ressalva de fundamentação.
- **Divergir (total ou parcialmente)** → voto divergente: adota o relatório do relator (sem
  repeti-lo), delimita o ponto de divergência e o enfrenta com densidade plena, encerrando com
  o dispositivo próprio e "É como voto." (`--tipo voto_vogal` no portão).
- **Pedir vista** → apenas sugestão na nota; o pedido é ato do Desembargador em sessão. Se
  deferida, o voto-vista segue o padrão do voto divergente ou convergente.

Essas minutas passam pela Fase 4 (revisão) e, se o usuário quiser, pela Fase 5 (inserção no
SG5 e finalização sem assinar). **Registrar voto em sessão é nível C** — nunca.

## R7. Chat e controle

No chat, uma linha por voto: número + relator (abreviado) + posição sugerida + situação (nota
pronta / minuta de voto pronta / inserida). Segunda linha só para ponto bloqueante (prescrição,
nulidade, conta errada, citação inexistente). Atualize `_inventario_revisao.json` com
`revisado_em` e o caminho da nota, para que a próxima rodada detecte alterações posteriores.
