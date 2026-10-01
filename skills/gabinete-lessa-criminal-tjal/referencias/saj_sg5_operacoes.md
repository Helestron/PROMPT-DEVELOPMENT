# Operação do SAJ/SG5 — catálogo de operações, roteiros e lições herdadas

Referência da Fase 5 e do Modo C do SKILL.md. O SAJ/SG5 (Segundo Grau) e o SAJ/PG5 (Primeiro
Grau) são da mesma família (Softplan, Delphi/DevExpress). A técnica de automação abaixo foi
**validada no PG5** (23–24/08/2026); os roteiros do SG5 são **receitas a validar** na Rodada de
Descoberta (item 1), com `-Ensaio` antes da primeira execução real de cada roteiro novo.

## 1. Rodada de Descoberta (primeira execução no gabinete, e a cada nova versão do SG5)

Objetivo: substituir todo `null`/`A_CONFIRMAR` de `config/gabinete.json` pelo que o próprio
sistema exibe. Somente leitura — nenhum documento é criado nesta rodada.

1. `saj_sg5.ps1 -Modo Verificar` → confirma o nome do processo (`sajsg5*`; se diferir, a saída
   lista os processos `saj*` ativos) e o caminho do executável.
2. `-Modo Captura` da janela principal (ou `scripts\testar_acesso.ps1` — SKILL.md, Fase 0, item
   0.1) → registre o título, a lotação (gabinete do Des. João Luiz de Azevedo Lessa) e o usuário
   exibidos; grave `gabinete.lotacao_esperada_regex` e `gabinete.usuario_saj`.
3. Filas de trabalho do gabinete: nomes exatos de "conclusos", "em elaboração", "aguardando
   assinatura" e demais filas existentes → `saj_sg5.filas`.
4. Emissão de documentos → "Consulta de Modelos": códigos de **categoria** e de **modelo** de
   despacho, decisão monocrática, relatório, voto, ementa, voto de vogal, voto-vista, voto
   vencido, declaração de voto e voto de referendo → `saj_sg5.categorias` e `saj_sg5.modelos`
   (as chaves são os tipos do portão: `despacho`, `decisao`, `relatorio`, `voto`, `ementa`,
   `voto_vogal`, `voto_vista`, `voto_vencido`, `declaracao_voto` e `referendo`). Prefira sempre
   o código: digitar nome falha por acentuação.
5. Painel de propriedades do documento (F8 no PG5; confirme no SG5): campo *Movimentação* —
   códigos e descrições disponíveis para cada ato → `saj_sg5.movimentacoes_tpu`, conferidos com a
   TPU/CNJ.
6. Grave cada achado no caderno de bordo com a captura correspondente. Só então execute um
   primeiro roteiro com `-Ensaio` e, depois, um real em processo indicado pelo usuário.

## 2. Matriz de operações (aplicada pelo `saj_sg5.ps1 -Operacao` e pelo SKILL.md)

| Nível | Regra | Operações (rótulo para `-Operacao` entre parênteses) |
|---|---|---|
| **A — automático** | executa sem perguntar, dentro do lote | consultar filas e processos (`consultar`); abrir processo e pasta (`abrir_processo`); emitir documento pelo modelo do gabinete (`emitir_documento`); editar (`editar`); colar a versão limpa (`colar_minuta`); salvar (`salvar`); **finalizar sem assinar**, com envio à fila de assinatura do Desembargador (`finalizar_sem_assinar`); mover entre filas internas do gabinete (`mover_fila_interna`); anotar pendência interna (`anotar_pendencia_interna`) |
| **B — com autorização de lote** | exige ordem expressa do usuário no chat, registrada em `autorizacao_nivel_b.json` na pasta de estado (texto literal, operações, processos, validade) | lançar movimentação visível nos autos (`lancar_movimentacao_nos_autos`); remessa ao revisor — RITJAL, art. 325 (`remessa_revisor`); pedido de dia pelo relator ou pelo revisor — arts. 49, II, e 61, XIV (`pedido_dia_julgamento`); vista à Procuradoria-Geral de Justiça — arts. 323, 324, 329, § 3º, e 331, parágrafo único (`vista_pgj`); pedido de inclusão em pauta (`pedido_inclusao_pauta`) e retirada de pauta (`retirada_pauta`); apresentação em mesa de feito que independe de pauta — arts. 61, XV, e 121 (`apresentacao_em_mesa`); devolução de autos após vista — art. 173, caput e § 2º (`devolucao_vista`); baixa para juízo de retratação — art. 326 (`baixa_juizo_retratacao`); encaminhamento à Secretaria (`encaminhar_secretaria`); conversão em diligência — art. 178 (`conversao_diligencia`); transferência interna de tarefa entre servidores do gabinete (`transferir_tarefa_interna`) |
| **C — vedado** | nunca, ainda que o usuário peça | assinar, inclusive o acórdão — arts. 61, XVII, 182 e 184 (`assinar`); assinar e liberar (`assinar_e_liberar`); liberar nos autos (`liberar_nos_autos`); registrar voto em sessão ou em plataforma virtual — art. 152 (`registrar_voto_sessao`); pedir vista em sessão — art. 173 (`pedir_vista_sessao`); declarar suspeição ou impedimento — arts. 20 e 245 (`declarar_suspeicao_impedimento`); excluir documento (`excluir_documento`) ou cancelar documento alheio (`cancelar_documento_alheio`); alterar cadastro de partes (`alterar_cadastro_partes`); redistribuir processo (`redistribuir_processo`); baixar ou arquivar (`baixar_ou_arquivar`); certificar trânsito (`certificar_transito`); digitar senha, PIN ou token (`digitar_credencial`) |

Por que o nível C é intransponível: assinatura, voto em sessão, pedido de vista e declaração de
suspeição ou de impedimento são atos pessoais do magistrado; a assinatura, além disso, é
eletrônica, baseada em certificado digital (Lei n.º 11.419/2006, art. 1º, § 2º, III; RITJAL,
arts. 67 e 184), e depende de credencial que a automação não pode manusear. Exclusão,
cancelamento, alteração de cadastro, redistribuição, baixa e certificação de trânsito produzem
nos autos efeitos que a fila de assinatura não permite revisar. A finalização sem assinatura é a
salvaguarda do desenho: o documento fica na fila do Desembargador, revisável e removível.

Formato da autorização de nível B (gravada por Claude **somente** após a ordem no chat, com o
texto literal da ordem, em `autorizacao_nivel_b.json` na pasta de estado — `GABINETE_TRABALHO`
ou, na falta, a pasta `scripts/`; SKILL.md, Fase 0, item 4):

```json
{"concedida_em": "2026-10-01T10:00:00", "valida_ate": "2026-10-01T23:59:00",
 "texto_literal": "Autorizo a remessa ao revisor da apelação 0700123-83.2024.8.02.0001.",
 "operacoes": ["remessa_revisor"],
 "processos": ["0700123-83.2024.8.02.0001"]}
```

Sem arquivo válido, o script recusa a ação; operação fora da matriz também é recusada até ser
classificada em `config/gabinete.json`. Autorização não se presume, não se estende a outro lote e
não se reutiliza depois de expirada.

## 3. Técnica de automação (validada no PG5)

- Controles Delphi/DevExpress não se expõem à UI Automation (panes sem nome): **clique por
  coordenada guiado por captura** — `-Modo Captura`, ler a imagem, `-Modo CliqueXY`, nova captura
  para **conferir o efeito antes do passo seguinte**.
- Script DPI-aware: captura e clique no mesmo sistema de coordenadas físicas.
- `MainWindowHandle` aponta para uma `TApplication` oculta; a janela real aparece na enumeração
  de janelas visíveis. O editor de textos pode não expor título: opere-o pelo quadro de
  coordenadas da janela principal.
- **Capture imediatamente antes de cada clique**: painéis rolam ao receber foco.
- Menus do editor não confirmam por clique sintético: prefira **atalhos** (`-Modo Teclas`).
  Modais ("Aviso", "Erro") fecham com `{ENTER}` dirigido à própria janela (`-Janela '^Aviso$'`).
- **Entrada ignorada = modal pendente**: rode `-Modo Janelas` para listar as janelas `saj*`
  visíveis e feche o modal pelo seu próprio quadro.
- Não reative a janela entre selecionar e agir (o script só ativa quando o primeiro plano
  pertence a outro processo).
- O bloqueio de termos vedados impede digitar "Assinatura" até em filtros: use outro termo.
- **Nunca `Ctrl+A` nem `Ctrl+M` no editor** (no PG5, Ctrl+A abre "Abrir…"; uma seleção pendente
  somada a `{ENTER}` apagou um documento inteiro). Selecione linha com `{HOME}` + `+{END}`.
  **Nunca `-Substituir`** em `ColarRtf` no editor. Diante de estrago antes de salvar, `^z`.
- Leitura de grades (fila de conclusos, pauta): selecione a grade e use `-Modo CopiarSelecao
  -Saida fila.txt` — somente leitura; o clipboard é limpo ao final.

Salvaguardas do script (não as contorne): identity gate (`-Processo sajsg5*`); kill switch
(`PARAR.txt` ao lado do script ou na pasta de estado, conferido antes de qualquer ação — avise o
usuário de que pode criá-lo a qualquer momento); log de auditoria `saj_log.jsonl` na pasta de
estado (ação, janela, operação, processo, horário); `-Ensaio`; clipboard higienizado; termos
vedados bloqueados, inclusive pelo nome real do controle clicado; matriz A/B/C.

## 4. Roteiros (receitas a validar no SG5; passos herdados do PG5 marcados ★)

### 4.1 Ler a fila de conclusos do gabinete (nível A)
Abrir a fila "conclusos" registrada em `config` → `CopiarSelecao` da grade → extrair número,
classe, data de conclusão, réu preso/prioridade, papel do gabinete (relator/revisor) → montar a
lista do lote (SKILL.md, item 1.2).

### 4.2 Emitir e inserir minuta (nível A) ★
1. "Emissão de Documentos" → categoria e modelo **por código** (`config`), `{TAB}` após cada.
2. Número do processo na máscara: confira quantos dígitos o campo espera (no PG5, treze —
   `NNNNNNN DD AAAA` — com `8.02.FFFF` fixo; digitar 17 empurrava o foro para a caixa seguinte e
   gerava "Processo informado inexistente"). No SG5, registre o comportamento na Descoberta.
3. Tela de pendências e prazos: feche **sem marcar nada** e **sem** "Não mostrar novamente";
   havendo prazo em curso, registre e alerte (decidir com prazo aberto pode ser prematuro).
4. Seleção entre principal e incidente/recurso: decida pelo que a minuta indica (a que autos
   se referem as fls.), registre a escolha e submeta-a à conferência.
5. Editar → aguardar o editor (20–24 s no PG5) → `^{HOME}` → localizar o título do modelo por
   captura → clique → `{HOME}` + `+{END}` → `-Modo ColarRtf` (a versão limpa começa pelo próprio
   título, que assim não se duplica). Conferir início e fim (`^{END}`) por captura.
6. Prazo do ato no painel, quando houver; somente leitura → registrar na lista de trabalho.
7. Movimentação do documento (painel de propriedades): espelhar o dispositivo (item 4.4).
8. Salvar (`^b` no PG5; 16–18 s) e fechar o editor.
9. **Antes de finalizar, conferir o campo de fila/etapa do fluxo**: se a finalização concluir
   etapa do fluxo ou lançar movimentação nos autos (no PG5, "Fila de Trabalho: Em Elaboração"),
   isso é **nível B** — sem autorização, salve, não finalize, registre e informe.
10. Selecionar a linha até o rodapé exibir **"Selecionados 1"** (a caixa marcada não basta) e
    conferir a linha "Partes:" — outros usuários inserem documentos nas mesmas filas.
11. Finalizar pelo **menu de contexto com busca** (`-Direito`, digitar `Finalizar`, `{ENTER}`) →
    botão Finalizar → aguardar "Operação realizada com sucesso" → OK → Fechar. O botão da barra
    de ferramentas não é confiável no PG5. Só registre "finalizado" após a mensagem de sucesso.

### 4.3 Movimentar (nível B, com autorização)

Sequências regimentais típicas do gabinete (cada movimentação, uma operação autorizada):

- **Apelação, como relator**: conclusão → vista à PGJ (art. 324) → relatório → remessa ao revisor
  (art. 325) → o revisor pede dia.
- **Apelação, como revisor**: exame e eventual retificação do relatório → pedido de dia em até
  dez dias (arts. 49 e 50).
- **RESE e agravo em execução**: vista à PGJ → inclusão em pauta / pedido de dia (arts. 323, § 1º,
  e 329, § 4º).
- **HC**: liminar → (concessiva: referendo em mesa na primeira sessão — art. 63, § 4º, a cargo da
  Secretaria) → informações e PGJ (art. 191) → apresentação em mesa (art. 121, VI).
- **Embargos de declaração**: apresentação em mesa na sessão subsequente (art. 334).
- **Vista**: devolução em até dez dias, prorrogáveis por mais dez mediante comunicação ao
  Presidente do órgão julgador (art. 173, caput e § 1º), com o voto-vista escrito juntado (art. 174); o feito é
  reincluído em pauta na sessão seguinte à devolução (art. 173, § 2º).

Em **todas** as chamadas desses roteiros, use `-Operacao <rótulo da matriz> -NumeroProcesso
<número>`, para que a matriz e o log alcancem cada clique. Antes do clique final, captura e
conferência do processo, da operação e do destinatário; depois, captura da confirmação e
registro na lista de trabalho.

### 4.4 Movimentação do ato (TPU)
A movimentação do documento espelha o dispositivo: provimento, provimento em parte, não
provimento, não conhecimento; concessão, concessão parcial ou denegação da ordem; liminar
deferida ou indeferida; decisão proferida; despacho. Use apenas os códigos confirmados na
Descoberta (`saj_sg5.movimentacoes_tpu`); código não confirmado → registre e deixe a conferência ao
gabinete, sem escolher por aproximação.

### 4.5 Consultar pauta e sessão (nível A)
Leitura da pauta da Câmara Criminal e da situação dos processos do gabinete (incluído, adiado,
retirado, pedido de vista, pedido de sustentação oral). Serve ao Modo B (votos a revisar por
sessão) e ao controle de prazos regimentais de vista.

## 5. Limite de tentativas e falhas

Três falhas no mesmo passo: mude de caminho (menu de contexto, atalho, outra tela) ou registre a
falha, informe em uma linha e siga para o próximo processo. **Processo baixado/arquivado**: se o
sistema perguntar se deseja continuar, responda **Não**, não insira, registre e alerte. **Nunca
relate como concluída ação que não ocorreu** — na dúvida, capture, verifique no fluxo e só então
registre.
