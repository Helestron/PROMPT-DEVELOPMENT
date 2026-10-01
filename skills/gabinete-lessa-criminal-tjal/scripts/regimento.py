#!/usr/bin/env python3
"""Consulta ao Regimento Interno do TJAL (referencias/ritjal_integral.txt).

O texto integral é o **vigente**: o que o PDF consolidado do Tribunal traz tachado (revogado) foi
excluído na extração (`extrair_regimento.py`) e está em `referencias/ritjal_revogados.txt`, só
para consulta histórica. Dispositivos incluídos ou alterados por emenda conservam a anotação
"(Incluído/Alterado pela Emenda …)". Regra de segurança mantida: se o mesmo artigo aparecer mais
de uma vez (extração de versão antiga do PDF), prevalece a ocorrência marcada por emenda; não
havendo marca, a última.

Uso:
    python regimento.py 62                  texto vigente do art. 62
    python regimento.py 62 63 173           vários artigos
    python regimento.py --buscar "referendo"   artigos que contêm o termo
    python regimento.py --fila minuta.docx  artigos do RITJAL citados na minuta, com o texto
                                            vigente, no esquema do ledger (status PENDENTE: a
                                            pertinência é juízo de quem revisa)
    python regimento.py --revogados         texto revogado (tachado no PDF), para consulta histórica
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "referencias" / "ritjal_integral.txt"
REVOGADOS = BASE.with_name("ritjal_revogados.txt")
HIFEN_FINAL = re.compile(r"[\w)]-$")
INICIO = re.compile(r"^Art\.\s*(\d+)\s*[º°o]?\s*\.?\s*-?\s*(.*)$")
MARCA = re.compile(r"\((?:Alterad[oa]|Incluíd[oa]|Redação dada)[^)]*Emenda[^)]*\)", re.I)
VERSAO = "RITJAL aprovado em 20/08/2024, com as Emendas n.ºs 17/2025, 18/2026 e 19/2026"


def carregar(caminho=BASE):
    blocos, atual, ultimo = [], None, 0
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith("#"):
            continue
        m = INICIO.match(linha.strip())
        if m and int(m.group(1)) >= ultimo:
            ultimo = int(m.group(1))
            atual = {"numero": ultimo, "linhas": [linha.strip()]}
            blocos.append(atual)
            continue
        if atual is not None:
            # Cabeçalho estrutural: "Seção IV", "CAPÍTULO VI", "Subseção II" (numeral romano em
            # seguida). Linhas como "Seção Especializada Cível ou nas Câmaras…" são texto do artigo.
            if re.match(r"^(TÍTULO|CAPÍTULO|Seção|Subseção)\s+[IVXLC]+\b", linha.strip()):
                atual = None  # cabeçalho estrutural encerra o artigo
                continue
            atual["linhas"].append(linha.strip())
    artigos = {}
    for b in blocos:
        artigos.setdefault(b["numero"], []).append(unir(b["linhas"]))
    return artigos


def unir(linhas):
    """Une as linhas do PDF: hífen real de fim de linha ("Procurador(a)-" + "Geral") é mantido e
    a palavra se cola à seguinte; nas demais quebras, um espaço. O Regimento não usa hifenização
    silábica automática, de modo que todo hífen final é parte da palavra."""
    texto = ""
    for linha in (x for x in linhas if x):
        if texto and HIFEN_FINAL.search(texto):
            texto += linha
        else:
            texto += (" " if texto else "") + linha
    return re.sub(r"\s+", " ", texto).strip()


def vigente(ocorrencias):
    marcadas = [o for o in ocorrencias if MARCA.search(o)]
    escolhido = (marcadas or ocorrencias)[-1]
    avisos = []
    if len(ocorrencias) > 1:
        avisos.append(f"{len(ocorrencias)} redações no texto; adotada a {'marcada por emenda' if marcadas else 'última'}")
    if MARCA.search(escolhido):
        avisos.append("contém dispositivo incluído ou alterado por emenda (anotação entre parênteses no "
                      "texto); a anotação não integra a citação")
    return escolhido, avisos


def consultar(numeros, artigos=None):
    artigos = artigos or carregar()
    saida = []
    for n in numeros:
        oc = artigos.get(int(n))
        if not oc:
            saida.append({"artigo": int(n), "erro": "artigo não localizado no texto integral"})
            continue
        texto, avisos = vigente(oc)
        saida.append({"artigo": int(n), "texto": texto, "avisos": avisos, "versao": VERSAO})
    return saida


def buscar(termo, artigos=None):
    artigos = artigos or carregar()
    t = termo.lower()
    res = []
    for n in sorted(artigos):
        texto, _ = vigente(artigos[n])
        if t in texto.lower():
            i = texto.lower().index(t)
            res.append({"artigo": n, "trecho": texto[max(0, i - 120): i + 160]})
    return res


def fila(arquivo):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from conferir_citacoes import extrair, texto_de
    nums = []
    for a in extrair(texto_de(Path(arquivo))):
        m = re.fullmatch(r"RITJAL ART (\d+)", a["chave_norm"])
        if m and int(m.group(1)) not in nums:
            nums.append(int(m.group(1)))
    entradas = []
    for r in consultar(nums):
        entradas.append({
            "id": f"R{r['artigo']:03d}", "tipo": "regimento",
            "chave": f"art. {r['artigo']} do Regimento Interno do TJAL",
            "fonte": "referencias/ritjal_integral.txt (" + VERSAO + ")",
            "trecho_literal": r.get("texto", ""), "observacao": "; ".join(r.get("avisos", [])) or r.get("erro", ""),
            "status": "PENDENTE" if "texto" in r else "REJECTED",
        })
    return entradas


def main(argv):
    if not argv:
        print(__doc__); return 2
    if argv[0] == "--buscar":
        print(json.dumps(buscar(" ".join(argv[1:])), ensure_ascii=False, indent=2)); return 0
    if argv[0] == "--fila":
        print(json.dumps(fila(argv[1]), ensure_ascii=False, indent=2)); return 0
    if argv[0] == "--revogados":
        print(REVOGADOS.read_text(encoding="utf-8") if REVOGADOS.exists() else "Arquivo de revogados ausente.")
        return 0
    r = consultar([a for a in argv if a.isdigit()])
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 1 if any("erro" in x for x in r) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
