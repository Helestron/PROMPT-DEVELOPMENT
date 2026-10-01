#!/usr/bin/env python3
"""Numeração única CNJ (Resolução CNJ n.º 65/2008) — validação e normalização.

Formato: NNNNNNN-DD.AAAA.J.TR.OOOO (J = 8, Justiça Estadual; TR = 02, TJAL).
Dígito verificador: módulo 97 (ISO 7064), calculado sobre NNNNNNN AAAA J TR OOOO 00.

Uso:
    python cnj.py 0700123-45.2024.8.02.0001 [...]
    python cnj.py --completar 0700123-45.2024 --foro 0001
Saída: uma linha JSON por número (valido, normalizado, sequencial, ano, foro, origem_2grau).
"""
import json
import re
import sys

PADRAO = re.compile(r"(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})")
PADRAO_TEXTO = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")


def digito(seq: str, ano: str, j: str, tr: str, foro: str) -> str:
    base = int(f"{seq}{ano}{j}{tr}{foro}00")
    return f"{98 - (base % 97):02d}"


def analisar(numero: str) -> dict:
    m = PADRAO.fullmatch(numero.strip())
    if not m:
        return {"entrada": numero, "valido": False, "motivo": "formato inválido"}
    seq, dd, ano, j, tr, foro = m.groups()
    esperado = digito(seq, ano, j, tr, foro)
    norm = f"{seq}-{dd}.{ano}.{j}.{tr}.{foro}"
    r = {
        "entrada": numero,
        "normalizado": norm,
        "treze_digitos": f"{seq}{dd}{ano}",
        "sequencial": seq,
        "digito": dd,
        "ano": ano,
        "segmento": j,
        "tribunal": tr,
        "foro": foro,
        # Foro 0000 = feito originário do Tribunal (HC, MS, revisão criminal etc.);
        # foro diverso = recurso que conserva o número da ação de origem.
        "originario_2grau": foro == "0000",
        "valido": dd == esperado and j == "8" and tr == "02",
    }
    if dd != esperado:
        r["motivo"] = f"dígito verificador não confere (esperado {esperado})"
    elif j != "8" or tr != "02":
        r["motivo"] = "não pertence ao TJAL (J.TR deveria ser 8.02)"
    return r


def completar(abreviado: str, foro: str) -> str:
    m = re.fullmatch(r"(\d{7})-?(\d{2})\.?(\d{4})", abreviado.strip())
    if not m:
        raise ValueError(f"forma abreviada inválida: {abreviado}")
    return f"{m.group(1)}-{m.group(2)}.{m.group(3)}.8.02.{foro}"


def extrair(texto: str) -> list:
    """Números CNJ distintos do TJAL encontrados no texto, na ordem de ocorrência."""
    vistos = []
    for n in PADRAO_TEXTO.findall(texto):
        if n not in vistos:
            vistos.append(n)
    return vistos


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--completar":
        foro = argv[argv.index("--foro") + 1] if "--foro" in argv else "0000"
        print(json.dumps(analisar(completar(argv[1], foro)), ensure_ascii=False))
        return 0
    falhou = False
    for n in argv:
        r = analisar(n)
        falhou |= not r["valido"]
        print(json.dumps(r, ensure_ascii=False))
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
