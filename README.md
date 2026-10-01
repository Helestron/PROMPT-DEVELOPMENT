# PROMPT-DEVELOPMENT

Skills e programas de apoio ao trabalho jurisdicional.

## `gabinete-lessa-criminal-tjal`

Skill do **Gabinete do Desembargador João Luiz de Azevedo Lessa — Câmara Criminal do TJAL**
(2º grau), derivada do `lote-minutas-esaj` (8ª Vara Cível de Arapiraca).

- Pacote instalável: [`dist/gabinete-lessa-criminal-tjal.skill`](dist/gabinete-lessa-criminal-tjal.skill)
- Fonte: [`skills/gabinete-lessa-criminal-tjal/`](skills/gabinete-lessa-criminal-tjal/) — comece por `SKILL.md`.

| Modo | Função |
|---|---|
| A — Conclusos | autos no e-SAJ (2º grau e origem) → análise criminal → minutas de despacho, decisão monocrática, relatório, voto e ementa → portões de revisão → inserção e movimentação no SAJ/SG5, finalizando sem assinar |
| B — Revisão de votos | votos de outros gabinetes em pasta/drive compartilhado (somente leitura) → autos → conferência de citações → nota de revisão com posição sugerida → minuta de voto divergente/vista |
| C — Operação no SG5 | qualquer função do sistema dentro da matriz A (automático) / B (autorização de lote) / C (vedado: assinar, liberar, votar em sessão, excluir, credenciais) |

Scripts (`scripts/`): `cnj.py`, `dosimetria.py`, `prescricao.py`, `montar_minuta.py`,
`verificar_minuta.py`, `gerar_versoes.py` (com conversor DOCX→RTF nativo),
`conferir_citacoes.py`, `inventario_votos.py`, `saj_sg5.ps1`.

### Antes do primeiro uso

1. Preencher `config/gabinete.json` pela **Rodada de Descoberta** (`referencias/saj_sg5_operacoes.md`,
   item 1): lotação, usuário, pastas, códigos de categoria/modelo, filas e movimentações do SG5.
   Os roteiros do SG5 derivam da técnica validada no PG5, mas **ainda não foram executados no
   SG5**; rode-os primeiro com `-Ensaio`.
2. Obter o texto oficial vigente do Regimento Interno do TJAL e preencher
   `referencias/regimento_tjal.md` (nenhum artigo regimental foi registrado de memória).
3. Confirmar as rotas do e-SAJ de 2º grau (`cposg5`) e registrá-las em `config.esaj.rotas_validadas`.
4. `pip install python-docx` (Python 3) e PowerShell 5.1 no Windows.

### Testes

```
pip install python-docx pytest
python -m pytest tests
```
