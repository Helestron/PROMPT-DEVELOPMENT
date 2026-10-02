#!/usr/bin/env python3
"""Conferência de citações: jurisprudência, súmulas, temas, dispositivos legais e regimentais.

Extrai de uma minuta (ou de voto de outro gabinete) todas as citações e as confronta com o
ledger de verificações (_verificacoes.json). Citação sem entrada VERIFIED é pendência
bloqueante; citação de entrada REJECTED ou PENDENTE também — havendo mais de uma entrada para a
mesma citação, prevalece a mais restritiva (REJECTED, depois PENDENTE, depois VERIFIED).

Reconhece precedentes pela sigla ou pelo nome da classe (inclusive com "n.°"), súmulas e temas
no singular ou em lista ("Súmulas 718 e 719 do STF"), dispositivos nas formas "art. 59 do CP" e
"CP, art. 59" e precedentes do TJAL pelo número CNJ, quando o contexto indica julgado (TJAL,
"Rel.", "julgado em", "DJe", "desta Câmara", "orientação", "entendimento"); outro número CNJ,
salvo o do próprio processo (--processo), vira apontamento. Dispositivo cujo diploma não se identifica também vira apontamento. No .docx,
lê também tabelas, hiperlinks e inserções controladas; ignora texto excluído e runs vermelhos.

Uso:
    python conferir_citacoes.py arquivo.(docx|rtf|odt|pdf|txt|doc) --ledger _verificacoes.json
                                [--processo NNNNNNN-DD.AAAA.8.02.OOOO]
        (.docx, .rtf, .odt e .txt são lidos sem dependências externas; .pdf usa pdftotext ou
         pdfplumber; .doc exige LibreOffice ou conversão prévia para .docx)
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
import unicodedata
from pathlib import Path

NO = r"(?:n\.?\s*[º°]?s?\s*)?"  # "n.º", "nº", "n.°", "n.ºs", "n." — opcional
# Classes por extenso, das mais longas às mais curtas, com a sigla normalizada.
CLASSES_EXTENSO = [
    (r"Recurso\s+(?:Ordin[áa]rio\s+)?em\s+Habeas\s+Corpus", "RHC"),
    (r"Habeas\s+Corpus", "HC"),
    (r"Agravo\s+em\s+Recurso\s+Especial", "ARESP"),
    (r"Embargos\s+de\s+Diverg[êe]ncia\s+em\s+Recurso\s+Especial", "ERESP"),
    (r"Recurso\s+Especial", "RESP"),
    (r"Agravo\s+em\s+Recurso\s+Extraordin[áa]rio", "ARE"),
    (r"Recurso\s+Extraordin[áa]rio", "RE"),
    (r"Recurso\s+(?:Ordin[áa]rio\s+)?em\s+Mandado\s+de\s+Seguran[çc]a", "RMS"),
    (r"Reclama[çc][ãa]o", "RCL"),
]
PREFIXOS_EXTENSO = [(r"Agravo\s+Regimental", "AGRG"), (r"Agravo\s+Interno", "AGINT"),
                    (r"Embargos\s+de\s+Declara[çc][ãa]o", "EDCL")]
_SIGLAS = r"HC|RHC|REsp|RESP|AREsp|ARESP|EREsp|ERESP|EAREsp|EARESP|RE|ARE|ADI|ADC|ADPF|Rcl|RCL|RMS|MS|AP|Inq|INQ|CC|RvCr"
_PREF = r"AgRg|AGRG|AgInt|AGINT|EDcl|EDCL|EAREsp|ED"
PREC = re.compile(
    rf"\b((?:(?:{_PREF})\s+n[oa]s?\s+(?:(?:{_PREF})\s+n[oa]s?\s+)?)?(?:{_SIGLAS}))"
    rf"\s*{NO}(\d{{1,3}}(?:\.\d{{3}})+|\d{{2,7}})(?![\d-])(?:\s*/\s*([A-Z]{{2}}))?")
PREC_EXTENSO = re.compile(
    rf"\b((?:(?:{'|'.join(x for x, _ in PREFIXOS_EXTENSO)})\s+n[oa]s?\s+)?"
    rf"(?:{'|'.join(x for x, _ in CLASSES_EXTENSO)}))"
    rf"\s*{NO}(\d{{1,3}}(?:\.\d{{3}})+|\d{{2,7}})(?![\d-])(?:\s*/\s*([A-Z]{{2}}))?", re.I)
CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")
INDICIO_JULGADO = re.compile(r"\bTJ[A-Z]{2}\b|\bRel(?:\.|ator|atora)\b|\bjulgad[oa]\b|\bj\.\s*\d|\bDJ[eE]?\b|"
                             r"\bDJAL\b|\bac[óo]rd[ãa]o\b|\bprecedente|\bdesta\s+(?:Câmara|Corte)\b|"
                             r"\bdeste\s+Tribunal\b|\bCâmara\s+Criminal\b|\borienta[çc][ãa]o\b|\bentendimento\b|"
                             r"\bjurisprud", re.I)
TRIB = r"STF|STJ|TJAL|TFR|Supremo\s+Tribunal\s+Federal|Superior\s+Tribunal\s+de\s+Justi[çc]a"
ITEM_SUM = rf"{NO}\d{{1,4}}(?:\s*/\s*(?:STF|STJ|TJAL|TFR))?"
SUM = re.compile(
    rf"\bS[úu]mulas?\s+(Vinculantes?\s+)?({ITEM_SUM}(?:(?:\s*,\s*|\s+e\s+){ITEM_SUM})*)"
    rf"(?:\s*(?:/|d[oa])\s*({TRIB}))?", re.I)
SUM_ENUNC = re.compile(rf"\benunciados?\s+{NO}(\d{{1,4}})\s+da\s+S[úu]mula\s+(Vinculante\s+)?d[oa]\s+({TRIB})", re.I)
ITEM_TEMA = rf"{NO}(?:\d{{1,2}}\.\d{{3}}|\d{{1,4}})(?:\s*/\s*(?:STF|STJ))?"
TEMA = re.compile(
    rf"\bTemas?\s+({ITEM_TEMA}(?:(?:\s*,\s*|\s+e\s+){ITEM_TEMA})*)"
    rf"(?:\s*(?:/|d[oa])\s*({TRIB})|\s+da\s+(repercuss[ãa]o\s+geral)|\s+dos\s+(?:recursos\s+)?(repetitivos))?", re.I)
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
    (r"Lei\s+(?:Complementar\s+)?(?:n\.?\s*[º°]?\s*)?(\d[\d\.]*)\s*/\s*(\d{2,4})", "LEI"),
    (r"Decreto-Lei\s+(?:n\.?\s*[º°]?\s*)?(\d[\d\.]*)\s*/\s*(\d{2,4})", "DL"),
    (r"Resolu[çc][ãa]o\s+(CNJ|TJAL)\s+(?:n\.?\s*[º°]?\s*)?(\d[\d\.]*)\s*/\s*(\d{4})", "RES"),
]
NUMS = r"\d+(?:\.\d{3})*(?:-[A-Z])?"
LISTA_ARTS = rf"({NUMS}(?:\s*(?:,|e|a)\s*{NUMS})*)"
# "art. 59 do CP": o diploma vem até 90 caracteres depois, sem atravessar outro "art." — em
# "art. 5º, LVII, e o art. 386 do CPP", o art. 5º fica sem diploma (apontamento), não vira CPP.
ART = re.compile(rf"\barts?\.\s*{LISTA_ARTS}((?:(?!\barts?\.).){{0,90}}?)\b(?:d[oa]s?|dest[ea])\s+",
                 re.S | re.I)
ART_SOLTO = re.compile(rf"\barts?\.\s*{LISTA_ARTS}", re.I)
# Forma inversa: "(CF, art. 93, IX)", "Lei n.º 11.343/2006, art. 33".
ART_INVERSO = re.compile(
    r"\b(CPP|CPC|CP|CF(?:/88)?|CRFB|LEP|RITJAL|RISTJ|RISTF"
    r"|Lei\s+(?:Complementar\s+)?(?:n\.?\s*[º°]?\s*)?\d[\d\.]*\s*/\s*\d{2,4}"
    r"|Decreto-Lei\s+(?:n\.?\s*[º°]?\s*)?\d[\d\.]*\s*/\s*\d{2,4})"
    rf"\s*,\s*(arts?\.\s*{LISTA_ARTS})")
# Destinos RTF que não contêm texto do documento (tabelas de fontes, cores, estilos, metadados,
# imagens, cabeçalhos e rodapés).
RTF_IGNORAR = {"fonttbl", "colortbl", "stylesheet", "info", "pict", "object", "header", "footer",
               "headerl", "headerr", "headerf", "footerl", "footerr", "footerf", "listtable",
               "listoverridetable", "rsidtbl", "generator", "xmlnstbl", "datastore", "themedata",
               "colorschememapping", "latentstyles", "pgdsctbl", "filetbl", "revtbl", "fldinst"}
RTF_TOKEN = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})? ?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|([^\\{}]+)", re.I)


def rtf_para_texto(rtf: str) -> str:
    """Extrai o texto de um RTF sem dependências externas (parágrafos, tabulações, acentos em
    \\'hh e \\uN, campos de fonte, cores e metadados ignorados)."""
    pilha, ignorar, uc, pular = [], False, 1, 0
    saida = []
    for m in RTF_TOKEN.finditer(rtf):
        palavra, arg, hexa, simbolo, chave, texto = m.groups()
        if chave == "{":
            pilha.append((ignorar, uc))
            continue
        if chave == "}":
            if pilha:
                ignorar, uc = pilha.pop()
            continue
        if pular and (texto or hexa or simbolo):
            if texto:
                consumir = min(pular, len(texto))
                texto, pular = texto[consumir:], pular - consumir
                if not texto:
                    continue
            else:
                pular -= 1
                continue
        if simbolo:
            if simbolo == "*":
                ignorar = True
            elif not ignorar and simbolo in "\\{}":
                saida.append(simbolo)
            elif not ignorar and simbolo == "~":
                saida.append("\u00a0")
            elif not ignorar and simbolo == "_":
                saida.append("-")
            continue
        if hexa:
            if not ignorar:
                saida.append(bytes([int(hexa, 16)]).decode("cp1252", errors="replace"))
            continue
        if palavra:
            palavra = palavra.lower()
            if palavra in RTF_IGNORAR:
                ignorar = True
            elif palavra == "uc" and arg:
                uc = int(arg)
            elif palavra == "u" and arg:
                if not ignorar:
                    n = int(arg)
                    saida.append(chr(n + 65536 if n < 0 else n))
                pular = uc
            elif not ignorar and palavra in ("par", "line", "sect", "page"):
                saida.append("\n")
            elif not ignorar and palavra == "tab":
                saida.append("\t")
            elif not ignorar and palavra in ("emdash", "endash"):
                saida.append("—" if palavra == "emdash" else "–")
            continue
        if texto and not ignorar:
            saida.append(texto.replace("\r", "").replace("\n", ""))
    # pares substitutos (caracteres fora do plano básico) gravados como dois \uN
    return "".join(saida).encode("utf-16", "surrogatepass").decode("utf-16", errors="replace")


def odt_para_texto(arq: Path) -> str:
    import html
    import zipfile
    xml = zipfile.ZipFile(arq).read("content.xml").decode("utf-8")
    xml = re.sub(r"<text:s(?: text:c=\"(\d+)\")?/>", lambda m: " " * int(m.group(1) or 1), xml)
    xml = re.sub(r"<text:tab/>", "\t", xml)
    xml = re.sub(r"<text:line-break/>|</text:p>|</text:h>", "\n", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml))


def docx_para_texto(arq: Path) -> str:
    """Texto de todos os parágrafos do .docx — inclusive em tabelas, hiperlinks, campos e
    inserções controladas —, exceto o texto excluído (w:del, w:moveFrom) e os runs em vermelho,
    que são apontamentos internos da versão anotada e não irão aos autos."""
    from docx import Document
    from docx.oxml.ns import qn
    W_R, W_T, W_TAB, W_BR = qn("w:r"), qn("w:t"), qn("w:tab"), qn("w:br")
    EXCLUIDO = {qn("w:del"), qn("w:moveFrom")}

    def vermelho(r):
        cor = r.find(f"{qn('w:rPr')}/{qn('w:color')}")
        return cor is not None and (cor.get(qn("w:val")) or "").upper() == "FF0000"

    def excluido(el):
        pai = el.getparent()
        while pai is not None:
            if pai.tag in EXCLUIDO:
                return True
            pai = pai.getparent()
        return False

    linhas = []
    for p in Document(arq).element.body.iter(qn("w:p")):
        partes = []
        for r in p.iter(W_R):
            if vermelho(r) or excluido(r):
                continue
            for el in r:
                if el.tag == W_T:
                    partes.append(el.text or "")
                elif el.tag == W_TAB:
                    partes.append("\t")
                elif el.tag == W_BR:
                    partes.append("\n")
        linhas.append("".join(partes))
    return "\n".join(linhas)


def texto_de(arq: Path) -> str:
    return unicodedata.normalize("NFC", _texto_bruto(arq))


def _texto_bruto(arq: Path) -> str:
    suf = arq.suffix.lower()
    if suf == ".txt":
        return arq.read_text(encoding="utf-8", errors="replace")
    if suf == ".rtf":
        return rtf_para_texto(arq.read_bytes().decode("latin-1"))
    if suf == ".odt":
        return odt_para_texto(arq)
    if suf == ".docx":
        return docx_para_texto(arq)
    if suf == ".pdf":
        if shutil.which("pdftotext"):
            return subprocess.run(["pdftotext", "-layout", str(arq), "-"], capture_output=True, text=True).stdout
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("Sem leitor de PDF: instale o Poppler (pdftotext) ou `pip install pdfplumber`.")
        with pdfplumber.open(arq) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError(f"Sem conversor para {suf}: salve o arquivo como .docx (Word) ou instale o LibreOffice.")
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


def tribunal(txt):
    """Sigla do tribunal a partir da sigla ou do nome por extenso."""
    if not txt:
        return None
    t = re.sub(r"\s+", " ", txt).lower()
    if t.startswith("supremo"):
        return "STF"
    if t.startswith("superior"):
        return "STJ"
    return txt.upper()


def itens(lista: str, padrao_trib: str, final):
    """Números de uma lista ("440/STJ, 718 e 719/STF"); o tribunal escrito depois de um número
    vale para os anteriores que não tenham o seu, como na escrita forense."""
    achados = re.findall(rf"(\d{{1,2}}\.\d{{3}}|\d{{1,4}})(?:\s*/\s*({padrao_trib}))?", lista, re.I)
    saida, prox = [], final
    for n, trib in reversed(achados):
        prox = trib.upper() if trib else prox
        saida.append((n, prox))
    return list(reversed(saida))


def classe_extenso(txt: str) -> str:
    t = re.sub(r"\s+", " ", txt)
    pref = ""
    for padrao, sigla in PREFIXOS_EXTENSO:
        m = re.match(rf"{padrao}\s+n[oa]s?\s+", t, re.I)
        if m:
            pref, t = f"{sigla} NO ", t[m.end():]
            break
    for padrao, sigla in CLASSES_EXTENSO:
        if re.fullmatch(padrao, t, re.I):
            return pref + sigla
    return pref + t.upper()


def dispositivo(dip, n):
    tipo = "regimento" if dip in ("RITJAL", "RISTJ", "RISTF") else "dispositivo"
    base, _, letra = n.partition("-")
    return tipo, f"{dip or '?'} ART {num(base)}{('-' + letra) if letra else ''}"


def extrair(texto: str, processo: str = None) -> list:
    t = re.sub(r"\s+", " ", texto)
    achados = []

    def add(tipo, chave, trecho):
        if not any(a["chave_norm"] == chave for a in achados):
            achados.append({"tipo": tipo, "chave_norm": chave, "trecho": trecho.strip()[:160]})

    for m in PREC.finditer(t):
        classe = re.sub(r"\s+", " ", m.group(1)).replace(" na ", " no ").replace(" nos ", " no ")
        add("precedente", f"{classe.upper()} {num(m.group(2))}", m.group(0))
    for m in PREC_EXTENSO.finditer(t):
        add("precedente", f"{classe_extenso(m.group(1))} {num(m.group(2))}", m.group(0))
    for m in CNJ.finditer(t):
        if processo and m.group(0) == processo:
            continue  # o próprio processo
        janela = t[max(0, m.start() - 150):m.end() + 150]
        tipo = "precedente" if INDICIO_JULGADO.search(janela) else "processo"
        add(tipo, f"CNJ {m.group(0)}", t[max(0, m.start() - 60):m.end() + 20])
    for m in SUM.finditer(t):
        vinc = bool(m.group(1))
        for n, trib in itens(m.group(2), "STF|STJ|TJAL|TFR", tribunal(m.group(3))):
            trib = "STF" if vinc else (trib or "?")
            add("sumula", f"SUMULA{' VINCULANTE' if vinc else ''} {trib} {num(n)}", m.group(0))
    for m in SUM_ENUNC.finditer(t):
        vinc = bool(m.group(2))
        add("sumula", f"SUMULA{' VINCULANTE' if vinc else ''} {tribunal(m.group(3))} {num(m.group(1))}", m.group(0))
    for m in TEMA.finditer(t):
        final = tribunal(m.group(2)) or ("STF" if m.group(3) else "STJ" if m.group(4) else None)
        for n, trib in itens(m.group(1), "STF|STJ", final):
            add("tema", f"TEMA {trib or '?'} {num(n)}", m.group(0))
    resolvidos = set()
    for m in ART.finditer(t):
        resto = t[m.end():m.end() + 140]
        dip = diploma(resto)
        resolvidos.add(m.start())
        for n in re.findall(NUMS, m.group(1)):
            add(*dispositivo(dip, n), m.group(0) + resto[:40])
    for m in ART_INVERSO.finditer(t):
        dip = diploma(m.group(1))
        resolvidos.add(m.start(2))
        for n in re.findall(NUMS, m.group(3)):
            add(*dispositivo(dip, n), m.group(0))
    for m in ART_SOLTO.finditer(t):  # dispositivo sem diploma identificável
        if m.start() not in resolvidos:
            for n in re.findall(NUMS, m.group(1)):
                add(*dispositivo(None, n), t[m.start():m.end() + 60])
    return achados


def norm_ledger(entrada: dict):
    """Chave normalizada de uma entrada do ledger: a `chave_norm` gravada pela fila (--listar) ou,
    na falta, a primeira citação reconhecida na `chave` — uma entrada confere uma única citação."""
    if entrada.get("chave_norm"):
        return [entrada["chave_norm"]]
    return [a["chave_norm"] for a in extrair(entrada.get("chave", ""))][:1]


RIGOR = {"REJECTED": 0, "VERIFIED": 2}  # qualquer outro status (PENDENTE etc.) = 1


def conferir(arq: Path, ledger: Path, processo: str = None):
    achados = extrair(texto_de(arq), processo)
    entradas = json.loads(ledger.read_text(encoding="utf-8")) if ledger.exists() else []
    indice = {}
    for e in entradas:
        for k in norm_ledger(e):
            # Havendo mais de uma entrada para a mesma citação, prevalece a mais restritiva.
            if k not in indice or RIGOR.get(e.get("status"), 1) < RIGOR.get(indice[k].get("status"), 1):
                indice[k] = e
    bloq, apont, ok = [], [], []
    for a in achados:
        if a["tipo"] == "processo":
            apont.append({**a, "problema": "número CNJ citado sem indício de julgado — se for precedente, "
                                           "registre-o no ledger; se for processo do caso, nada a fazer"})
            continue
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
    processo = argv[argv.index("--processo") + 1] if "--processo" in argv else None
    if "--listar" in argv:
        achados = [a for a in extrair(texto_de(arq), processo) if a["tipo"] != "processo"]
        fila = [{"id": f"P{i + 1:03d}", "tipo": a["tipo"], "chave": a["trecho"], "chave_norm": a["chave_norm"],
                 "status": "PENDENTE", "orgao": "", "relator": "", "julgamento": "", "publicacao": "",
                 "fonte": "", "trecho_literal": "", "observacao": ""} for i, a in enumerate(achados)]
        out = json.dumps(fila, ensure_ascii=False, indent=2)
        if "--saida" in argv:
            Path(argv[argv.index("--saida") + 1]).write_text(out, encoding="utf-8")
        print(out)
        return 0
    ledger = Path(argv[argv.index("--ledger") + 1]) if "--ledger" in argv else arq.parent / "_verificacoes.json"
    r = conferir(arq, ledger, processo)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["aprovada"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
