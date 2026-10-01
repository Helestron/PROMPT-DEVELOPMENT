#!/usr/bin/env python3
"""Conferência de citações: jurisprudência, súmulas, temas, dispositivos legais e regimentais.

Extrai de uma minuta (ou de voto de outro gabinete) todas as citações e as confronta com o
ledger de verificações (_verificacoes.json). Citação sem entrada VERIFIED é pendência
bloqueante; citação de entrada REJECTED também.

Uso:
    python conferir_citacoes.py arquivo.(docx|rtf|odt|doc|pdf|txt) --ledger _verificacoes.json
    python conferir_citacoes.py arquivo --listar [--saida fila.json]
        (--listar: só extrai e gera a fila de verificação, com entradas PENDENTE no esquema
         do ledger — usado na revisão de votos de outros gabinetes e na Fase 2-B)

Esquema de cada entrada do ledger:
    {"id": "V001", "tipo": "precedente|sumula|tema|dispositivo|regimento|doutrina",
     "chave": "AgRg no HC 598.051/SP" | "Súmula 231/STJ" | "Tema 1.139/STJ" | "art. 33 da Lei n.º 11.343/2006",
     "orgao": "STJ, Sexta Turma", "relator": "...", "julgamento": "AAAA-MM-DD", "publicacao": "...",
     "fonte": "URL oficial ou JusBrasil (inteiro teor)", "trecho_literal": "...",
     "redacao_vigente_conferida_em": "AAAA-MM-DD" (dispositivos e regimento),
     "status": "VERIFIED|REJECTED|PENDENTE", "observacao": "..."}
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PREC = re.compile(
    r"\b((?:(?:AgRg|AgInt|EDcl|EAREsp|ED)\s+n[oa]s?\s+(?:(?:AgRg|EDcl)\s+n[oa]s?\s+)?)?"
    r"(?:HC|RHC|REsp|AREsp|EREsp|RE|ARE|ADI|ADC|ADPF|Rcl|RMS|MS|AP|Inq|CC|RvCr))"
    r"\s*(?:n\.?\s*º?\s*)?(\d{1,3}(?:\.\d{3})+|\d{2,7})(?:\s*/\s*([A-Z]{2}))?")
SUM = re.compile(
    r"\bS[úu]mula\s+(Vinculante\s+)?(?:n\.?\s*º?\s*)?(\d{1,4})(?:\s*(?:/|d[oa])\s*(STF|STJ|TJAL|TFR))?", re.I)
SUM_ENUNC = re.compile(r"\benunciado\s+(?:n\.?\s*º?\s*)?(\d{1,4})\s+da\s+S[úu]mula\s+(Vinculante\s+)?d[oa]\s+(STF|STJ|TJAL)", re.I)
TEMA = re.compile(r"\bTema\s+(?:n\.?\s*º?\s*)?(\d{1,2}\.?\d{3}|\d{1,4})(?:\s*(?:/|d[oa])\s*(STF|STJ))?", re.I)
DIPLOMAS = [
    (r"C[óo]digo\s+de\s+Processo\s+Penal|CPP", "CPP"),
    (r"C[óo]digo\s+de\s+Processo\s+Civil|CPC", "CPC"),
    (r"C[óo]digo\s+Penal(?!\s+Militar)|CP(?![A-Z])", "CP"),
    (r"Constitui[çc][ãa]o(?:\s+Federal|\s+da\s+Rep[úu]blica)?|CF(?:/88)?|CRFB", "CF"),
    (r"Lei\s+de\s+Execu[çc][ãa]o\s+Penal|LEP", "LEP"),
    # Regimentos dos tribunais superiores antes do genérico "Regimento", que designa o RITJAL
    # ("Regimento Interno deste Tribunal", "deste Regimento", "RITJAL").
    (r"Regimento\s+Interno\s+do\s+(?:STJ|Superior\s+Tribunal\s+de\s+Justi[çc]a)|RISTJ", "RISTJ"),
    (r"Regimento\s+Interno\s+do\s+(?:STF|Supremo\s+Tribunal\s+Federal)|RISTF", "RISTF"),
    (r"RITJAL|Regimento(?:\s+Interno)?", "RITJAL"),
    (r"Lei\s+(?:Complementar\s+)?n\.?\s*º?\s*([\d\.]+)\s*/\s*(\d{2,4})", "LEI"),
    (r"Decreto-Lei\s+n\.?\s*º?\s*([\d\.]+)\s*/\s*(\d{2,4})", "DL"),
    (r"Resolu[çc][ãa]o\s+(CNJ|TJAL)\s+n\.?\s*º?\s*([\d\.]+)\s*/\s*(\d{4})", "RES"),
]
NUMS = r"\d+(?:\.\d{3})*(?:-[A-Z])?"
ART = re.compile(rf"\barts?\.\s*({NUMS}(?:\s*(?:,|e|a)\s*{NUMS})*)(.{{0,90}}?)\b(?:d[oa]s?|dest[ea])\s+", re.S)


def texto_de(arq: Path) -> str:
    suf = arq.suffix.lower()
    if suf == ".txt":
        return arq.read_text(encoding="utf-8", errors="replace")
    if suf == ".docx":
        # Runs em vermelho são apontamentos internos da versão anotada (ressalva, conferências)
        # e não integram o texto que irá aos autos: ficam fora da conferência.
        from docx import Document

        def vermelho(r):
            c = r.font.color
            return c is not None and c.type is not None and c.rgb is not None and str(c.rgb).upper() == "FF0000"
        return "\n".join("".join(r.text for r in p.runs if not vermelho(r)) for p in Document(arq).paragraphs)
    if suf == ".pdf":
        return subprocess.run(["pdftotext", "-layout", str(arq), "-"], capture_output=True, text=True).stdout
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError(f"Sem conversor para {suf}: instale LibreOffice ou converta para .docx")
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([soffice, "--headless", "--convert-to", "txt:Text (encoded):UTF8", "--outdir", d, str(arq)],
                       check=True, capture_output=True, timeout=180)
        return next(Path(d).glob("*.txt")).read_text(encoding="utf-8", errors="replace")


def num(s: str) -> str:
    return s.replace(".", "").lstrip("0") or "0"


def diploma(cauda: str):
    for padrao, sigla in DIPLOMAS:
        m = re.match(padrao, cauda, re.I)
        if m:
            if sigla == "LEI":
                return f"Lei {num(m.group(1))}/{m.group(2)[-4:] if len(m.group(2)) == 4 else m.group(2)}"
            if sigla == "DL":
                return f"DL {num(m.group(1))}/{m.group(2)}"
            if sigla == "RES":
                return f"Res. {m.group(1).upper()} {num(m.group(2))}/{m.group(3)}"
            return sigla
    return None


def extrair(texto: str) -> list:
    t = re.sub(r"\s+", " ", texto)
    achados = []

    def add(tipo, chave, trecho):
        if not any(a["chave_norm"] == chave for a in achados):
            achados.append({"tipo": tipo, "chave_norm": chave, "trecho": trecho.strip()[:160]})

    for m in PREC.finditer(t):
        classe = re.sub(r"\s+", " ", m.group(1)).replace(" na ", " no ").replace(" nos ", " no ")
        add("precedente", f"{classe.upper()} {num(m.group(2))}", m.group(0))
    for m in SUM.finditer(t):
        vinc = bool(m.group(1))
        trib = "STF" if vinc else (m.group(3) or "?").upper()
        add("sumula", f"SUMULA{' VINCULANTE' if vinc else ''} {trib} {num(m.group(2))}", m.group(0))
    for m in SUM_ENUNC.finditer(t):
        vinc = bool(m.group(2))
        add("sumula", f"SUMULA{' VINCULANTE' if vinc else ''} {m.group(3).upper()} {num(m.group(1))}", m.group(0))
    for m in TEMA.finditer(t):
        add("tema", f"TEMA {(m.group(2) or '?').upper()} {num(m.group(1))}", m.group(0))
    for m in ART.finditer(t):
        resto = t[m.end():m.end() + 140]
        dip = diploma(resto)
        nums = re.findall(NUMS, m.group(1))
        for n in nums:
            tipo = "regimento" if dip in ("RITJAL", "RISTJ", "RISTF") else "dispositivo"
            add(tipo, f"{dip or '?'} ART {num(n.split('-')[0])}{('-' + n.split('-')[1]) if '-' in n else ''}",
                m.group(0) + resto[:40])
    return achados


def norm_ledger(entrada: dict):
    chaves = [a["chave_norm"] for a in extrair(entrada.get("chave", ""))]
    return chaves


def conferir(arq: Path, ledger: Path):
    achados = extrair(texto_de(arq))
    entradas = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else []
    indice = {}
    for e in entradas:
        for k in norm_ledger(e):
            # VERIFIED prevalece sobre qualquer outra entrada da mesma chave
            if indice.get(k, {}).get("status") != "VERIFIED":
                indice[k] = e
    bloq, apont, ok = [], [], []
    for a in achados:
        if "?" in a["chave_norm"]:
            apont.append({**a, "problema": "fonte/diploma não identificado — conferir manualmente"})
            continue
        e = indice.get(a["chave_norm"])
        if not e:
            bloq.append({**a, "problema": "citação sem entrada no ledger"})
        elif e.get("status") == "REJECTED":
            bloq.append({**a, "problema": f"citação REJEITADA no ledger ({e.get('id')}): {e.get('observacao', '')}"})
        elif e.get("status") != "VERIFIED":
            bloq.append({**a, "problema": f"entrada {e.get('id')} ainda {e.get('status')}"})
        else:
            ok.append({**a, "ledger": e.get("id")})
    return {"arquivo": str(arq), "verificadas": ok, "bloqueantes": bloq, "apontamentos": apont,
            "aprovada": not bloq}


def main(argv):
    if not argv:
        print(__doc__); return 2
    arq = Path(argv[0])
    if "--listar" in argv:
        achados = extrair(texto_de(arq))
        fila = [{"id": f"P{i + 1:03d}", "tipo": a["tipo"], "chave": a["trecho"], "chave_norm": a["chave_norm"],
                 "status": "PENDENTE", "orgao": "", "relator": "", "julgamento": "", "publicacao": "",
                 "fonte": "", "trecho_literal": "", "observacao": ""} for i, a in enumerate(achados)]
        out = json.dumps(fila, ensure_ascii=False, indent=2)
        if "--saida" in argv:
            Path(argv[argv.index("--saida") + 1]).write_text(out, encoding="utf-8")
        print(out)
        return 0
    ledger = Path(argv[argv.index("--ledger") + 1]) if "--ledger" in argv else arq.parent / "_verificacoes.json"
    r = conferir(arq, ledger)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["aprovada"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
