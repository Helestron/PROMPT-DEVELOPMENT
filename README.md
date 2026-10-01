# PROMPT-DEVELOPMENT

Skills e programas de apoio ao trabalho jurisdicional.

## `gabinete-lessa-criminal-tjal`

Skill do **Gabinete do Desembargador João Luiz de Azevedo Lessa — Câmara Criminal do TJAL**
(2º grau), derivado do `lote-minutas-esaj` (8ª Vara Cível de Arapiraca).

- Pacote instalável: [`dist/gabinete-lessa-criminal-tjal.skill`](dist/gabinete-lessa-criminal-tjal.skill)
- Fonte: [`skills/gabinete-lessa-criminal-tjal/`](skills/gabinete-lessa-criminal-tjal/) — comece por `SKILL.md`.

| Modo | Função |
|---|---|
| A — Conclusos | autos no e-SAJ (2º grau e origem) → análise criminal integral → conferência de jurisprudência, lei e Regimento → minutas de despacho, decisão monocrática (inclusive liminar), relatório, voto, voto de referendo de liminar e ementa → portões de revisão → inserção no SAJ/SG5, finalizando sem assinar, e movimentação autorizada |
| B — Revisão de votos | votos de outros gabinetes para a sessão (pasta ou drive compartilhado e material de pauta recebido via intrajus; somente leitura) → autos → conferência de citações → nota de revisão com posição sugerida → minuta de voto divergente, voto-vista, voto vencido ou declaração de voto, quando o Desembargador a pedir |
| C — Operação no SG5 | qualquer função do sistema dentro da matriz A (automático) / B (autorização de lote) / C (vedado: assinar, liberar nos autos, registrar voto ou pedir vista em sessão, excluir, redistribuir, digitar credenciais) |

Scripts (`scripts/`): `cnj.py`, `dosimetria.py`, `prescricao.py`, `montar_minuta.py`,
`verificar_minuta.py`, `gerar_versoes.py` (com conversor DOCX→RTF nativo),
`conferir_citacoes.py`, `inventario_votos.py`, `regimento.py`, `extrair_regimento.py`,
`gerar_mapa_regimento.py`, `saj_sg5.ps1` e `testar_acesso.ps1`.

### Antes do primeiro uso

1. Preencher `config/gabinete.json`: as pastas (trabalho, modelos do gabinete, votos
   compartilhados e saída da revisão), informadas pelo gabinete; e, pela **Rodada de
   Descoberta** (`referencias/saj_sg5_operacoes.md`, item 1), lotação, usuário, códigos de
   categoria e de modelo, filas e movimentações do SG5. Os roteiros do SG5 derivam da técnica
   validada no PG5, mas **ainda não foram executados no SG5**; rode-os primeiro com `-Ensaio`.
2. **Teste de acesso**, somente leitura (`SKILL.md`, Fase 0, item 0.1), na máquina do gabinete:
   e-SAJ de 2º grau pelo Chrome e SG5 por `scripts\testar_acesso.ps1`.
3. e-SAJ de 2º grau: a entrada é `https://www2.tjal.jus.br/cposg5/open.do?gateway=true`; na
   primeira execução, registrar em `esaj.rotas_validadas` a URL de pesquisa e o link da pasta
   digital obtidos a partir dela.
4. Python 3 com `pip install python-docx pdfplumber` (o `pdfplumber` serve à reextração do
   Regimento e à leitura de PDF quando faltar o `pdftotext`) e PowerShell 5.1 no Windows. Se a
   pasta `scripts/` for somente leitura, defina `GABINETE_TRABALHO` com a pasta de trabalho do
   gabinete (log, autorização de nível B e `PARAR.txt`).

### Regimento Interno do TJAL

Incluído o PDF consolidado (`referencias/ritjal_consolidado_emenda19.pdf` — aprovado em
20/08/2024, com as Emendas n.ºs 17/2025, 18/2026 e 19/2026) e o texto extraído dele:
`referencias/ritjal_integral.txt` traz **somente o texto vigente**; o texto revogado, que o PDF
marca por tachado, fica em `referencias/ritjal_revogados.txt`, para consulta histórica. Mapa de
uso em `referencias/regimento_tjal.md`.

Consulta: `python scripts/regimento.py 63` (texto vigente), `--buscar "termo"`,
`--fila minuta.docx` e `--revogados`. Nova emenda: `python scripts/extrair_regimento.py <PDF
consolidado>` e, em seguida, `python scripts/gerar_mapa_regimento.py`.

### Testes

```
pip install python-docx pytest pdfplumber
python -m pytest tests
```
