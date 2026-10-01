#!/usr/bin/env python3
"""Extrai o texto do Regimento Interno do TJAL a partir do PDF oficial, separando o vigente do revogado.

O PDF consolidado do Tribunal marca o texto **revogado por tachado** (linha horizontal sobre o
meio da linha de texto) e o texto **incluído por emenda em azul**. A extração em texto puro perde o
tachado e cola hífens de fim de linha ("Procurador(a)-" + "Geral" → "Procurador(a)Geral"). Este
script:

  1. detecta, por geometria, os caracteres tachados (linha horizontal que atravessa a faixa
     central do caractere) e os exclui do texto vigente;
  2. grava o texto revogado à parte, com a página, para consulta histórica;
  3. preserva as quebras de linha do PDF (o `regimento.py` une as linhas e mantém o hífen real
     de fim de linha — no Regimento não há hifenização silábica automática);
  4. remove as marcas de paginação ("Página N").

Uso:
    pip install pdfplumber
    python extrair_regimento.py RITJAL.pdf [--saida ../referencias] [--versao "texto da versão"]
Saída: <saida>/ritjal_integral.txt (vigente) e <saida>/ritjal_revogados.txt; depois, rode
`python gerar_mapa_regimento.py` para regenerar o mapa e reconfira o ledger.
"""
import re
import sys
from datetime import date
from pathlib import Path

PAGINACAO = re.compile(r"^\s*Página(\s+\d+)?\s*$")
SO_NUMERO = re.compile(r"^\s*\d{1,4}\s*$")


def linhas_horizontais(pagina):
    hs = [l for l in pagina.lines if abs(l["top"] - l["bottom"]) < 1.0]
    hs += [r for r in pagina.rects if (r["bottom"] - r["top"]) < 1.5 and (r["x1"] - r["x0"]) > 3]
    return hs


def tachado(ch, horizontais):
    """Caractere atravessado por linha horizontal na faixa central (não é sublinhado)."""
    if ch.get("object_type") != "char":
        return False
    h = ch["bottom"] - ch["top"]
    cx = (ch["x0"] + ch["x1"]) / 2
    for l in horizontais:
        if l["x0"] - 0.5 <= cx <= l["x1"] + 0.5 and ch["top"] + 0.3 * h <= l["top"] <= ch["bottom"] - 0.2 * h:
            return True
    return False


def limpar(texto):
    saida, anterior_pagina = [], False
    for linha in (texto or "").splitlines():
        if PAGINACAO.match(linha):
            anterior_pagina = linha.strip() == "Página"
            continue
        if anterior_pagina and SO_NUMERO.match(linha):
            anterior_pagina = False
            continue
        anterior_pagina = False
        saida.append(linha.rstrip())
    return saida


def extrair(pdf_path):
    import pdfplumber
    vigente, revogado, n_tachados = [], [], 0
    with pdfplumber.open(pdf_path) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            hs = linhas_horizontais(pagina)
            if hs:
                marcados = {id(c) for c in pagina.chars if tachado(c, hs)}
            else:
                marcados = set()
            n_tachados += len(marcados)
            vig = pagina.filter(lambda o: id(o) not in marcados) if marcados else pagina
            vigente += limpar(vig.extract_text(x_tolerance=1.5))
            if marcados:
                rev = pagina.filter(lambda o: o.get("object_type") != "char" or id(o) in marcados)
                trecho = [l for l in limpar(rev.extract_text(x_tolerance=1.5)) if l.strip()]
                if trecho:
                    revogado.append(f"--- página {i} do PDF ---")
                    revogado += trecho
    return vigente, revogado, n_tachados


def main(argv):
    if not argv:
        print(__doc__); return 2
    pdf_path = Path(argv[0])
    saida = Path(argv[argv.index("--saida") + 1]) if "--saida" in argv else \
        Path(__file__).resolve().parent.parent / "referencias"
    versao = argv[argv.index("--versao") + 1] if "--versao" in argv else \
        "Regimento aprovado pelo Pleno em 20/08/2024, com as Emendas n.ºs 17 (19/08/2025), 18 (27/01/2026) e 19 (10/02/2026)"
    vigente, revogado, n = extrair(pdf_path)
    cab = [
        "# REGIMENTO INTERNO DO TRIBUNAL DE JUSTIÇA DO ESTADO DE ALAGOAS — TEXTO VIGENTE PESQUISÁVEL",
        f"# Fonte: {pdf_path.name} (PDF consolidado fornecido pelo gabinete). Versão: {versao}.",
        f"# Extraído em {date.today().isoformat()} por scripts/extrair_regimento.py: o texto TACHADO no PDF",
        "# (revogado) foi EXCLUÍDO e está em ritjal_revogados.txt; o texto em azul no PDF (incluído por",
        "# emenda) está aqui com a respectiva anotação. Quebras de linha do PDF preservadas; marcas de",
        "# paginação removidas. Consulte por artigo com scripts/regimento.py.",
        "",
    ]
    (saida / "ritjal_integral.txt").write_text("\n".join(cab + vigente) + "\n", encoding="utf-8")
    cab_rev = [
        "# REGIMENTO INTERNO DO TJAL — TEXTO REVOGADO (tachado no PDF consolidado)",
        f"# Fonte: {pdf_path.name}. Somente para consulta histórica: NÃO citar como vigente.",
        "",
    ]
    (saida / "ritjal_revogados.txt").write_text("\n".join(cab_rev + revogado) + "\n", encoding="utf-8")
    print(f"Vigente: {len(vigente)} linhas; caracteres tachados excluídos: {n}; "
          f"trechos revogados em {sum(1 for l in revogado if l.startswith('--- página'))} página(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
