#!/usr/bin/env python3
"""Portão léxico e de estilo das minutas (SKILL.md, Fase 4, portão 1).

Verifica um .docx (versão anotada ou limpa) e devolve, em JSON, as pendências BLOQUEANTES
(impedem a geração da versão limpa e a inserção no SAJ/SG5) e os APONTAMENTOS de revisão
(cada um deve ser reexaminado e justificado na lista de trabalho; o não justificado vira
bloqueante).

Uso:
    python verificar_minuta.py arquivo.docx --tipo voto|relatorio|voto_vogal|voto_vista|voto_vencido|
                               declaracao_voto|referendo|decisao|despacho|ementa|nota_revisao
                               --versao anotada|limpa [--config ../config/gabinete.json]
Código de saída: 0 aprovado; 1 há bloqueantes; 2 uso incorreto (tipo ou versão desconhecidos).

As listas "linguagem_de_metodo", "termos_tema" e "termos_prazo" são expressões regulares, para
não confundir linguagem de método com fatos do processo ("extração de dados do celular",
"varredura policial no imóvel", "distância percorrida", "texto extraído do aparelho celular").

O texto é lido em Unicode NFC. Tabela, caixa de texto, hiperlink, campo, controle de conteúdo e
alteração controlada pendente bloqueiam: o portão e o conversor para RTF leem apenas parágrafos
e runs simples, e o que estivesse nessas estruturas sumiria do documento enviado ao SAJ sem ter
sido verificado.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

PADRAO = {
    "titulos_admitidos": ["DESPACHO", "DECISÃO", "DECISÃO MONOCRÁTICA", "RELATÓRIO", "VOTO",
                          "VOTO-VISTA", "VOTO DIVERGENTE", "VOTO VENCIDO", "DECLARAÇÃO DE VOTO",
                          "VOTO (REFERENDO DE LIMINAR)", "EMENTA", "NOTA DE REVISÃO"],
    "ultima_linha": {
        "despacho": "Publicações e intimações via DJEN",
        "decisao": "Publicações e intimações via DJEN",
        "voto": "É como voto.",
        "voto_vogal": "É como voto.",
        "voto_vista": "É como voto.",
        "voto_vencido": "É como voto.",
        "declaracao_voto": "É como voto.",
        "referendo": "É como voto.",
    },
    "fecho_relatorio": {
        "decisao": "Brevemente relatado, passo a decidir.",
        "voto": "É o relatório.",
        "relatorio": "É o relatório.",
    },
    "expressoes_vedadas": ["publique-se", "intime-se", "intimem-se", "cumpra-se", "registre-se"],
    "linguagem_de_metodo": [r"varredura\s+(?:dos|das|do|da)\s+(?:autos|peças|processo|documentos)",
                            r"camada de texto", r"extração\s+(?:de|do)\s+texto",
                            r"texto\s+extraído\s+(?:dos\s+autos|da\s+pasta|do\s+pdf|das?\s+peças?|dos?\s+documentos?)",
                            r"\bocr\b", r"renderiz", r"página a página",
                            r"(?:páginas?|peças?|documentos?|folhas?)\s+(?:foram\s+)?examinad[oa]s?\s+visualmente",
                            r"percorrid[oa]s?\s+(?:tod[oa]s\s+)?(?:as|os|a)\s+(?:peças|autos|íntegra|documentos|páginas)",
                            r"leitura integral", r"confrontad[oa]s?\s+(?:com\s+)?o\s+(?:cposg|cpopg)",
                            r"linha a linha", r"inteligência artificial", r"modelo de linguagem"],
    "verbos_fragmento": ["rejeitada", "rejeitado", "afastada", "afastado", "superada", "superado",
                         "indeferido", "indeferida", "prejudicada", "prejudicado", "rejeito", "acolho",
                         "indefiro", "defiro", "reconheço", "afasto", "conheço", "nego", "dou", "passo",
                         "presentes", "ausentes", "mantida", "mantido"],
    "transicoes": ["desse modo", "dessa forma", "por tais motivos", "assim", "com efeito", "nesse passo",
                   "por isso", "por conseguinte", "diante disso", "logo", "portanto", "ante o exposto",
                   "isso posto", "nessa linha", "em consequência", "por essas razões"],
    "termos_tema": [r"\btema\s+(?:n\.?\s*º?\s*)?\d", r"\brepetitiv", r"repercussão geral", r"\biac\b"],
    "termos_prazo": [r"dias úteis", r"\bart\. 219\b", r"\bart\. 224\b", r"\bart\. 798\b", r"tempestiv",
                     r"preclus", r"decurso do prazo"],
    "max_palavras_paragrafo": 150,
    "formulas_fixas": ["À douta revisão.", "É como voto.", "É o relatório."],
}
MARCA_RESSALVA = "Resolução CNJ n.º 615/2025"
MARCA_ADVERTENCIA = "Os trechos em vermelho são apontamentos de conferência"
DATA = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
                  r"|\b(?:0?[1-9]|[12]\d|3[01])\.(?:0?[1-9]|1[0-2])\.(?:19|20)\d{2}\b"
                  r"|\b\d{1,2}\.?[º°]?\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|"
                  r"outubro|novembro|dezembro)\b(?:\s+de\s+\d{4})?", re.I)
HORA = re.compile(r"\b\d{1,2}:\d{2}\b|\b\d{1,2}h(?:\d{2})?(?:min)?\b|\bàs\s+\d{1,2}\s*horas?\b", re.I)
ROMANO = re.compile(r"^\s*(?:[IVXL]+|\d+)\s*(?:[-–—.)]|\.\d)\s*")
# Bloco de assinatura: linha de local e data, linha do nome do magistrado ou linha do cargo.
FECHO_ASSINATURA = re.compile(r"^(?:Macei[óo](?:/AL)?\s*[,.]|(?:Des\.|Desembargador(?:a)?)\s+[^,;:]{0,80}$"
                              r"|Relator(?:a|\(a\))?\.?$)", re.I)
# "P. R. I." (publique-se, registre-se, intime-se) como fecho; no meio do texto, pode ser iniciais de parte.
PRI = re.compile(r"\bP\.\s*R\.\s*I\.(?:\s*C\.)?\s*$|\bP\.\s*I\.(?:\s*C\.)?\s*$")
# Colchetes legítimos em citações: supressão e anotações usuais; qualquer outro é campo pendente.
COLCHETE_ADMITIDO = re.compile(
    r"\[(?:\.\.\.|…|sic!?|grifei|destaquei|negritei|g\.\s*n\.|n\.\s*g\.|"
    r"(?:grifos?|destaques?)\s+(?:nossos?|meus?|do\s+original|no\s+original|acrescidos?))\]", re.I)
NAO_SUPORTADO = {"w:tbl": "tabela", "w:txbxContent": "caixa de texto", "w:ins": "alteração controlada pendente",
                 "w:del": "alteração controlada pendente", "w:moveFrom": "alteração controlada pendente",
                 "w:moveTo": "alteração controlada pendente"}
TIPOS = {"despacho", "decisao", "relatorio", "voto", "voto_vogal", "voto_vista", "voto_vencido",
         "declaracao_voto", "referendo", "ementa", "nota_revisao"}


def carregar(config):
    cfg = json.loads(json.dumps(PADRAO))
    if config and Path(config).exists():
        extra = json.loads(Path(config).read_text(encoding="utf-8")).get("redacao", {})
        for k, v in extra.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    return cfg


def vermelho(run):
    c = run.font.color
    return c is not None and c.type is not None and c.rgb is not None and str(c.rgb).upper() == "FF0000"


def nfc(texto):
    return unicodedata.normalize("NFC", texto)


def estruturas_nao_suportadas(doc) -> list:
    """Estruturas cujo texto o portão e o conversor RTF não leem (o texto se perderia)."""
    corpo = doc.element.body
    achados = {nome for tag, nome in NAO_SUPORTADO.items() if corpo.find(".//" + qn(tag)) is not None}
    for p in corpo.iterchildren(qn("w:p")):
        diretos = set(p.iterchildren(qn("w:r")))
        if any(r not in diretos and r.find(qn("w:t")) is not None for r in p.iter(qn("w:r"))):
            achados.add("texto em hiperlink, campo ou controle de conteúdo")
    return sorted(achados)


def ler(arquivo):
    doc = Document(arquivo)
    pars = []
    for p in doc.paragraphs:
        texto = nfc(p.text).strip()
        if not texto:
            continue
        todos = [r for r in p.runs if r.text]
        runs = [r for r in todos if r.text.strip()]
        # Trechos em negrito contíguos (o Word fragmenta runs), com o texto que os antecede e segue.
        negritos, i = [], 0
        while i < len(todos):
            if not todos[i].bold:
                i += 1
                continue
            j = i
            while j < len(todos) and (todos[j].bold or not todos[j].text.strip()):
                j += 1
            negritos.append((nfc("".join(r.text for r in todos[i:j])).strip(),
                             nfc("".join(r.text for r in todos[:i])), nfc("".join(r.text for r in todos[j:]))))
            i = j
        pars.append({
            "texto": texto,
            "todo_vermelho": bool(runs) and all(vermelho(r) for r in runs),
            "tem_vermelho": any(vermelho(r) for r in runs),
            "todo_negrito": bool(runs) and all(r.bold for r in runs),
            "negritos": negritos,
            "recuo_cm": (p.paragraph_format.left_indent.cm if p.paragraph_format.left_indent else 0),
        })
    return pars, estruturas_nao_suportadas(doc)


def palavras(t):
    return len(re.findall(r"\w+", t))


def verificar(arquivo, tipo, versao, config=None):
    cfg = carregar(config or Path(__file__).resolve().parent.parent / "config" / "gabinete.json")
    pars, estruturas = ler(arquivo)
    B, A = [], []
    titulos = {t.upper() for t in cfg["titulos_admitidos"]}
    corpo = [p for p in pars if not p["todo_vermelho"]]
    textos = [p["texto"] for p in corpo]
    completo = "\n".join(textos)
    baixo = completo.lower()

    # 1. Marcas de uso interno conforme a versão
    if versao == "anotada":
        if MARCA_RESSALVA not in "\n".join(p["texto"] for p in pars):
            B.append("versão anotada sem a ressalva do art. 93, IX, da CF / Resolução CNJ n.º 615/2025")
        if MARCA_ADVERTENCIA not in "\n".join(p["texto"] for p in pars):
            B.append("versão anotada sem a advertência final sobre os trechos em vermelho")
        if not any(p["tem_vermelho"] for p in pars):
            B.append("versão anotada sem aplicação efetiva da cor vermelha (FF0000)")
    else:
        if any(p["tem_vermelho"] for p in pars):
            B.append("resíduo vermelho na versão limpa")
        for marca in ("[Conferir", MARCA_RESSALVA, MARCA_ADVERTENCIA, "Obs.:"):
            if marca in completo:
                B.append(f"marca de uso interno na versão limpa: {marca!r}")
        if re.search(r"\[[^\]]*\]", COLCHETE_ADMITIDO.sub("", completo)):
            B.append("colchete de campo não preenchido na versão limpa")

    if tipo == "nota_revisao":  # documento interno: só as marcas acima importam
        return {"arquivo": str(arquivo), "tipo": tipo, "versao": versao, "bloqueantes": B, "apontamentos": A}

    for nome in estruturas:
        B.append(f"estrutura não suportada pelo portão e pelo conversor RTF ({nome}): converta em texto "
                 "corrido ou, nas alterações controladas, aceite ou rejeite todas antes de verificar")

    # 2. Expressões vedadas e fecho com local/data/assinatura
    for exp in cfg["expressoes_vedadas"]:
        if re.search(rf"\b{re.escape(exp)}\b", baixo):
            B.append(f"expressão vedada: {exp!r}")
    for t in textos[-4:]:
        # Bloco de assinatura é curto; menção ao "Desembargador Relator" no corpo do voto não é fecho.
        if palavras(t) <= 12 and (FECHO_ASSINATURA.search(t) or DATA.search(t)):
            B.append(f"fecho com local, data ou identificação do magistrado: {t[:80]!r}")
    for t in textos:
        if PRI.search(t):
            B.append(f"expressão vedada: fórmula abreviada de publicação e intimação em {t[-60:]!r}")
    # Linguagem de método é vedada em toda peça que vai aos autos, inclusive na ementa.
    for termo in cfg["linguagem_de_metodo"]:
        m = re.search(rf"(?<!\w)(?:{termo})", baixo)
        if m:
            B.append(f"linguagem de método: {m.group(0)!r}")

    # 3. Última linha
    ult = cfg["ultima_linha"].get(tipo)
    if ult and (not textos or textos[-1] != ult):
        B.append(f"a última linha deve ser exatamente {ult!r} (encontrado: {textos[-1][:60] if textos else ''!r})")

    # 4. Relatório: fecho fixo, uma única vez; sem datas nem horários
    fecho = cfg["fecho_relatorio"].get(tipo)
    if fecho:
        idx = [i for i, t in enumerate(textos) if t == fecho]
        if len(idx) != 1:
            B.append(f"o relatório deve encerrar-se, uma única vez, com {fecho!r} (ocorrências: {len(idx)})")
        else:
            inicio = next((i for i, t in enumerate(textos) if t.upper() in titulos), -1)
            for t in textos[inicio + 1:idx[0]]:
                if DATA.search(t) or HORA.search(t):
                    B.append(f"data ou horário no relatório: {t[:80]!r}")
        for outra in ("relatei", "decido.", "é o breve relatório", "é o relatório"):
            if outra != fecho.lower() and outra in baixo and not fecho.lower().startswith(outra):
                B.append(f"fórmula de transição diversa da fixa: {outra!r}")

    if tipo == "ementa":  # a ementa padronizada admite seções e caixa alta próprias
        return {"arquivo": str(arquivo), "tipo": tipo, "versao": versao, "bloqueantes": B, "apontamentos": A}

    fixos = {fecho, ult, *cfg["formulas_fixas"]}
    for i, p in enumerate(corpo):
        t = p["texto"]
        if t.upper() in titulos or t in fixos:
            continue
        citacao = p["recuo_cm"] >= 3
        # 5. Epígrafes internas
        if p["todo_negrito"] and not citacao:
            B.append(f"parágrafo inteiro em negrito (epígrafe disfarçada): {t[:70]!r}")
        if ROMANO.match(t) and palavras(t) <= 15 and not citacao:
            B.append(f"numeração de seção encabeçando bloco: {t[:70]!r}")
        if re.match(r"^(Da|Do|Das|Dos)\s", t) and palavras(t) <= 10 and not t.endswith("."):
            B.append(f"epígrafe interna: {t[:70]!r}")
        if t.isupper() and palavras(t) <= 10 and not citacao:
            B.append(f"linha em caixa alta não admitida: {t[:70]!r}")
        # 6. Frases fragmentadas (parágrafo aberto por expressão de transição está encadeado)
        transicao = any(t.lower().startswith(x) for x in cfg["transicoes"])
        if palavras(t) <= 8 and not citacao and not transicao:
            B.append(f"parágrafo fragmentado (até oito palavras): {t!r}")
        for s in re.split(r"(?<=[.!?])\s+", t):
            w = s.split()
            curto = palavras(s) <= 6 or (palavras(s) <= 12 and "," not in s)
            # Ênclise ("Nego-lhe provimento.") não disfarça o fragmento.
            if w and curto and w[0].lower().strip(",").split("-")[0] in cfg["verbos_fragmento"]:
                B.append(f"período fragmentado sem transição: {s!r}")
        # 7. Negrito de período inteiro (com o ponto dentro ou logo depois do negrito)
        for n, antes, depois in p["negritos"]:
            abre_periodo = not antes.strip() or re.search(r"[.!?:]\s*$", antes)
            if palavras(n) >= 10 and (n.endswith(".") or (abre_periodo and re.match(r"\s*[.!?]", depois))):
                B.append(f"negrito aplicado a período inteiro: {n[:70]!r}")
        # 8. Apontamentos de revisão
        if ":" in t and not citacao:
            prox = corpo[i + 1] if i + 1 < len(corpo) else None
            if not (prox and prox["recuo_cm"] >= 3 and t.rstrip().endswith(":")):
                A.append(f"dois-pontos no corpo do texto: {t[:70]!r}")
        if "—" in t or " – " in t:
            A.append(f"travessão: {t[:70]!r}")
        if palavras(t) > cfg["max_palavras_paragrafo"] and not citacao:
            A.append(f"parágrafo com {palavras(t)} palavras: {t[:50]!r}")

    for termo in cfg["termos_tema"]:
        m = re.search(termo, baixo)
        if m:
            A.append(f"menção a tema/precedente qualificado ({m.group(0)!r}): só se aplicado ou invocado")
    for termo in cfg["termos_prazo"]:
        m = re.search(termo, baixo)
        if m:
            A.append(f"passagem de prazo/preclusão ({m.group(0)!r}): só se controvertida ou conhecida de ofício")

    return {"arquivo": str(arquivo), "tipo": tipo, "versao": versao,
            "bloqueantes": sorted(set(B), key=B.index), "apontamentos": sorted(set(A), key=A.index)}


def main(argv):
    if not argv:
        print(__doc__); return 2
    tipo = argv[argv.index("--tipo") + 1] if "--tipo" in argv else "decisao"
    versao = argv[argv.index("--versao") + 1] if "--versao" in argv else "limpa"
    config = argv[argv.index("--config") + 1] if "--config" in argv else None
    if tipo not in TIPOS or versao not in ("anotada", "limpa"):
        print(f"Tipo ou versão desconhecidos: {tipo!r}/{versao!r}. Tipos: {', '.join(sorted(TIPOS))}.")
        return 2
    r = verificar(argv[0], tipo, versao, config)
    r["aprovada"] = not r["bloqueantes"]
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["aprovada"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
